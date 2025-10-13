import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Button,
  LinearProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  Collapse,
  Stack,
  Grid,
  Divider
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  Refresh,
  NotificationsActive,
  NotificationsOff,
  ExpandMore,
  ExpandLess,
  Bolt,
  ShowChart,
  Update
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'

interface TradingSignal {
  id: string
  stock_code: string
  stock_name: string
  signal_type: 'BUY' | 'SELL' | 'HOLD'
  signal_strength: number
  current_price: number
  volume: number
  created_at: string
  strategy_id: string
  indicators?: any
}

interface Strategy {
  id: string
  name: string
}

interface MarketData {
  stock_code: string
  current_price: number
  change_price: number  // change_amount → change_price
  change_rate: number
  volume: number
  high_52w: number  // 52주 고가
  low_52w: number   // 52주 저가
  market_cap: number
  updated_at: string  // monitored_at → updated_at
}

export default function SignalMonitor() {
  const [signals, setSignals] = useState<TradingSignal[]>([])
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [marketData, setMarketData] = useState<MarketData[]>([])
  const [filterStrategy, setFilterStrategy] = useState<string>('all')
  const [filterType, setFilterType] = useState<string>('all')
  const [notifications, setNotifications] = useState(true)
  const [expandedSignals, setExpandedSignals] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [marketLoading, setMarketLoading] = useState(true)
  const [lastMarketUpdate, setLastMarketUpdate] = useState<Date | null>(null)

  useEffect(() => {
    fetchSignals()
    fetchStrategies()
    fetchMarketData()

    // Supabase Realtime 구독 - 매매 신호
    const signalChannel = supabase
      .channel('signals')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'trading_signals'
        },
        (payload) => {
          setSignals((prev) => [payload.new as TradingSignal, ...prev])
        }
      )
      .subscribe()

    // Supabase Realtime 구독 - 시장 데이터 (kw_price_current 테이블)
    const marketChannel = supabase
      .channel('kw_price_current')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',  // INSERT가 아닌 UPDATE 구독
          schema: 'public',
          table: 'kw_price_current'
        },
        (payload) => {
          console.log('📊 New market data:', payload.new)
          setMarketData((prev) => {
            const newData = payload.new as MarketData
            const exists = prev.findIndex((item) => item.stock_code === newData.stock_code)
            if (exists >= 0) {
              const updated = [...prev]
              updated[exists] = newData
              return updated
            }
            return [newData, ...prev]
          })
          setLastMarketUpdate(new Date())
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(signalChannel)
      supabase.removeChannel(marketChannel)
    }
  }, [])

  const fetchSignals = async () => {
    try {
      const { data, error } = await supabase
        .from('trading_signals')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50)

      if (error) throw error
      setSignals(data || [])
    } catch (error) {
      console.error('Failed to fetch signals:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStrategies = async () => {
    try {
      const { data, error } = await supabase
        .from('strategies')
        .select('id, name')
        .eq('is_active', true)

      if (error) throw error
      setStrategies(data || [])
    } catch (error) {
      console.error('Failed to fetch strategies:', error)
    }
  }

  const fetchMarketData = async () => {
    try {
      setMarketLoading(true)

      // kw_price_current 테이블에서 전체 데이터 조회
      const { data, error } = await supabase
        .from('kw_price_current')
        .select('*')
        .order('updated_at', { ascending: false })
        .limit(20)  // 상위 20개 종목만

      if (error) throw error

      setMarketData(data || [])
      setLastMarketUpdate(new Date())
    } catch (error) {
      console.error('시장 데이터 로드 실패:', error)
    } finally {
      setMarketLoading(false)
    }
  }

  const filteredSignals = signals.filter(signal => {
    if (filterStrategy !== 'all' && signal.strategy_id !== filterStrategy) return false
    if (filterType !== 'all' && signal.signal_type !== filterType) return false
    return true
  })

  const toggleExpand = (signalId: string) => {
    const newExpanded = new Set(expandedSignals)
    if (newExpanded.has(signalId)) {
      newExpanded.delete(signalId)
    } else {
      newExpanded.add(signalId)
    }
    setExpandedSignals(newExpanded)
  }

  const getSignalColor = (type: string) => {
    switch (type) {
      case 'BUY': return 'success'
      case 'SELL': return 'error'
      default: return 'default'
    }
  }

  const getStrengthColor = (strength: number) => {
    if (strength >= 0.8) return '#4caf50'
    if (strength >= 0.6) return '#2196f3'
    if (strength >= 0.4) return '#ff9800'
    return '#757575'
  }

  const getPriceColor = (changeRate: number) => {
    if (changeRate > 0) return 'error.main'
    if (changeRate < 0) return 'primary.main'
    return 'text.secondary'
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)

    if (minutes < 1) return '방금 전'
    if (minutes < 60) return `${minutes}분 전`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}시간 전`
    return `${Math.floor(hours / 24)}일 전`
  }

  const formatVolume = (volume: number) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`
    }
    return volume.toString()
  }

  if (loading) {
    return (
      <Card>
        <CardContent>
          <LinearProgress />
        </CardContent>
      </Card>
    )
  }

  return (
    <Box>
      {/* 시장 모니터링 섹션 */}
      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)' }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Stack direction="row" spacing={1} alignItems="center">
                <ShowChart sx={{ color: 'white' }} />
                <Typography variant="h5" color="white" gutterBottom>
                  시장 모니터링 (n8n)
                </Typography>
              </Stack>
              <Typography variant="body2" color="rgba(255, 255, 255, 0.8)">
                n8n 워크플로우가 1분마다 수집하는 주요 종목 시세
              </Typography>
            </Box>
            <Stack direction="row" spacing={1} alignItems="center">
              {lastMarketUpdate && (
                <Chip
                  icon={<Update />}
                  label={lastMarketUpdate.toLocaleTimeString()}
                  size="small"
                  sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', color: 'white' }}
                />
              )}
              <IconButton onClick={fetchMarketData} sx={{ color: 'white' }}>
                <Refresh />
              </IconButton>
            </Stack>
          </Stack>

          {marketLoading && <LinearProgress sx={{ mb: 2 }} />}

          {marketData.length === 0 && !marketLoading ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              n8n 워크플로우에서 수집한 데이터가 없습니다. 워크플로우가 활성화되어 있는지 확인하세요.
            </Alert>
          ) : (
            <>
              {/* 시장 요약 */}
              <Grid container spacing={2} mb={2}>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(244, 67, 54, 0.1)', border: '1px solid rgba(244, 67, 54, 0.3)' }}>
                    <Typography variant="caption" color="text.secondary">
                      상승
                    </Typography>
                    <Typography variant="h4" color="error.main">
                      {marketData.filter((d) => d.change_rate > 0).length}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(33, 150, 243, 0.1)', border: '1px solid rgba(33, 150, 243, 0.3)' }}>
                    <Typography variant="caption" color="text.secondary">
                      하락
                    </Typography>
                    <Typography variant="h4" color="primary.main">
                      {marketData.filter((d) => d.change_rate < 0).length}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(158, 158, 158, 0.1)', border: '1px solid rgba(158, 158, 158, 0.3)' }}>
                    <Typography variant="caption" color="text.secondary">
                      보합
                    </Typography>
                    <Typography variant="h4">
                      {marketData.filter((d) => d.change_rate === 0).length}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* 시장 데이터 테이블 */}
              <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>종목</TableCell>
                      <TableCell align="right">현재가</TableCell>
                      <TableCell align="right">등락률</TableCell>
                      <TableCell align="right">거래량</TableCell>
                      <TableCell align="right">고가</TableCell>
                      <TableCell align="right">저가</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {marketData.map((item) => (
                      <TableRow key={item.stock_code} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {item.stock_code}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography
                            variant="body2"
                            fontWeight="bold"
                            color={getPriceColor(item.change_rate)}
                          >
                            {item.current_price?.toLocaleString() || '-'}원
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                            {item.change_rate > 0 ? <TrendingUp fontSize="small" color="error" /> :
                             item.change_rate < 0 ? <TrendingDown fontSize="small" color="primary" /> : null}
                            <Typography
                              variant="body2"
                              fontWeight="medium"
                              color={getPriceColor(item.change_rate)}
                            >
                              {item.change_rate > 0 ? '+' : ''}
                              {item.change_rate?.toFixed(2) || '0.00'}%
                            </Typography>
                          </Stack>
                        </TableCell>
                        <TableCell align="right">
                          {formatVolume(item.volume)}
                        </TableCell>
                        <TableCell align="right" sx={{ color: 'error.main' }}>
                          {item.high_52w ? item.high_52w.toLocaleString() : '-'}
                        </TableCell>
                        <TableCell align="right" sx={{ color: 'primary.main' }}>
                          {item.low_52w ? item.low_52w.toLocaleString() : '-'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </>
          )}
        </CardContent>
      </Card>

      <Divider sx={{ my: 3 }} />

      {/* 매매 신호 섹션 */}
      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Stack direction="row" spacing={1} alignItems="center">
                <Bolt sx={{ color: 'white' }} />
                <Typography variant="h5" color="white" gutterBottom>
                  실시간 매매 신호
                </Typography>
              </Stack>
              <Typography variant="body2" color="rgba(255, 255, 255, 0.8)">
                전략별 매수/매도 신호를 실시간으로 모니터링합니다
              </Typography>
            </Box>
            <Stack direction="row" spacing={1}>
              <IconButton
                onClick={() => setNotifications(!notifications)}
                sx={{ color: 'white' }}
              >
                {notifications ? <NotificationsActive /> : <NotificationsOff />}
              </IconButton>
              <IconButton onClick={fetchSignals} sx={{ color: 'white' }}>
                <Refresh />
              </IconButton>
            </Stack>
          </Stack>

          <Stack direction="row" spacing={2}>
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>전략 선택</InputLabel>
              <Select
                value={filterStrategy}
                onChange={(e) => setFilterStrategy(e.target.value)}
                label="전략 선택"
                sx={{
                  color: 'white',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.5)' }
                }}
              >
                <MenuItem value="all">모든 전략</MenuItem>
                {strategies.map(strategy => (
                  <MenuItem key={strategy.id} value={strategy.id}>
                    {strategy.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>신호 타입</InputLabel>
              <Select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                label="신호 타입"
                sx={{
                  color: 'white',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.5)' }
                }}
              >
                <MenuItem value="all">전체</MenuItem>
                <MenuItem value="BUY">매수</MenuItem>
                <MenuItem value="SELL">매도</MenuItem>
                <MenuItem value="HOLD">보류</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </CardContent>
      </Card>

      {filteredSignals.length === 0 ? (
        <Alert severity="info">
          현재 활성화된 신호가 없습니다.
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>종목</TableCell>
                <TableCell align="center">신호</TableCell>
                <TableCell align="center">전략</TableCell>
                <TableCell align="right">현재가</TableCell>
                <TableCell align="right">거래량</TableCell>
                <TableCell align="center">신호강도</TableCell>
                <TableCell align="center">시간</TableCell>
                <TableCell align="center">상세</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredSignals.map((signal) => {
                const strategy = strategies.find(s => s.id === signal.strategy_id)
                const isExpanded = expandedSignals.has(signal.id)

                return (
                  <React.Fragment key={signal.id}>
                    <TableRow hover>
                      <TableCell>
                        <Stack direction="row" spacing={1} alignItems="center">
                          {signal.signal_type === 'BUY' ? (
                            <TrendingUp color="success" />
                          ) : signal.signal_type === 'SELL' ? (
                            <TrendingDown color="error" />
                          ) : null}
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {signal.stock_name || signal.stock_code}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {signal.stock_code}
                            </Typography>
                          </Box>
                        </Stack>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={signal.signal_type}
                          color={getSignalColor(signal.signal_type) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={strategy?.name || '알 수 없음'}
                          variant="outlined"
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        {signal.current_price?.toLocaleString() || '-'}원
                      </TableCell>
                      <TableCell align="right">
                        {signal.volume?.toLocaleString() || '-'}
                      </TableCell>
                      <TableCell align="center">
                        <Stack direction="row" spacing={1} alignItems="center" justifyContent="center">
                          <Bolt sx={{ color: getStrengthColor(signal.signal_strength) }} />
                          <Typography
                            variant="body2"
                            sx={{ color: getStrengthColor(signal.signal_strength), fontWeight: 'bold' }}
                          >
                            {(signal.signal_strength * 100).toFixed(0)}%
                          </Typography>
                        </Stack>
                      </TableCell>
                      <TableCell align="center">
                        <Typography variant="caption" color="text.secondary">
                          {formatTime(signal.created_at)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <IconButton size="small" onClick={() => toggleExpand(signal.id)}>
                          {isExpanded ? <ExpandLess /> : <ExpandMore />}
                        </IconButton>
                      </TableCell>
                    </TableRow>
                    {isExpanded && signal.indicators && (
                      <TableRow>
                        <TableCell colSpan={8}>
                          <Collapse in={isExpanded}>
                            <Box sx={{ p: 2, bgcolor: 'background.default' }}>
                              <Typography variant="subtitle2" gutterBottom>
                                기술적 지표
                              </Typography>
                              <Stack direction="row" spacing={2} flexWrap="wrap">
                                {Object.entries(signal.indicators).map(([key, value]) => (
                                  <Box key={key}>
                                    <Typography variant="caption" color="text.secondary">
                                      {key}
                                    </Typography>
                                    <Typography variant="body2" fontWeight="medium">
                                      {typeof value === 'number' ? value.toFixed(2) : String(value)}
                                    </Typography>
                                  </Box>
                                ))}
                              </Stack>
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    )}
                  </React.Fragment>
                )
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Card sx={{ mt: 2 }}>
        <CardContent sx={{ py: 1 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Stack direction="row" spacing={1} alignItems="center">
              <Box sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: 'success.main',
                animation: 'pulse 2s infinite'
              }} />
              <Typography variant="caption" color="text.secondary">
                실시간 연결됨
              </Typography>
            </Stack>
            <Typography variant="caption" color="text.secondary">
              신호 {filteredSignals.length}개 · 모니터링 {marketData.length}개 종목
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  )
}
