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
  Stack
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  Refresh,
  NotificationsActive,
  NotificationsOff,
  ExpandMore,
  ExpandLess,
  Bolt
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

export default function SignalMonitor() {
  const [signals, setSignals] = useState<TradingSignal[]>([])
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [filterStrategy, setFilterStrategy] = useState<string>('all')
  const [filterType, setFilterType] = useState<string>('all')
  const [notifications, setNotifications] = useState(true)
  const [expandedSignals, setExpandedSignals] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSignals()
    fetchStrategies()

    // Supabase Realtime 구독
    const channel = supabase
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

    return () => {
      supabase.removeChannel(channel)
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
      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Typography variant="h5" color="white" gutterBottom>
                실시간 매매 신호
              </Typography>
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
                        {signal.current_price?.toLocaleString()}원
                      </TableCell>
                      <TableCell align="right">
                        {signal.volume?.toLocaleString()}
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
              총 {filteredSignals.length}개 신호
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  )
}