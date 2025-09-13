import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Stack,
  Chip,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
  CircularProgress,
  IconButton,
  Tooltip,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  SelectChangeEvent,
  FormControlLabel,
  Checkbox,
  Autocomplete
} from '@mui/material'
import {
  PlayArrow,
  Refresh,
  Download,
  CheckCircle,
  Cancel,
  Warning,
  Info,
  TrendingUp,
  TrendingDown,
  ExpandMore,
  ExpandLess,
  Assessment,
  ShowChart,
  Timeline,
  Speed,
  AttachMoney,
  Percent
} from '@mui/icons-material'

interface StrategyAnalysisProps {
  strategy?: any
  investmentConfig?: any
}

interface AnalysisResult {
  timestamp: string
  strategy_summary: {
    indicators_count: number
    indicators: any[]
    buy_conditions_count: number
    sell_conditions_count: number
  }
  signal_analysis: {
    buy_signal_count: number
    sell_signal_count: number
    buy_signal_interval_avg?: number
    signals: any[]
  }
  backtest_analysis: {
    total_return: number
    win_rate: number
    sharpe_ratio: number
    max_drawdown: number
    total_trades: number
    winning_trades: number
    losing_trades: number
    profit_factor: number
    trades: any[]
  }
  condition_analysis: {
    buy_conditions_detail: any[]
    sell_conditions_detail: any[]
  }
}

const StrategyAnalysis: React.FC<StrategyAnalysisProps> = ({ strategy: initialStrategy, investmentConfig }) => {
  const [loading, setLoading] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedStocks, setSelectedStocks] = useState<string[]>(['005930']) // 기본값: 삼성전자
  const [startDate, setStartDate] = useState('2024-01-01')
  const [endDate, setEndDate] = useState('2024-06-30')
  const [selectedStrategy, setSelectedStrategy] = useState<any>(initialStrategy)
  const [savedStrategies, setSavedStrategies] = useState<any[]>([])
  const [expandedSections, setExpandedSections] = useState({
    signals: true,
    performance: true,
    conditions: false,
    trades: false
  })

  // 사용 가능한 종목 목록
  const availableStocks = [
    { code: '005930', name: '삼성전자' },
    { code: '000660', name: 'SK하이닉스' },
    { code: '035720', name: '카카오' },
    { code: '035420', name: '네이버' },
    { code: '051910', name: 'LG화학' },
    { code: '006400', name: '삼성SDI' },
    { code: '005380', name: '현대차' },
    { code: '000270', name: '기아' },
    { code: '068270', name: '셀트리온' },
    { code: '105560', name: 'KB금융' }
  ]

  // Supabase에서 저장된 전략 불러오기
  useEffect(() => {
    loadSavedStrategies()
  }, [])

  const loadSavedStrategies = async () => {
    try {
      const { supabase } = await import('../lib/supabase')
      const { data, error } = await supabase
        .from('strategies')
        .select('*')
        .order('created_at', { ascending: false })

      if (!error && data) {
        setSavedStrategies(data)
      }
    } catch (err) {
      console.error('전략 로드 실패:', err)
    }
  }

  const runAnalysis = async () => {
    if (!selectedStrategy) {
      setError('분석할 전략을 선택해주세요.')
      return
    }

    if (selectedStocks.length === 0) {
      setError('분석할 종목을 하나 이상 선택해주세요.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // 백엔드 API 호출
      const response = await fetch('http://localhost:8001/api/backtest/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_config: {
            indicators: selectedStrategy?.indicators || [],
            buyConditions: selectedStrategy?.buyConditions || [],
            sellConditions: selectedStrategy?.sellConditions || [],
            ...investmentConfig
          },
          stock_codes: selectedStocks, // 다중 종목 지원
          start_date: startDate,
          end_date: endDate,
          save_to_file: false
        })
      })

      if (!response.ok) {
        throw new Error('분석 실행 실패')
      }

      const data = await response.json()

      // 백엔드 응답 구조에 맞게 데이터 처리
      if (data.success && data.results_by_stock) {
        // 첫 번째 종목의 결과를 기본으로 표시 (추후 멀티 종목 UI 확장 가능)
        const firstStock = selectedStocks[0]
        setAnalysisResult(data.results_by_stock[firstStock])

        // 전체 요약 정보도 저장 (나중에 사용 가능)
        console.log('전체 요약:', data.summary)
      } else {
        throw new Error(data.detail || '분석 결과를 받지 못했습니다')
      }
    } catch (err) {
      console.error('분석 오류:', err)
      setError('분석 중 오류가 발생했습니다. 서버 연결을 확인해주세요.')

      // 더미 데이터 (테스트용)
      setAnalysisResult(createDummyResult())
    } finally {
      setLoading(false)
    }
  }

  const createDummyResult = (): AnalysisResult => ({
    timestamp: new Date().toISOString(),
    strategy_summary: {
      indicators_count: selectedStrategy?.indicators?.length || 0,
      indicators: selectedStrategy?.indicators || [],
      buy_conditions_count: selectedStrategy?.buyConditions?.length || 0,
      sell_conditions_count: selectedStrategy?.sellConditions?.length || 0
    },
    signal_analysis: {
      buy_signal_count: 15,
      sell_signal_count: 12,
      buy_signal_interval_avg: 8.5,
      signals: [
        { date: '2024-01-15', type: 'BUY', price: 68500, conditions_met: [] },
        { date: '2024-01-28', type: 'SELL', price: 71200, conditions_met: [] },
        { date: '2024-02-10', type: 'BUY', price: 69800, conditions_met: [] },
        { date: '2024-02-25', type: 'SELL', price: 72500, conditions_met: [] }
      ]
    },
    backtest_analysis: {
      total_return: 12.5,
      win_rate: 65,
      sharpe_ratio: 1.35,
      max_drawdown: 8.2,
      total_trades: 12,
      winning_trades: 8,
      losing_trades: 4,
      profit_factor: 2.1,
      trades: []
    },
    condition_analysis: {
      buy_conditions_detail: selectedStrategy?.buyConditions?.map((cond: any) => ({
        condition: cond,
        met_count: Math.floor(Math.random() * 50) + 10,
        met_percentage: Math.random() * 30 + 10
      })) || [],
      sell_conditions_detail: selectedStrategy?.sellConditions?.map((cond: any) => ({
        condition: cond,
        met_count: Math.floor(Math.random() * 50) + 10,
        met_percentage: Math.random() * 30 + 10
      })) || []
    }
  })

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const getPerformanceColor = (value: number, type: 'return' | 'rate' | 'drawdown') => {
    if (type === 'drawdown') {
      return value < 10 ? 'success' : value < 20 ? 'warning' : 'error'
    }
    return value > 0 ? 'success' : 'error'
  }

  return (
    <Box>
      {/* 전략 선택 섹션 */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          전략 선택
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <FormControl fullWidth size="small">
              <InputLabel>분석할 전략 선택</InputLabel>
              <Select
                value={selectedStrategy?.id || ''}
                onChange={(e) => {
                  const strategy = savedStrategies.find(s => s.id === e.target.value)
                  setSelectedStrategy(strategy)
                }}
                label="분석할 전략 선택"
              >
                {initialStrategy && (
                  <MenuItem value={initialStrategy.id}>
                    현재 편집 중인 전략
                  </MenuItem>
                )}
                {savedStrategies.map((strat) => (
                  <MenuItem key={strat.id} value={strat.id}>
                    {strat.name} {strat.is_public ? '(공개)' : '(비공개)'}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            {selectedStrategy && (
              <Typography variant="body2" color="text.secondary">
                지표: {selectedStrategy.indicators?.length || 0}개,
                매수조건: {selectedStrategy.buyConditions?.length || 0}개,
                매도조건: {selectedStrategy.sellConditions?.length || 0}개
              </Typography>
            )}
          </Grid>
        </Grid>
      </Paper>

      {/* 분석 설정 */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          분석 설정
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <Autocomplete
              multiple
              size="small"
              options={availableStocks}
              getOptionLabel={(option) => `${option.name} (${option.code})`}
              value={availableStocks.filter(s => selectedStocks.includes(s.code))}
              onChange={(_, newValue) => {
                setSelectedStocks(newValue.map(v => v.code))
              }}
              renderInput={(params) => (
                <TextField {...params} label="테스트할 종목 선택" placeholder="종목 선택" />
              )}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              size="small"
              label="시작일"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              size="small"
              label="종료일"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <Stack direction="row" spacing={1}>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PlayArrow />}
                onClick={runAnalysis}
                disabled={loading || !selectedStrategy || selectedStocks.length === 0}
                size="small"
              >
                {loading ? '분석 중...' : '분석 실행'}
              </Button>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={runAnalysis}
                disabled={loading || !analysisResult}
                size="small"
              >
                재분석
              </Button>
              {analysisResult && (
                <Button
                  variant="outlined"
                  startIcon={<Download />}
                  size="small"
                  onClick={() => {
                    // CSV 다운로드 구현
                    const csvContent = 'data:text/csv;charset=utf-8,' +
                      'Date,Type,Price\n' +
                      analysisResult.signal_analysis.signals
                        .map(s => `${s.date},${s.type},${s.price}`)
                        .join('\n')
                    const link = document.createElement('a')
                    link.href = encodeURI(csvContent)
                    link.download = `strategy_analysis_${new Date().toISOString()}.csv`
                    link.click()
                  }}
                >
                  결과 다운로드
                </Button>
              )}
            </Stack>
          </Grid>
        </Grid>
        {analysisResult && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            마지막 분석: {new Date(analysisResult.timestamp).toLocaleString()}
          </Typography>
        )}
      </Paper>

      {/* 에러 메시지 */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* 전략 요약 */}
      {selectedStrategy && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              현재 전략: {selectedStrategy?.name || '이름 없음'}
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
              <Chip
                icon={<ShowChart />}
                label={`지표 ${selectedStrategy?.indicators?.length || 0}개`}
                size="small"
              />
              <Chip
                icon={<TrendingUp />}
                label={`매수조건 ${selectedStrategy?.buyConditions?.length || 0}개`}
                size="small"
                color="success"
              />
              <Chip
                icon={<TrendingDown />}
                label={`매도조건 ${selectedStrategy?.sellConditions?.length || 0}개`}
                size="small"
                color="error"
              />
            </Stack>
          </CardContent>
        </Card>
      )}

      {/* 분석 결과 */}
      {analysisResult && (
        <Grid container spacing={3}>
          {/* 성과 요약 카드 */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="center"
                sx={{ mb: 2 }}
              >
                <Typography variant="h6">성과 요약</Typography>
                <IconButton size="small" onClick={() => toggleSection('performance')}>
                  {expandedSections.performance ? <ExpandLess /> : <ExpandMore />}
                </IconButton>
              </Stack>
              <Collapse in={expandedSections.performance}>
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Stack spacing={1}>
                          <Typography variant="caption" color="text.secondary">
                            총 수익률
                          </Typography>
                          <Typography variant="h5" color={getPerformanceColor(analysisResult.backtest_analysis.total_return, 'return')}>
                            {analysisResult.backtest_analysis.total_return.toFixed(2)}%
                          </Typography>
                        </Stack>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Stack spacing={1}>
                          <Typography variant="caption" color="text.secondary">
                            승률
                          </Typography>
                          <Typography variant="h5">
                            {analysisResult.backtest_analysis.win_rate.toFixed(1)}%
                          </Typography>
                          <Typography variant="caption">
                            {analysisResult.backtest_analysis.winning_trades}승 {analysisResult.backtest_analysis.losing_trades}패
                          </Typography>
                        </Stack>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Stack spacing={1}>
                          <Typography variant="caption" color="text.secondary">
                            최대 낙폭
                          </Typography>
                          <Typography variant="h5" color={getPerformanceColor(analysisResult.backtest_analysis.max_drawdown, 'drawdown')}>
                            -{analysisResult.backtest_analysis.max_drawdown.toFixed(2)}%
                          </Typography>
                        </Stack>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Stack spacing={1}>
                          <Typography variant="caption" color="text.secondary">
                            샤프 비율
                          </Typography>
                          <Typography variant="h5">
                            {analysisResult.backtest_analysis.sharpe_ratio.toFixed(2)}
                          </Typography>
                        </Stack>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Collapse>
            </Paper>
          </Grid>

          {/* 신호 분석 */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="center"
                sx={{ mb: 2 }}
              >
                <Typography variant="h6">신호 분석</Typography>
                <IconButton size="small" onClick={() => toggleSection('signals')}>
                  {expandedSections.signals ? <ExpandLess /> : <ExpandMore />}
                </IconButton>
              </Stack>
              <Collapse in={expandedSections.signals}>
                <Stack spacing={2}>
                  <Stack direction="row" spacing={2}>
                    <Chip
                      icon={<TrendingUp />}
                      label={`매수 신호: ${analysisResult.signal_analysis.buy_signal_count}회`}
                      color="success"
                    />
                    <Chip
                      icon={<TrendingDown />}
                      label={`매도 신호: ${analysisResult.signal_analysis.sell_signal_count}회`}
                      color="error"
                    />
                  </Stack>
                  {analysisResult.signal_analysis.buy_signal_interval_avg && (
                    <Typography variant="body2" color="text.secondary">
                      평균 매수 간격: {analysisResult.signal_analysis.buy_signal_interval_avg.toFixed(1)}일
                    </Typography>
                  )}
                  <Divider />
                  <Typography variant="subtitle2">최근 신호</Typography>
                  <List dense>
                    {analysisResult.signal_analysis.signals.slice(0, 4).map((signal, idx) => (
                      <ListItem key={idx}>
                        <ListItemIcon>
                          {signal.type === 'BUY' ?
                            <TrendingUp color="success" /> :
                            <TrendingDown color="error" />
                          }
                        </ListItemIcon>
                        <ListItemText
                          primary={`${signal.date} - ${signal.type}`}
                          secondary={`가격: ${signal.price.toLocaleString()}원`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Stack>
              </Collapse>
            </Paper>
          </Grid>

          {/* 조건 충족 분석 */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="center"
                sx={{ mb: 2 }}
              >
                <Typography variant="h6">조건 충족 분석</Typography>
                <IconButton size="small" onClick={() => toggleSection('conditions')}>
                  {expandedSections.conditions ? <ExpandLess /> : <ExpandMore />}
                </IconButton>
              </Stack>
              <Collapse in={expandedSections.conditions}>
                <Stack spacing={2}>
                  <div>
                    <Typography variant="subtitle2" gutterBottom>매수 조건</Typography>
                    {analysisResult.condition_analysis.buy_conditions_detail.map((detail, idx) => (
                      <Box key={idx} sx={{ mb: 1 }}>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2">
                            {detail.condition.indicator} {detail.condition.operator} {detail.condition.value}
                          </Typography>
                          <Chip
                            label={`${detail.met_percentage.toFixed(1)}%`}
                            size="small"
                            color={detail.met_percentage > 20 ? 'success' : 'default'}
                          />
                        </Stack>
                        <LinearProgress
                          variant="determinate"
                          value={detail.met_percentage}
                          sx={{ mt: 0.5, height: 4 }}
                        />
                      </Box>
                    ))}
                  </div>
                  <Divider />
                  <div>
                    <Typography variant="subtitle2" gutterBottom>매도 조건</Typography>
                    {analysisResult.condition_analysis.sell_conditions_detail.map((detail, idx) => (
                      <Box key={idx} sx={{ mb: 1 }}>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2">
                            {detail.condition.indicator} {detail.condition.operator} {detail.condition.value}
                          </Typography>
                          <Chip
                            label={`${detail.met_percentage.toFixed(1)}%`}
                            size="small"
                            color={detail.met_percentage > 20 ? 'error' : 'default'}
                          />
                        </Stack>
                        <LinearProgress
                          variant="determinate"
                          value={detail.met_percentage}
                          sx={{ mt: 0.5, height: 4 }}
                          color="error"
                        />
                      </Box>
                    ))}
                  </div>
                </Stack>
              </Collapse>
            </Paper>
          </Grid>

          {/* 거래 내역 테이블 */}
          {analysisResult.signal_analysis.signals.length > 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Stack
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center"
                  sx={{ mb: 2 }}
                >
                  <Typography variant="h6">거래 신호 상세</Typography>
                  <IconButton size="small" onClick={() => toggleSection('trades')}>
                    {expandedSections.trades ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Stack>
                <Collapse in={expandedSections.trades}>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>날짜</TableCell>
                          <TableCell>유형</TableCell>
                          <TableCell align="right">가격</TableCell>
                          <TableCell>조건</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {analysisResult.signal_analysis.signals.map((signal, idx) => (
                          <TableRow key={idx}>
                            <TableCell>{signal.date}</TableCell>
                            <TableCell>
                              <Chip
                                label={signal.type}
                                size="small"
                                color={signal.type === 'BUY' ? 'success' : 'error'}
                              />
                            </TableCell>
                            <TableCell align="right">{signal.price.toLocaleString()}원</TableCell>
                            <TableCell>
                              {signal.conditions_met?.length > 0 ?
                                signal.conditions_met.map((c: any) => c.indicator).join(', ') :
                                '-'
                              }
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Collapse>
              </Paper>
            </Grid>
          )}

          {/* 진단 및 개선 제안 */}
          <Grid item xs={12}>
            <Alert severity="info" icon={<Info />}>
              <Typography variant="subtitle2" gutterBottom>
                전략 진단
              </Typography>
              {analysisResult.signal_analysis.buy_signal_count < 5 && (
                <Typography variant="body2">
                  • 매수 신호가 적습니다. 조건을 완화해보세요.
                </Typography>
              )}
              {analysisResult.backtest_analysis.win_rate < 40 && (
                <Typography variant="body2">
                  • 승률이 낮습니다. 매수/매도 조건을 재검토하세요.
                </Typography>
              )}
              {analysisResult.backtest_analysis.max_drawdown > 20 && (
                <Typography variant="body2">
                  • 최대 낙폭이 큽니다. 리스크 관리를 강화하세요.
                </Typography>
              )}
              {analysisResult.backtest_analysis.win_rate > 60 &&
               analysisResult.backtest_analysis.total_return > 10 && (
                <Typography variant="body2" color="success.main">
                  • 전략 성과가 양호합니다!
                </Typography>
              )}
            </Alert>
          </Grid>
        </Grid>
      )}

      {/* 초기 상태 */}
      {!analysisResult && !loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Assessment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            전략 분석 준비
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            전략을 구성한 후 '전략 분석 실행' 버튼을 클릭하여 상세한 분석 결과를 확인하세요.
          </Typography>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={runAnalysis}
            disabled={!selectedStrategy}
          >
            분석 시작
          </Button>
        </Paper>
      )}
    </Box>
  )
}

export default StrategyAnalysis