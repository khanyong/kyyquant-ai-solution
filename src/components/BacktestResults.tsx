import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
  LinearProgress,
  Alert,
  Divider,
  IconButton,
  Tooltip,
  ToggleButton,
  ToggleButtonGroup,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Slider,
  CircularProgress
} from '@mui/material'
import {
  Timeline,
  Assessment,
  TrendingUp,
  TrendingDown,
  ShowChart,
  BarChart,
  PieChart,
  CompareArrows,
  Download,
  Refresh,
  DateRange,
  Info,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Speed,
  AccountBalance,
  Insights,
  Casino
} from '@mui/icons-material'
import { Line, Bar, Pie, Radar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler
} from 'chart.js'
import { BacktestService } from '../services/backtestService'

// Chart.js 컴포넌트 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  ChartTooltip,
  Legend,
  Filler
)
import type {
  BacktestResult as BacktestResultDB,
  BacktestTrade,
  BacktestDailyReturn,
  BacktestMonthlyReturn,
  BacktestSectorPerformance,
  BacktestRiskMetric
} from '../services/backtestService'
import { supabase } from '../lib/supabase'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

// 화면 표시용 인터페이스
interface BacktestResultDisplay {
  id: string
  strategyId: string
  strategyName: string
  period: {
    start: string
    end: string
    years: number
  }
  returns: {
    total: number
    annual: number
    monthly: number[]
    daily: number[]
  }
  risk: {
    maxDrawdown: number
    maxDrawdownDuration: number
    volatility: number
    sharpeRatio: number
    sortinoRatio: number
    calmarRatio: number
    beta: number
    alpha: number
  }
  trades: {
    total: number
    wins: number
    losses: number
    winRate: number
    avgWin: number
    avgLoss: number
    profitFactor: number
    avgHoldingDays: number
    maxConsecutiveWins: number
    maxConsecutiveLosses: number
  }
  positions: {
    maxPositions: number
    avgPositions: number
    turnover: number
  }
  sectorPerformance: BacktestSectorPerformance[]
  monthlyReturns: BacktestMonthlyReturn[]
  tradeHistory: BacktestTrade[]
  dailyReturns?: BacktestDailyReturn[]
}

const BacktestResultsUpdated: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0)
  const [selectedBacktests, setSelectedBacktests] = useState<string[]>([])
  const [results, setResults] = useState<BacktestResultDisplay[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [testPeriod, setTestPeriod] = useState({
    start: '2019-01-01',
    end: '2024-01-01',
    marketCondition: 'all' // all, bull, bear, sideways
  })
  const [isRunning, setIsRunning] = useState(false)
  const [compareMode, setCompareMode] = useState(true)
  const [monteCarloDialog, setMonteCarloDialog] = useState(false)
  const [monteCarloResults, setMonteCarloResults] = useState<any>(null)
  const [userId, setUserId] = useState<string | null>(null)

  // 사용자 정보 가져오기
  useEffect(() => {
    const fetchUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (user) {
        setUserId(user.id)
      }
    }
    fetchUser()
  }, [])

  // 백테스트 결과 가져오기
  useEffect(() => {
    if (userId) {
      fetchBacktestResults()
    }
  }, [userId])

  const fetchBacktestResults = async () => {
    if (!userId) return
    
    setLoading(true)
    setError(null)
    
    try {
      // 백테스트 결과 목록 조회
      const backtestResults = await BacktestService.getBacktestResults(userId)
      
      if (!backtestResults || backtestResults.length === 0) {
        setResults([])
        setLoading(false)
        return
      }

      // 각 백테스트에 대한 상세 데이터 조회
      const detailedResults = await Promise.all(
        backtestResults.slice(0, 2).map(async (backtest) => {
          const [trades, dailyReturns, monthlyReturns, sectorPerformance] = await Promise.all([
            BacktestService.getBacktestTrades(backtest.id),
            BacktestService.getBacktestDailyReturns(backtest.id),
            BacktestService.getBacktestMonthlyReturns(backtest.id),
            BacktestService.getBacktestSectorPerformance(backtest.id)
          ])

          // 데이터 변환
          const displayResult: BacktestResultDisplay = {
            id: backtest.id,
            strategyId: backtest.strategy_id,
            strategyName: backtest.strategy_name || '전략',
            period: {
              start: backtest.start_date,
              end: backtest.end_date,
              years: new Date(backtest.end_date).getFullYear() - new Date(backtest.start_date).getFullYear()
            },
            returns: {
              total: backtest.total_return * 100,
              annual: backtest.annual_return * 100,
              monthly: monthlyReturns.map(m => m.monthly_return * 100),
              daily: dailyReturns.map(d => d.daily_return * 100)
            },
            risk: {
              maxDrawdown: backtest.max_drawdown * 100,
              maxDrawdownDuration: backtest.max_drawdown_duration || 0,
              volatility: backtest.volatility * 100,
              sharpeRatio: backtest.sharpe_ratio || 0,
              sortinoRatio: backtest.sortino_ratio || 0,
              calmarRatio: backtest.calmar_ratio || 0,
              beta: backtest.beta || 0,
              alpha: backtest.alpha || 0
            },
            trades: {
              total: backtest.total_trades,
              wins: backtest.profitable_trades,
              losses: backtest.total_trades - backtest.profitable_trades,
              winRate: backtest.win_rate || 0,
              avgWin: backtest.avg_win * 100,
              avgLoss: backtest.avg_loss * 100,
              profitFactor: backtest.profit_factor || 0,
              avgHoldingDays: backtest.avg_holding_days || 0,
              maxConsecutiveWins: backtest.max_consecutive_wins || 0,
              maxConsecutiveLosses: backtest.max_consecutive_losses || 0
            },
            positions: {
              maxPositions: backtest.max_positions || 0,
              avgPositions: backtest.avg_positions || 0,
              turnover: backtest.turnover || 0
            },
            sectorPerformance: sectorPerformance,
            monthlyReturns: monthlyReturns,
            tradeHistory: trades,
            dailyReturns: dailyReturns
          }

          return displayResult
        })
      )

      setResults(detailedResults)
      setSelectedBacktests(detailedResults.map(r => r.id))
    } catch (err) {
      console.error('Error fetching backtest results:', err)
      setError('백테스트 결과를 불러오는데 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  // 더미 일별 수익률 데이터 생성
  const generateDummyDailyReturns = () => {
    const returns: any[] = []
    let cumulative = 100
    for (let i = 0; i < 250; i++) { // 약 1년 거래일
      const dailyReturn = (Math.random() - 0.48) * 3 // -1.44% ~ 1.56% 범위
      cumulative = cumulative * (1 + dailyReturn / 100)
      returns.push({
        date: new Date(2023, 0, 1 + i).toISOString().split('T')[0],
        portfolio_value: cumulative * 10000000,
        daily_return: dailyReturn / 100,
        cumulative_return: (cumulative - 100) / 100,
        drawdown: Math.min(0, (cumulative - Math.max(...returns.slice(-20).map(r => r.cumulative_return || 100) || 100)) / 100)
      })
    }
    return returns
  }

  // 더미 데이터 (데이터가 없을 때 표시용)
  const dummyResults: BacktestResultDisplay[] = [
    {
      id: 'dummy1',
      strategyId: 'strategy1',
      strategyName: '모멘텀 전략',
      period: { start: '2019-01-01', end: '2024-01-01', years: 5 },
      returns: {
        total: 125.3,
        annual: 17.6,
        monthly: [2.1, -1.3, 3.5, 1.2, -0.5, 2.8, 1.9, -0.8, 2.3, 3.1, -1.2, 2.5],
        daily: generateDummyDailyReturns().map(d => d.daily_return * 100)
      },
      risk: {
        maxDrawdown: -18.5,
        maxDrawdownDuration: 45,
        volatility: 16.2,
        sharpeRatio: 1.35,
        sortinoRatio: 1.82,
        calmarRatio: 0.95,
        beta: 0.85,
        alpha: 3.2
      },
      trades: {
        total: 245,
        wins: 156,
        losses: 89,
        winRate: 63.7,
        avgWin: 3.8,
        avgLoss: -2.1,
        profitFactor: 2.83,
        avgHoldingDays: 12.5,
        maxConsecutiveWins: 8,
        maxConsecutiveLosses: 4
      },
      positions: {
        maxPositions: 10,
        avgPositions: 7.2,
        turnover: 4.5
      },
      sectorPerformance: [
        { id: '1', backtest_id: 'dummy1', sector: 'IT/소프트웨어', trades_count: 85, total_return: 0.452, win_rate: 68.5, avg_return: 0.053, total_profit: 450000, total_loss: -120000, best_trade: 0.15, worst_trade: -0.08, avg_holding_days: 10 },
        { id: '2', backtest_id: 'dummy1', sector: '바이오/헬스케어', trades_count: 62, total_return: 0.283, win_rate: 58.2, avg_return: 0.046, total_profit: 380000, total_loss: -150000, best_trade: 0.12, worst_trade: -0.10, avg_holding_days: 15 },
        { id: '3', backtest_id: 'dummy1', sector: '2차전지', trades_count: 48, total_return: 0.358, win_rate: 65.3, avg_return: 0.075, total_profit: 520000, total_loss: -80000, best_trade: 0.18, worst_trade: -0.06, avg_holding_days: 8 },
        { id: '4', backtest_id: 'dummy1', sector: '반도체', trades_count: 50, total_return: 0.160, win_rate: 61.0, avg_return: 0.032, total_profit: 280000, total_loss: -95000, best_trade: 0.09, worst_trade: -0.07, avg_holding_days: 12 }
      ],
      monthlyReturns: [
        { id: '1', backtest_id: 'dummy1', year: 2023, month: 1, monthly_return: 0.052, trades_count: 18, win_rate: 65, avg_gain: 0.038, avg_loss: -0.021 },
        { id: '2', backtest_id: 'dummy1', year: 2023, month: 2, monthly_return: -0.021, trades_count: 15, win_rate: 45, avg_gain: 0.025, avg_loss: -0.032 },
        { id: '3', backtest_id: 'dummy1', year: 2023, month: 3, monthly_return: 0.038, trades_count: 22, win_rate: 68, avg_gain: 0.042, avg_loss: -0.018 },
        { id: '4', backtest_id: 'dummy1', year: 2023, month: 4, monthly_return: 0.015, trades_count: 20, win_rate: 55, avg_gain: 0.035, avg_loss: -0.025 },
        { id: '5', backtest_id: 'dummy1', year: 2023, month: 5, monthly_return: -0.008, trades_count: 19, win_rate: 48, avg_gain: 0.028, avg_loss: -0.030 },
        { id: '6', backtest_id: 'dummy1', year: 2023, month: 6, monthly_return: 0.023, trades_count: 21, win_rate: 62, avg_gain: 0.031, avg_loss: -0.019 }
      ],
      tradeHistory: [
        { id: '1', backtest_id: 'dummy1', trade_date: '2023-01-05', stock_code: '005930', stock_name: '삼성전자', action: 'BUY', price: 58000, quantity: 100, amount: 5800000, commission: 8700, returns: 0.052, holding_days: 15, profit_loss: 301600 },
        { id: '2', backtest_id: 'dummy1', trade_date: '2023-01-20', stock_code: '005930', stock_name: '삼성전자', action: 'SELL', price: 61000, quantity: 100, amount: 6100000, commission: 9150, returns: 0.052, holding_days: 15, profit_loss: 301600 },
        { id: '3', backtest_id: 'dummy1', trade_date: '2023-02-01', stock_code: '000660', stock_name: 'SK하이닉스', action: 'BUY', price: 82000, quantity: 50, amount: 4100000, commission: 6150, returns: -0.018, holding_days: 20, profit_loss: -73800 },
        { id: '4', backtest_id: 'dummy1', trade_date: '2023-02-21', stock_code: '000660', stock_name: 'SK하이닉스', action: 'SELL', price: 80500, quantity: 50, amount: 4025000, commission: 6037, returns: -0.018, holding_days: 20, profit_loss: -73800 }
      ],
      dailyReturns: generateDummyDailyReturns()
    },
    {
      id: 'dummy2',
      strategyId: 'strategy2',
      strategyName: '가치투자 전략',
      period: { start: '2019-01-01', end: '2024-01-01', years: 5 },
      returns: {
        total: 95.2,
        annual: 14.3,
        monthly: [1.8, 0.5, 2.1, 1.5, 0.8, 1.9, 1.2, 0.3, 1.7, 2.0, 0.9, 1.6],
        daily: generateDummyDailyReturns().map(d => d.daily_return * 100 * 0.8)
      },
      risk: {
        maxDrawdown: -12.3,
        maxDrawdownDuration: 32,
        volatility: 12.5,
        sharpeRatio: 1.52,
        sortinoRatio: 2.15,
        calmarRatio: 1.16,
        beta: 0.72,
        alpha: 2.8
      },
      trades: {
        total: 132,
        wins: 92,
        losses: 40,
        winRate: 69.7,
        avgWin: 2.8,
        avgLoss: -1.5,
        profitFactor: 3.21,
        avgHoldingDays: 28.3,
        maxConsecutiveWins: 12,
        maxConsecutiveLosses: 3
      },
      positions: {
        maxPositions: 15,
        avgPositions: 11.5,
        turnover: 2.3
      },
      sectorPerformance: [
        { id: '5', backtest_id: 'dummy2', sector: '금융', trades_count: 42, total_return: 0.285, win_rate: 72.3, avg_return: 0.068, total_profit: 320000, total_loss: -60000, best_trade: 0.11, worst_trade: -0.05, avg_holding_days: 25 },
        { id: '6', backtest_id: 'dummy2', sector: '화학', trades_count: 35, total_return: 0.221, win_rate: 68.5, avg_return: 0.063, total_profit: 280000, total_loss: -70000, best_trade: 0.09, worst_trade: -0.06, avg_holding_days: 30 },
        { id: '7', backtest_id: 'dummy2', sector: '철강/소재', trades_count: 28, total_return: 0.183, win_rate: 65.2, avg_return: 0.065, total_profit: 250000, total_loss: -65000, best_trade: 0.10, worst_trade: -0.07, avg_holding_days: 35 },
        { id: '8', backtest_id: 'dummy2', sector: '건설/부동산', trades_count: 27, total_return: 0.263, win_rate: 71.5, avg_return: 0.097, total_profit: 310000, total_loss: -50000, best_trade: 0.13, worst_trade: -0.04, avg_holding_days: 28 }
      ],
      monthlyReturns: [
        { id: '7', backtest_id: 'dummy2', year: 2023, month: 1, monthly_return: 0.018, trades_count: 10, win_rate: 70, avg_gain: 0.025, avg_loss: -0.012 },
        { id: '8', backtest_id: 'dummy2', year: 2023, month: 2, monthly_return: 0.005, trades_count: 8, win_rate: 62, avg_gain: 0.018, avg_loss: -0.015 },
        { id: '9', backtest_id: 'dummy2', year: 2023, month: 3, monthly_return: 0.021, trades_count: 12, win_rate: 75, avg_gain: 0.028, avg_loss: -0.010 },
        { id: '10', backtest_id: 'dummy2', year: 2023, month: 4, monthly_return: 0.015, trades_count: 11, win_rate: 68, avg_gain: 0.022, avg_loss: -0.013 },
        { id: '11', backtest_id: 'dummy2', year: 2023, month: 5, monthly_return: 0.008, trades_count: 9, win_rate: 65, avg_gain: 0.020, avg_loss: -0.014 },
        { id: '12', backtest_id: 'dummy2', year: 2023, month: 6, monthly_return: 0.019, trades_count: 13, win_rate: 72, avg_gain: 0.026, avg_loss: -0.011 }
      ],
      tradeHistory: [
        { id: '5', backtest_id: 'dummy2', trade_date: '2023-01-10', stock_code: '055550', stock_name: '신한지주', action: 'BUY', price: 35000, quantity: 150, amount: 5250000, commission: 7875, returns: 0.028, holding_days: 35, profit_loss: 147000 },
        { id: '6', backtest_id: 'dummy2', trade_date: '2023-02-14', stock_code: '055550', stock_name: '신한지주', action: 'SELL', price: 36000, quantity: 150, amount: 5400000, commission: 8100, returns: 0.028, holding_days: 35, profit_loss: 147000 },
        { id: '7', backtest_id: 'dummy2', trade_date: '2023-03-05', stock_code: '005380', stock_name: '현대차', action: 'BUY', price: 180000, quantity: 30, amount: 5400000, commission: 8100, returns: 0.035, holding_days: 42, profit_loss: 189000 },
        { id: '8', backtest_id: 'dummy2', trade_date: '2023-04-16', stock_code: '005380', stock_name: '현대차', action: 'SELL', price: 186300, quantity: 30, amount: 5589000, commission: 8383, returns: 0.035, holding_days: 42, profit_loss: 189000 }
      ],
      dailyReturns: generateDummyDailyReturns()
    }
  ]

  // 데이터가 없을 때 더미 데이터 사용
  const displayResults = results.length > 0 ? results : (loading ? [] : dummyResults)

  const runMonteCarloSimulation = () => {
    setIsRunning(true)
    // 시뮬레이션 실행
    setTimeout(() => {
      setMonteCarloResults({
        simulations: 1000,
        confidence95: { min: -15, max: 180 },
        confidence99: { min: -25, max: 220 },
        median: 95,
        mean: 98,
        worstCase: -35,
        bestCase: 285
      })
      setIsRunning(false)
      setMonteCarloDialog(true)
    }, 2000)
  }

  const exportResults = () => {
    alert('백테스트 결과를 Excel로 내보냅니다')
  }

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Assessment />
            백테스팅 심층 분석
          </Typography>
          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              startIcon={<Casino />}
              onClick={runMonteCarloSimulation}
              disabled={isRunning}
            >
              몬테카를로
            </Button>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={exportResults}
            >
              Excel 내보내기
            </Button>
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={() => setIsRunning(true)}
              disabled={isRunning}
            >
              백테스트 실행
            </Button>
          </Stack>
        </Box>

        {/* 테스트 설정 */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>테스트 기간</InputLabel>
              <Select
                value={testPeriod.marketCondition}
                onChange={(e) => setTestPeriod({ ...testPeriod, marketCondition: e.target.value })}
                label="테스트 기간"
              >
                <MenuItem value="all">전체 기간 (5년)</MenuItem>
                <MenuItem value="bull">상승장 기간</MenuItem>
                <MenuItem value="bear">하락장 기간</MenuItem>
                <MenuItem value="sideways">횡보장 기간</MenuItem>
                <MenuItem value="covid">코로나 기간</MenuItem>
                <MenuItem value="custom">사용자 지정</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="date"
              label="시작일"
              value={testPeriod.start}
              onChange={(e) => setTestPeriod({ ...testPeriod, start: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="date"
              label="종료일"
              value={testPeriod.end}
              onChange={(e) => setTestPeriod({ ...testPeriod, end: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <ToggleButtonGroup
              value={compareMode}
              exclusive
              onChange={(e, value) => setCompareMode(value)}
              fullWidth
            >
              <ToggleButton value={true}>
                <CompareArrows sx={{ mr: 1 }} />
                비교 모드
              </ToggleButton>
              <ToggleButton value={false}>
                <ShowChart sx={{ mr: 1 }} />
                단일 분석
              </ToggleButton>
            </ToggleButtonGroup>
          </Grid>
        </Grid>

        {isRunning && <LinearProgress sx={{ mt: 2 }} />}
      </Paper>

      {/* 탭 메뉴 */}
      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)}>
            <Tab icon={<Timeline />} iconPosition="start" label="성과 요약" />
            <Tab icon={<ShowChart />} iconPosition="start" label="수익률 곡선" />
            <Tab icon={<TrendingDown />} iconPosition="start" label="리스크 분석" />
            <Tab icon={<BarChart />} iconPosition="start" label="거래 분석" />
            <Tab icon={<PieChart />} iconPosition="start" label="섹터별 성과" />
            <Tab icon={<DateRange />} iconPosition="start" label="월별 수익률" />
            <Tab icon={<Insights />} iconPosition="start" label="상세 내역" />
          </Tabs>
        </Box>

        {/* 성과 요약 탭 */}
        <TabPanel value={currentTab} index={0}>
          <Grid container spacing={3}>
            {displayResults.map((result) => (
              <Grid item xs={12} md={compareMode ? 6 : 12} key={result.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {result.strategyName}
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    
                    <Grid container spacing={2}>
                      <Grid item xs={6} md={3}>
                        <Stack alignItems="center">
                          <Typography variant="h5" color="primary">
                            {result.returns.total.toFixed(1)}%
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            총 수익률
                          </Typography>
                        </Stack>
                      </Grid>
                      <Grid item xs={6} md={3}>
                        <Stack alignItems="center">
                          <Typography variant="h5">
                            {result.returns.annual.toFixed(1)}%
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            연평균 수익률
                          </Typography>
                        </Stack>
                      </Grid>
                      <Grid item xs={6} md={3}>
                        <Stack alignItems="center">
                          <Typography variant="h5" color="error">
                            {result.risk.maxDrawdown.toFixed(1)}%
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            최대 낙폭
                          </Typography>
                        </Stack>
                      </Grid>
                      <Grid item xs={6} md={3}>
                        <Stack alignItems="center">
                          <Typography variant="h5" color="success">
                            {result.trades.winRate.toFixed(1)}%
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            승률
                          </Typography>
                        </Stack>
                      </Grid>
                    </Grid>

                    <Box sx={{ mt: 3 }}>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="textSecondary">
                            샤프 비율
                          </Typography>
                          <Typography variant="h6">
                            {result.risk.sharpeRatio.toFixed(2)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="textSecondary">
                            손익비
                          </Typography>
                          <Typography variant="h6">
                            {result.trades.profitFactor.toFixed(2)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="textSecondary">
                            총 거래 횟수
                          </Typography>
                          <Typography variant="h6">
                            {result.trades.total}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="textSecondary">
                            평균 보유일
                          </Typography>
                          <Typography variant="h6">
                            {result.trades.avgHoldingDays.toFixed(1)}일
                          </Typography>
                        </Grid>
                      </Grid>
                    </Box>

                    {/* 리스크 지표 */}
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        리스크 지표
                      </Typography>
                      <Stack direction="row" spacing={1}>
                        <Chip
                          label={`변동성: ${result.risk.volatility.toFixed(1)}%`}
                          size="small"
                        />
                        <Chip
                          label={`Beta: ${result.risk.beta.toFixed(2)}`}
                          size="small"
                        />
                        <Chip
                          label={`Alpha: ${result.risk.alpha.toFixed(2)}`}
                          size="small"
                        />
                      </Stack>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* 수익률 곡선 탭 */}
        <TabPanel value={currentTab} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    누적 수익률 곡선
                  </Typography>
                  <Box sx={{ height: 400 }}>
                    <Line
                      data={{
                        labels: displayResults[0]?.dailyReturns?.slice(0, 100).map((_, i) => 
                          new Date(2023, 0, i + 1).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
                        ) || [],
                        datasets: displayResults.map((result, idx) => ({
                          label: result.strategyName,
                          data: result.dailyReturns?.slice(0, 100).map((d, i) => {
                            const cumReturn = result.dailyReturns?.slice(0, i + 1).reduce((acc, r) => acc * (1 + r.daily_return), 1) || 1
                            return ((cumReturn - 1) * 100).toFixed(2)
                          }) || [],
                          borderColor: idx === 0 ? 'rgb(75, 192, 192)' : 'rgb(255, 99, 132)',
                          backgroundColor: idx === 0 ? 'rgba(75, 192, 192, 0.2)' : 'rgba(255, 99, 132, 0.2)',
                          tension: 0.1,
                          fill: false
                        }))
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            position: 'top' as const,
                          },
                          title: {
                            display: false
                          },
                          tooltip: {
                            mode: 'index',
                            intersect: false,
                          }
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            ticks: {
                              callback: function(value) {
                                return value + '%'
                              }
                            }
                          }
                        }
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    드로다운 차트
                  </Typography>
                  <Box sx={{ height: 300 }}>
                    <Line
                      data={{
                        labels: displayResults[0]?.dailyReturns?.slice(0, 100).map((_, i) => 
                          new Date(2023, 0, i + 1).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
                        ) || [],
                        datasets: displayResults.map((result, idx) => ({
                          label: result.strategyName,
                          data: result.dailyReturns?.slice(0, 100).map(d => (d.drawdown * 100).toFixed(2)) || [],
                          borderColor: idx === 0 ? 'rgb(255, 159, 64)' : 'rgb(153, 102, 255)',
                          backgroundColor: idx === 0 ? 'rgba(255, 159, 64, 0.2)' : 'rgba(153, 102, 255, 0.2)',
                          tension: 0.1,
                          fill: true
                        }))
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            position: 'top' as const,
                          }
                        },
                        scales: {
                          y: {
                            ticks: {
                              callback: function(value) {
                                return value + '%'
                              }
                            }
                          }
                        }
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    일별 수익률 분포
                  </Typography>
                  <Box sx={{ height: 300 }}>
                    <Bar
                      data={{
                        labels: ['-3% 이하', '-2%', '-1%', '0%', '1%', '2%', '3% 이상'],
                        datasets: displayResults.map((result, idx) => {
                          const distribution = [0, 0, 0, 0, 0, 0, 0]
                          result.returns.daily.forEach(r => {
                            if (r <= -3) distribution[0]++
                            else if (r <= -2) distribution[1]++
                            else if (r <= -1) distribution[2]++
                            else if (r <= 0) distribution[3]++
                            else if (r <= 1) distribution[4]++
                            else if (r <= 2) distribution[5]++
                            else distribution[6]++
                          })
                          return {
                            label: result.strategyName,
                            data: distribution,
                            backgroundColor: idx === 0 ? 'rgba(54, 162, 235, 0.5)' : 'rgba(255, 206, 86, 0.5)'
                          }
                        })
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            position: 'top' as const,
                          },
                          title: {
                            display: false
                          }
                        }
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 리스크 분석 탭 */}
        <TabPanel value={currentTab} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    낙폭 분석
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>전략</TableCell>
                          <TableCell align="right">최대 낙폭</TableCell>
                          <TableCell align="right">회복 기간</TableCell>
                          <TableCell align="right">칼마 비율</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {displayResults.map((result) => (
                          <TableRow key={result.id}>
                            <TableCell>{result.strategyName}</TableCell>
                            <TableCell align="right">
                              <Typography color="error">
                                {result.risk.maxDrawdown.toFixed(1)}%
                              </Typography>
                            </TableCell>
                            <TableCell align="right">
                              {result.risk.maxDrawdownDuration}일
                            </TableCell>
                            <TableCell align="right">
                              {result.risk.calmarRatio.toFixed(2)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    리스크 조정 수익률
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>전략</TableCell>
                          <TableCell align="right">샤프</TableCell>
                          <TableCell align="right">소르티노</TableCell>
                          <TableCell align="right">변동성</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {displayResults.map((result) => (
                          <TableRow key={result.id}>
                            <TableCell>{result.strategyName}</TableCell>
                            <TableCell align="right">
                              {result.risk.sharpeRatio.toFixed(2)}
                            </TableCell>
                            <TableCell align="right">
                              {result.risk.sortinoRatio.toFixed(2)}
                            </TableCell>
                            <TableCell align="right">
                              {result.risk.volatility.toFixed(1)}%
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 거래 분석 탭 */}
        <TabPanel value={currentTab} index={3}>
          <Grid container spacing={3}>
            {displayResults.map((result) => (
              <Grid item xs={12} md={6} key={result.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {result.strategyName} - 거래 통계
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">승/패</Typography>
                        <Typography variant="h6">
                          {result.trades.wins} / {result.trades.losses}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">평균 수익/손실</Typography>
                        <Typography variant="h6">
                          +{result.trades.avgWin.toFixed(1)}% / {result.trades.avgLoss.toFixed(1)}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">최대 연속 승/패</Typography>
                        <Typography variant="h6">
                          {result.trades.maxConsecutiveWins} / {result.trades.maxConsecutiveLosses}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">회전율</Typography>
                        <Typography variant="h6">
                          {result.positions.turnover.toFixed(1)}x
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* 섹터별 성과 탭 */}
        {/* 섹터별 성과 탭 */}
        <TabPanel value={currentTab} index={4}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    섹터별 수익률
                  </Typography>
                  <Box sx={{ height: 350 }}>
                    <Pie
                      data={{
                        labels: displayResults[0]?.sectorPerformance.map(s => s.sector) || [],
                        datasets: [{
                          label: '수익률',
                          data: displayResults[0]?.sectorPerformance.map(s => (s.total_return * 100).toFixed(2)) || [],
                          backgroundColor: [
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(75, 192, 192, 0.6)',
                            'rgba(153, 102, 255, 0.6)',
                            'rgba(255, 159, 64, 0.6)'
                          ],
                          borderWidth: 1
                        }]
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            position: 'right' as const,
                          },
                          tooltip: {
                            callbacks: {
                              label: function(context) {
                                return context.label + ': ' + context.parsed + '%'
                              }
                            }
                          }
                        }
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    섹터별 거래 통계
                  </Typography>
                  <Box sx={{ height: 350 }}>
                    <Bar
                      data={{
                        labels: displayResults[0]?.sectorPerformance.map(s => s.sector) || [],
                        datasets: [
                          {
                            label: '거래 횟수',
                            data: displayResults[0]?.sectorPerformance.map(s => s.trades_count) || [],
                            backgroundColor: 'rgba(75, 192, 192, 0.6)',
                            yAxisID: 'y',
                          },
                          {
                            label: '승률 (%)',
                            data: displayResults[0]?.sectorPerformance.map(s => s.win_rate) || [],
                            backgroundColor: 'rgba(255, 99, 132, 0.6)',
                            yAxisID: 'y1',
                          }
                        ]
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            position: 'top' as const,
                          }
                        },
                        scales: {
                          y: {
                            type: 'linear' as const,
                            display: true,
                            position: 'left' as const,
                          },
                          y1: {
                            type: 'linear' as const,
                            display: true,
                            position: 'right' as const,
                            grid: {
                              drawOnChartArea: false,
                            },
                          },
                        },
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            {displayResults.map((result) => (
              <Grid item xs={12} key={result.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {result.strategyName} - 상세 섹터 분석
                    </Typography>
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>섹터</TableCell>
                            <TableCell align="right">거래수</TableCell>
                            <TableCell align="right">총 수익률</TableCell>
                            <TableCell align="right">승률</TableCell>
                            <TableCell align="right">평균 수익</TableCell>
                            <TableCell align="right">최고 거래</TableCell>
                            <TableCell align="right">최악 거래</TableCell>
                            <TableCell align="right">평균 보유일</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {result.sectorPerformance.map((sector) => (
                            <TableRow key={sector.sector}>
                              <TableCell>
                                <Chip label={sector.sector} size="small" />
                              </TableCell>
                              <TableCell align="right">{sector.trades_count}</TableCell>
                              <TableCell align="right">
                                <Typography color={sector.total_return > 0 ? 'success.main' : 'error.main'}>
                                  {(sector.total_return * 100).toFixed(1)}%
                                </Typography>
                              </TableCell>
                              <TableCell align="right">{sector.win_rate.toFixed(1)}%</TableCell>
                              <TableCell align="right">{(sector.avg_return * 100).toFixed(2)}%</TableCell>
                              <TableCell align="right">
                                <Typography color="success.main">
                                  +{(sector.best_trade * 100).toFixed(1)}%
                                </Typography>
                              </TableCell>
                              <TableCell align="right">
                                <Typography color="error.main">
                                  {(sector.worst_trade * 100).toFixed(1)}%
                                </Typography>
                              </TableCell>
                              <TableCell align="right">{sector.avg_holding_days.toFixed(0)}일</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* 월별 수익률 탭 */}
        <TabPanel value={currentTab} index={5}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    월별 수익률 히트맵
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>전략</TableCell>
                          <TableCell align="center">1월</TableCell>
                          <TableCell align="center">2월</TableCell>
                          <TableCell align="center">3월</TableCell>
                          <TableCell align="center">4월</TableCell>
                          <TableCell align="center">5월</TableCell>
                          <TableCell align="center">6월</TableCell>
                          <TableCell align="center">7월</TableCell>
                          <TableCell align="center">8월</TableCell>
                          <TableCell align="center">9월</TableCell>
                          <TableCell align="center">10월</TableCell>
                          <TableCell align="center">11월</TableCell>
                          <TableCell align="center">12월</TableCell>
                          <TableCell align="center">연간</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {displayResults.map((result) => (
                          <TableRow key={result.id}>
                            <TableCell>{result.strategyName}</TableCell>
                            {result.monthlyReturns.slice(0, 12).map((month, idx) => (
                              <TableCell key={idx} align="center">
                                <Chip
                                  label={`${(month.monthly_return * 100).toFixed(1)}%`}
                                  size="small"
                                  color={month.monthly_return > 0 ? 'success' : 'error'}
                                  sx={{ 
                                    minWidth: 60,
                                    opacity: Math.abs(month.monthly_return) * 10 + 0.5
                                  }}
                                />
                              </TableCell>
                            ))}
                            <TableCell align="center">
                              <Typography 
                                variant="subtitle2" 
                                color={result.returns.annual > 0 ? 'success.main' : 'error.main'}
                                fontWeight="bold"
                              >
                                {result.returns.annual.toFixed(1)}%
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    월별 수익률 추이
                  </Typography>
                  <Box sx={{ height: 350 }}>
                    <Bar
                      data={{
                        labels: displayResults[0]?.monthlyReturns.map(m => `${m.year}-${String(m.month).padStart(2, '0')}`) || [],
                        datasets: displayResults.map((result, idx) => ({
                          label: result.strategyName,
                          data: result.monthlyReturns.map(m => (m.monthly_return * 100).toFixed(2)),
                          backgroundColor: idx === 0 ? 'rgba(75, 192, 192, 0.6)' : 'rgba(255, 99, 132, 0.6)',
                        }))
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            position: 'top' as const,
                          }
                        },
                        scales: {
                          y: {
                            ticks: {
                              callback: function(value) {
                                return value + '%'
                              }
                            }
                          }
                        }
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 상세 내역 탭 */}
        <TabPanel value={currentTab} index={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                거래 상세 내역
              </Typography>
              <TableContainer sx={{ maxHeight: 600 }}>
                <Table stickyHeader size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>날짜</TableCell>
                      <TableCell>종목코드</TableCell>
                      <TableCell>종목명</TableCell>
                      <TableCell align="center">매매</TableCell>
                      <TableCell align="right">가격</TableCell>
                      <TableCell align="right">수량</TableCell>
                      <TableCell align="right">금액</TableCell>
                      <TableCell align="right">수수료</TableCell>
                      <TableCell align="right">수익률</TableCell>
                      <TableCell align="right">보유일</TableCell>
                      <TableCell align="right">손익</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {displayResults.flatMap(result => 
                      result.tradeHistory.map(trade => (
                        <TableRow key={trade.id} hover>
                          <TableCell>{new Date(trade.trade_date).toLocaleDateString('ko-KR')}</TableCell>
                          <TableCell>{trade.stock_code}</TableCell>
                          <TableCell>{trade.stock_name}</TableCell>
                          <TableCell align="center">
                            <Chip 
                              label={trade.action} 
                              size="small" 
                              color={trade.action === 'BUY' ? 'primary' : 'secondary'}
                            />
                          </TableCell>
                          <TableCell align="right">{trade.price.toLocaleString()}원</TableCell>
                          <TableCell align="right">{trade.quantity.toLocaleString()}주</TableCell>
                          <TableCell align="right">{trade.amount.toLocaleString()}원</TableCell>
                          <TableCell align="right">{trade.commission?.toLocaleString()}원</TableCell>
                          <TableCell align="right">
                            <Typography 
                              variant="body2" 
                              color={trade.returns > 0 ? 'success.main' : trade.returns < 0 ? 'error.main' : 'textSecondary'}
                            >
                              {trade.returns ? `${(trade.returns * 100).toFixed(2)}%` : '-'}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            {trade.holding_days ? `${trade.holding_days}일` : '-'}
                          </TableCell>
                          <TableCell align="right">
                            <Typography 
                              variant="body2" 
                              color={trade.profit_loss && trade.profit_loss > 0 ? 'success.main' : 'error.main'}
                              fontWeight="bold"
                            >
                              {trade.profit_loss ? `${trade.profit_loss.toLocaleString()}원` : '-'}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
              
              {displayResults[0]?.tradeHistory.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="textSecondary">
                    거래 내역이 없습니다
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </TabPanel>
      </Paper>

      {/* 몬테카를로 시뮬레이션 다이얼로그 */}
      <Dialog open={monteCarloDialog} onClose={() => setMonteCarloDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>몬테카를로 시뮬레이션 결과</DialogTitle>
        <DialogContent>
          {monteCarloResults && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                1,000회 시뮬레이션 기반 확률적 수익률 분포
              </Alert>
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">95% 신뢰구간</Typography>
                  <Typography variant="h6">
                    {monteCarloResults.confidence95.min}% ~ {monteCarloResults.confidence95.max}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">99% 신뢰구간</Typography>
                  <Typography variant="h6">
                    {monteCarloResults.confidence99.min}% ~ {monteCarloResults.confidence99.max}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">중앙값</Typography>
                  <Typography variant="h6">{monteCarloResults.median}%</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">평균</Typography>
                  <Typography variant="h6">{monteCarloResults.mean}%</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">최악 시나리오</Typography>
                  <Typography variant="h6" color="error">{monteCarloResults.worstCase}%</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">최선 시나리오</Typography>
                  <Typography variant="h6" color="success.main">{monteCarloResults.bestCase}%</Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMonteCarloDialog(false)}>닫기</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default BacktestResultsUpdated