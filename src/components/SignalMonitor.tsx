import React, { useState, useEffect } from 'react'
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
  Chip,
  Stack,
  Card,
  CardContent,
  IconButton,
  Badge,
  Alert,
  Button,
  LinearProgress,
  Tooltip
} from '@mui/material'
import {
  NotificationsActive,
  TrendingUp,
  TrendingDown,
  Refresh,
  CheckCircle,
  Cancel,
  AccessTime,
  ShowChart,
  Bolt
} from '@mui/icons-material'

interface Signal {
  id: string
  timestamp: Date
  stock: string
  stockCode: string
  type: 'BUY' | 'SELL' | 'HOLD'
  indicator: string
  condition: string
  price: number
  confidence: number
  status: 'pending' | 'executed' | 'cancelled'
  strategy: string
  timeframe?: '일봉' | '주봉' | '월봉'
  splitOrder?: {
    level: 1 | 2 | 3
    totalLevels: number
    percentage: number
  }
  financials?: {
    per?: number
    pbr?: number
    roe?: number
    debtRatio?: number
  }
  riskManagement?: {
    stopLoss?: number
    systemCut?: boolean
    maxLoss?: number
  }
  sectorInfo?: {
    sector: string
    sectorIndex: string
    sectorPerformance: number // % change
    relativeStrength: number // vs sector
    correlation: number // with sector
  }
}

const SignalMonitor: React.FC = () => {
  const [signals, setSignals] = useState<Signal[]>([])
  const [activeStrategies, setActiveStrategies] = useState(3)
  const [isLive, setIsLive] = useState(true)

  // Mock 실시간 신호 생성
  useEffect(() => {
    if (!isLive) return

    const generateSignal = (): Signal => {
      const stocks = [
        { name: '삼성전자', code: '005930', price: 71000, per: 12.5, pbr: 1.2, roe: 9.8, debtRatio: 35, sector: '반도체', market: 'KOSPI' },
        { name: 'SK하이닉스', code: '000660', price: 128500, per: 8.3, pbr: 1.8, roe: 21.5, debtRatio: 42, sector: '반도체', market: 'KOSPI' },
        { name: 'NAVER', code: '035420', price: 215000, per: 28.4, pbr: 2.3, roe: 8.1, debtRatio: 28, sector: 'IT', market: 'KOSPI' },
        { name: '카카오', code: '035720', price: 45200, per: 35.2, pbr: 1.5, roe: 4.3, debtRatio: 22, sector: 'IT', market: 'KOSPI' },
        { name: '에코프로비엠', code: '247540', price: 850000, per: 45.2, pbr: 8.5, roe: 18.8, debtRatio: 15, sector: '2차전지', market: 'KOSDAQ' },
        { name: '셈트리온', code: '195870', price: 85000, per: 65.3, pbr: 3.2, roe: 4.9, debtRatio: 68, sector: '바이오', market: 'KOSDAQ' }
      ]
      
      const stock = stocks[Math.floor(Math.random() * stocks.length)]
      const types: Signal['type'][] = ['BUY', 'SELL', 'HOLD']
      const indicators = ['RSI', 'MACD', 'BB', 'MA Cross', 'Volume', '일목균형표', 'Stochastic']
      const strategies = ['모멘텀 전략', '평균회귀 전략', 'RSI + MACD', '일목균형표']
      
      const timeframes: ('일봉' | '주봉' | '월봉')[] = ['일봉', '주봉', '월봉']
      const shouldSplit = Math.random() > 0.7
      const signalType = types[Math.floor(Math.random() * types.length)]
      const sectorPerf = (Math.random() - 0.5) * 10 // -5% to +5%
      const relStrength = (Math.random() - 0.5) * 20 // -10% to +10%
      
      return {
        id: Date.now().toString(),
        timestamp: new Date(),
        stock: stock.name,
        stockCode: stock.code,
        type: signalType,
        indicator: indicators[Math.floor(Math.random() * indicators.length)],
        condition: `${Math.random() > 0.5 ? '상향' : '하향'} 돌파`,
        price: stock.price + Math.floor(Math.random() * 1000 - 500),
        confidence: Math.random() * 40 + 60,
        status: 'pending',
        strategy: strategies[Math.floor(Math.random() * strategies.length)],
        timeframe: timeframes[Math.floor(Math.random() * timeframes.length)],
        splitOrder: shouldSplit ? {
          level: Math.floor(Math.random() * 3) + 1 as 1 | 2 | 3,
          totalLevels: 3,
          percentage: signalType === 'BUY' ? 33.3 : 50
        } : undefined,
        financials: {
          per: stock.per,
          pbr: stock.pbr,
          roe: stock.roe,
          debtRatio: stock.debtRatio
        },
        riskManagement: {
          stopLoss: signalType === 'BUY' ? -3 : undefined,
          systemCut: Math.random() > 0.8,
          maxLoss: -5
        },
        sectorInfo: {
          sector: stock.sector,
          sectorIndex: stock.market === 'KOSPI' ? 'KOSPI ' + stock.sector : 'KOSDAQ ' + stock.sector,
          sectorPerformance: sectorPerf,
          relativeStrength: relStrength,
          correlation: Math.random() * 0.8 + 0.2 // 0.2 to 1.0
        }
      }
    }

    const interval = setInterval(() => {
      const newSignal = generateSignal()
      setSignals(prev => [newSignal, ...prev].slice(0, 50))
    }, Math.random() * 5000 + 3000)

    return () => clearInterval(interval)
  }, [isLive])

  const executeSignal = (id: string) => {
    setSignals(prev => prev.map(s => 
      s.id === id ? { ...s, status: 'executed' } : s
    ))
  }

  const cancelSignal = (id: string) => {
    setSignals(prev => prev.map(s => 
      s.id === id ? { ...s, status: 'cancelled' } : s
    ))
  }

  const getSignalColor = (type: Signal['type']) => {
    switch(type) {
      case 'BUY': return 'error'
      case 'SELL': return 'primary'
      case 'HOLD': return 'default'
    }
  }

  const getStatusColor = (status: Signal['status']) => {
    switch(status) {
      case 'executed': return 'success'
      case 'cancelled': return 'error'
      case 'pending': return 'warning'
    }
  }

  const recentBuySignals = signals.filter(s => s.type === 'BUY' && s.status === 'pending').length
  const recentSellSignals = signals.filter(s => s.type === 'SELL' && s.status === 'pending').length

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h5">
          <Bolt sx={{ mr: 1, verticalAlign: 'middle', color: isLive ? 'success.main' : 'text.disabled' }} />
          실시간 신호 모니터
        </Typography>
        
        <Stack direction="row" spacing={2}>
          <Button
            variant={isLive ? 'contained' : 'outlined'}
            color={isLive ? 'success' : 'inherit'}
            onClick={() => setIsLive(!isLive)}
            startIcon={isLive ? <NotificationsActive /> : <Cancel />}
          >
            {isLive ? 'LIVE' : 'PAUSED'}
          </Button>
          <IconButton onClick={() => setSignals([])}>
            <Refresh />
          </IconButton>
        </Stack>
      </Stack>

      {/* 상태 카드 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    활성 전략
                  </Typography>
                  <Typography variant="h4">
                    {activeStrategies}
                  </Typography>
                </Box>
                <ShowChart sx={{ fontSize: 40, color: 'primary.main' }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    매수 신호
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {recentBuySignals}
                  </Typography>
                </Box>
                <Badge badgeContent={recentBuySignals} color="error">
                  <TrendingUp sx={{ fontSize: 40, color: 'error.main' }} />
                </Badge>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    매도 신호
                  </Typography>
                  <Typography variant="h4" color="primary.main">
                    {recentSellSignals}
                  </Typography>
                </Box>
                <Badge badgeContent={recentSellSignals} color="primary">
                  <TrendingDown sx={{ fontSize: 40, color: 'primary.main' }} />
                </Badge>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    오늘 실행
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {signals.filter(s => s.status === 'executed').length}
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, color: 'success.main' }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 실시간 진행 표시 */}
      {isLive && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress color="success" variant="indeterminate" />
        </Box>
      )}

      {/* 신호 테이블 */}
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>시간</TableCell>
              <TableCell>종목</TableCell>
              <TableCell>신호</TableCell>
              <TableCell>차트</TableCell>
              <TableCell>지표</TableCell>
              <TableCell>조건</TableCell>
              <TableCell align="right">가격</TableCell>
              <TableCell>신뢰도</TableCell>
              <TableCell>전략</TableCell>
              <TableCell>업종</TableCell>
              <TableCell>분할</TableCell>
              <TableCell>재무</TableCell>
              <TableCell>리스크</TableCell>
              <TableCell>상태</TableCell>
              <TableCell align="center">액션</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {signals.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10} align="center">
                  <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                    대기 중인 신호가 없습니다
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              signals.map((signal) => (
                <TableRow 
                  key={signal.id}
                  sx={{ 
                    opacity: signal.status === 'cancelled' ? 0.5 : 1,
                    bgcolor: signal.status === 'executed' ? 'success.light' : 'inherit'
                  }}
                >
                  <TableCell>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <AccessTime fontSize="small" />
                      <Typography variant="body2">
                        {signal.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Stack>
                      <Typography variant="body2">{signal.stock}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {signal.stockCode}
                      </Typography>
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Stack spacing={0.5}>
                      <Chip 
                        label={signal.type} 
                        size="small" 
                        color={getSignalColor(signal.type)}
                      />
                      {signal.splitOrder && (
                        <Typography variant="caption" color="text.secondary">
                          {signal.splitOrder.level}차/{signal.splitOrder.totalLevels}
                        </Typography>
                      )}
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={signal.timeframe || '일봉'} 
                      size="small" 
                      variant="outlined"
                      color={signal.timeframe === '월봉' ? 'secondary' : signal.timeframe === '주봉' ? 'primary' : 'default'}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip label={signal.indicator} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>{signal.condition}</TableCell>
                  <TableCell align="right">
                    {signal.price.toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <LinearProgress 
                        variant="determinate" 
                        value={signal.confidence} 
                        sx={{ width: 50, height: 6, borderRadius: 3 }}
                        color={signal.confidence > 80 ? 'success' : signal.confidence > 60 ? 'warning' : 'error'}
                      />
                      <Typography variant="caption">
                        {signal.confidence.toFixed(0)}%
                      </Typography>
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">{signal.strategy}</Typography>
                  </TableCell>
                  <TableCell>
                    {signal.sectorInfo && (
                      <Stack spacing={0.5}>
                        <Chip 
                          label={signal.sectorInfo.sector} 
                          size="small" 
                          variant="outlined"
                          color={signal.sectorInfo.sectorPerformance > 0 ? 'success' : 'error'}
                        />
                        <Tooltip title={`업종 성과: ${signal.sectorInfo.sectorPerformance.toFixed(1)}%\n상대강도: ${signal.sectorInfo.relativeStrength.toFixed(1)}%\n상관계수: ${signal.sectorInfo.correlation.toFixed(2)}`}>
                          <Typography variant="caption" sx={{ cursor: 'help' }}>
                            RS: {signal.sectorInfo.relativeStrength > 0 ? '+' : ''}{signal.sectorInfo.relativeStrength.toFixed(1)}%
                          </Typography>
                        </Tooltip>
                      </Stack>
                    )}
                  </TableCell>
                  <TableCell>
                    {signal.splitOrder ? (
                      <Typography variant="caption">
                        {signal.splitOrder.percentage}%
                      </Typography>
                    ) : (
                      <Typography variant="caption" color="text.secondary">-</Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {signal.financials && (
                      <Tooltip title={
                        `PER: ${signal.financials.per}\nPBR: ${signal.financials.pbr}\nROE: ${signal.financials.roe}%\n부채비율: ${signal.financials.debtRatio}%`
                      }>
                        <Typography variant="caption" sx={{ cursor: 'help' }}>
                          P{signal.financials.per?.toFixed(1)}
                        </Typography>
                      </Tooltip>
                    )}
                  </TableCell>
                  <TableCell>
                    {signal.riskManagement && (
                      <Stack spacing={0.5}>
                        {signal.riskManagement.stopLoss && (
                          <Typography variant="caption" color="error">
                            SL: {signal.riskManagement.stopLoss}%
                          </Typography>
                        )}
                        {signal.riskManagement.systemCut && (
                          <Chip label="CUT" size="small" color="error" />
                        )}
                      </Stack>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={signal.status} 
                      size="small" 
                      color={getStatusColor(signal.status)}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell align="center">
                    {signal.status === 'pending' && (
                      <Stack direction="row" spacing={1}>
                        <Tooltip title="실행">
                          <IconButton 
                            size="small" 
                            color="success"
                            onClick={() => executeSignal(signal.id)}
                          >
                            <CheckCircle />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="취소">
                          <IconButton 
                            size="small" 
                            color="error"
                            onClick={() => cancelSignal(signal.id)}
                          >
                            <Cancel />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 알림 설정 */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          신호 발생 시 자동으로 주문을 실행하려면 자동 실행 모드를 활성화하세요.
          현재는 수동 확인 모드입니다.
        </Typography>
      </Alert>
    </Box>
  )
}

export default SignalMonitor