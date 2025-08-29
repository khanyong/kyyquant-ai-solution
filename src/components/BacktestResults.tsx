import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Stack,
  Chip,
  LinearProgress,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  ShowChart,
  AttachMoney,
  Timeline,
  PlayArrow,
  DateRange
} from '@mui/icons-material'
import { TextField } from '@mui/material'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface BacktestResult {
  strategyName: string
  period: string
  totalReturn: number
  sharpeRatio: number
  maxDrawdown: number
  winRate: number
  totalTrades: number
  profitFactor: number
  avgWin: number
  avgLoss: number
}

const BacktestResults: React.FC = () => {
  const [selectedStrategy, setSelectedStrategy] = useState('momentum')
  const [period, setPeriod] = useState('1Y')
  const [customPeriod, setCustomPeriod] = useState({
    start: new Date(new Date().setFullYear(new Date().getFullYear() - 1)).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })
  const [isRunning, setIsRunning] = useState(false)

  // Mock 백테스트 결과
  const mockResult: BacktestResult = {
    strategyName: 'RSI + MACD 전략',
    period: '2023.01 - 2024.01',
    totalReturn: 23.5,
    sharpeRatio: 1.85,
    maxDrawdown: -8.3,
    winRate: 62.5,
    totalTrades: 156,
    profitFactor: 1.92,
    avgWin: 2.8,
    avgLoss: -1.5
  }

  // Mock 수익률 곡선 데이터
  const equityCurveData = {
    labels: Array.from({length: 252}, (_, i) => `Day ${i+1}`),
    datasets: [
      {
        label: '전략 수익률',
        data: Array.from({length: 252}, (_, i) => 
          10000 * (1 + (Math.random() - 0.45) * 0.02) ** i
        ),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        fill: true,
        tension: 0.1
      },
      {
        label: '벤치마크 (KOSPI)',
        data: Array.from({length: 252}, (_, i) => 
          10000 * (1 + (Math.random() - 0.48) * 0.015) ** i
        ),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        fill: true,
        tension: 0.1
      }
    ]
  }

  const drawdownData = {
    labels: Array.from({length: 252}, (_, i) => `Day ${i+1}`),
    datasets: [
      {
        label: 'Drawdown (%)',
        data: Array.from({length: 252}, () => 
          -Math.random() * 10
        ),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        fill: true
      }
    ]
  }

  const trades = [
    { date: '2024-01-15', type: 'BUY', stock: '삼성전자', price: 71000, quantity: 10, pnl: null },
    { date: '2024-01-18', type: 'SELL', stock: '삼성전자', price: 72500, quantity: 10, pnl: 15000 },
    { date: '2024-01-20', type: 'BUY', stock: 'SK하이닉스', price: 128000, quantity: 5, pnl: null },
    { date: '2024-01-22', type: 'SELL', stock: 'SK하이닉스', price: 126500, quantity: 5, pnl: -7500 },
    { date: '2024-01-25', type: 'BUY', stock: 'NAVER', price: 215000, quantity: 3, pnl: null },
  ]

  const runBacktest = () => {
    setIsRunning(true)
    setTimeout(() => {
      setIsRunning(false)
    }, 3000)
  }

  const MetricCard = ({ title, value, unit, color, icon }: any) => (
    <Card>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="text.secondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h5" component="div" color={color}>
              {value}{unit}
            </Typography>
          </Box>
          <Box sx={{ color: color || 'text.secondary' }}>
            {icon}
          </Box>
        </Stack>
      </CardContent>
    </Card>
  )

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h5">
            <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
            백테스팅 결과
          </Typography>
          {period === '10Y' && (
            <Chip 
              icon={<DateRange />} 
              label="10년 장기 백테스트" 
              size="small" 
              color="primary" 
              sx={{ mt: 1 }}
            />
          )}
          {period === 'CUSTOM' && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
              사용자 지정 기간: {customPeriod.start} ~ {customPeriod.end}
            </Typography>
          )}
        </Box>
        
        <Stack direction="row" spacing={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>전략 선택</InputLabel>
            <Select
              value={selectedStrategy}
              onChange={(e) => setSelectedStrategy(e.target.value)}
              label="전략 선택"
            >
              <MenuItem value="momentum">모멘텀 전략</MenuItem>
              <MenuItem value="mean_reversion">평균회귀 전략</MenuItem>
              <MenuItem value="rsi_macd">RSI + MACD</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 100 }}>
            <InputLabel>기간</InputLabel>
            <Select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              label="기간"
            >
              <MenuItem value="1M">1개월</MenuItem>
              <MenuItem value="3M">3개월</MenuItem>
              <MenuItem value="6M">6개월</MenuItem>
              <MenuItem value="1Y">1년</MenuItem>
              <MenuItem value="3Y">3년</MenuItem>
            </Select>
          </FormControl>
          
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={runBacktest}
            disabled={isRunning}
          >
            백테스트 실행
          </Button>
        </Stack>
      </Stack>

      {isRunning && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" gutterBottom>백테스트 실행 중...</Typography>
          <LinearProgress />
        </Box>
      )}

      {/* 핵심 지표 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="총 수익률"
            value={`+${mockResult.totalReturn}`}
            unit="%"
            color="success.main"
            icon={<TrendingUp />}
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="샤프 비율"
            value={mockResult.sharpeRatio.toFixed(2)}
            unit=""
            color="primary.main"
            icon={<ShowChart />}
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="최대 낙폭"
            value={mockResult.maxDrawdown.toFixed(1)}
            unit="%"
            color="error.main"
            icon={<TrendingDown />}
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="승률"
            value={mockResult.winRate.toFixed(1)}
            unit="%"
            color="info.main"
            icon={<AttachMoney />}
          />
        </Grid>
      </Grid>

      {/* 차트 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>수익률 곡선</Typography>
            <Line 
              data={equityCurveData} 
              options={{
                responsive: true,
                plugins: {
                  legend: { position: 'top' as const },
                  title: { display: false }
                },
                scales: {
                  y: {
                    beginAtZero: false,
                    title: { display: true, text: '자산 (원)' }
                  }
                }
              }}
            />
          </Paper>
        </Grid>
        
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>상세 통계</Typography>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell>총 거래 횟수</TableCell>
                  <TableCell align="right">{mockResult.totalTrades}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Profit Factor</TableCell>
                  <TableCell align="right">{mockResult.profitFactor.toFixed(2)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>평균 수익</TableCell>
                  <TableCell align="right">+{mockResult.avgWin}%</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>평균 손실</TableCell>
                  <TableCell align="right">{mockResult.avgLoss}%</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>최대 연속 수익</TableCell>
                  <TableCell align="right">7회</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>최대 연속 손실</TableCell>
                  <TableCell align="right">3회</TableCell>
                </TableRow>
                {period === '10Y' && (
                  <>
                    <TableRow>
                      <TableCell>연평균 수익률 (CAGR)</TableCell>
                      <TableCell align="right">14.2%</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>월평균 거래</TableCell>
                      <TableCell align="right">{Math.floor(mockResult.totalTrades / 120)}회</TableCell>
                    </TableRow>
                  </>
                )}
                {(period === '5Y' || period === '10Y') && (
                  <TableRow>
                    <TableCell>시장 대비 초과수익</TableCell>
                    <TableCell align="right">+{period === '10Y' ? '82.5' : '45.3'}%</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </Paper>
        </Grid>
      </Grid>

      {/* Drawdown 차트 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Drawdown</Typography>
        <Line 
          data={drawdownData} 
          options={{
            responsive: true,
            plugins: {
              legend: { display: false },
              title: { display: false }
            },
            scales: {
              y: {
                max: 0,
                title: { display: true, text: 'Drawdown (%)' }
              }
            }
          }}
        />
      </Paper>

      {/* 거래 내역 */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>최근 거래 내역</Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>날짜</TableCell>
                <TableCell>유형</TableCell>
                <TableCell>종목</TableCell>
                <TableCell align="right">가격</TableCell>
                <TableCell align="right">수량</TableCell>
                <TableCell align="right">손익</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {trades.map((trade, index) => (
                <TableRow key={index}>
                  <TableCell>{trade.date}</TableCell>
                  <TableCell>
                    <Chip 
                      label={trade.type} 
                      size="small"
                      color={trade.type === 'BUY' ? 'error' : 'primary'}
                    />
                  </TableCell>
                  <TableCell>{trade.stock}</TableCell>
                  <TableCell align="right">{trade.price.toLocaleString()}</TableCell>
                  <TableCell align="right">{trade.quantity}</TableCell>
                  <TableCell align="right">
                    {trade.pnl !== null && (
                      <Typography 
                        variant="body2" 
                        color={trade.pnl >= 0 ? 'success.main' : 'error.main'}
                      >
                        {trade.pnl >= 0 ? '+' : ''}{trade.pnl.toLocaleString()}
                      </Typography>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  )
}

export default BacktestResults