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
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Pagination
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
  Update,
  CheckCircle,
  Error,
  Schedule,
  PlayArrow,
  Timer
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'
import { isMarketOpen, getMarketStatusMessage } from '../utils/marketHours'
import { n8nClient, WorkflowExecutionSummary, NodeExecutionStatus } from '../lib/n8n'

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
  allocated_capital?: number
  allocated_percent?: number
}

interface MarketData {
  stock_code: string
  stock_name: string
  current_price: number
  change_price: number  // change_amount → change_price
  change_rate: number
  volume: number
  high_52w: number  // 52주 고가
  low_52w: number   // 52주 저가
  market_cap: number
  updated_at: string  // monitored_at → updated_at
}

interface WorkflowStats {
  last1min: number
  last5min: number
  successRate: number
  totalExecutions: number
}

interface PendingStock {
  stock_code: string
  stock_name: string
  current_price: number
  condition_match_score: number
  is_near_entry: boolean
  strategy_id: string
  updated_at: string
}

interface PendingSellStock {
  stock_code: string
  stock_name: string
  current_price: number
  exit_condition_match_score: number
  is_near_exit: boolean
  is_held: boolean
  strategy_id: string
  updated_at: string
}

export default function SignalMonitor() {
  const [signals, setSignals] = useState<TradingSignal[]>([])
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [marketData, setMarketData] = useState<MarketData[]>([])
  const [pendingStocks, setPendingStocks] = useState<PendingStock[]>([])
  const [pendingSellStocks, setPendingSellStocks] = useState<PendingSellStock[]>([])
  const [filterStrategy, setFilterStrategy] = useState<string>('all')
  const [filterType, setFilterType] = useState<string>('all')
  const [notifications, setNotifications] = useState(true)
  const [expandedSignals, setExpandedSignals] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [signalPage, setSignalPage] = useState(1)
  const [signalsPerPage] = useState(10)
  const [marketLoading, setMarketLoading] = useState(true)
  const [lastMarketUpdate, setLastMarketUpdate] = useState<Date | null>(null)
  const [workflowStats, setWorkflowStats] = useState<WorkflowStats>({
    last1min: 0,
    last5min: 0,
    successRate: 0,
    totalExecutions: 0
  })
  const [marketStats, setMarketStats] = useState({
    rising: 0,
    falling: 0,
    neutral: 0
  })
  const [workflows, setWorkflows] = useState<WorkflowExecutionSummary[]>([])
  const [workflowLoading, setWorkflowLoading] = useState(true)
  const [workflowError, setWorkflowError] = useState<string | null>(null)
  const [lastWorkflowUpdate, setLastWorkflowUpdate] = useState<Date | null>(null)
  const [expandedWorkflow, setExpandedWorkflow] = useState<string | false>(false)
  const [marketStatus, setMarketStatus] = useState<string>('')
  const [showAllStocks, setShowAllStocks] = useState(false)

  useEffect(() => {
    fetchSignals()
    fetchStrategies()
    fetchMarketData()
    fetchPendingStocks()
    fetchPendingSellStocks()  // 매도 대기 종목 초기 로드
    fetchWorkflowStats()
    fetchWorkflowData()

    // 시장 상태 초기화 및 주기적 업데이트
    setMarketStatus(getMarketStatusMessage())
    const statusInterval = setInterval(() => {
      setMarketStatus(getMarketStatusMessage())
    }, 60000) // 1분마다 시장 상태 업데이트

    // 워크플로우 통계 30초마다 업데이트 (시장 오픈 시간에만)
    const statsInterval = setInterval(() => {
      if (isMarketOpen()) {
        fetchWorkflowStats()
        fetchWorkflowData()
        fetchPendingStocks()  // 매수 대기 종목도 함께 업데이트
        fetchPendingSellStocks()  // 매도 대기 종목도 함께 업데이트
      }
    }, 30000)

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
      clearInterval(statusInterval)
      clearInterval(statsInterval)
      supabase.removeChannel(signalChannel)
      supabase.removeChannel(marketChannel)
    }
  }, [])

  const fetchSignals = async () => {
    try {
      // 활성화된 자동매매 전략의 신호만 가져오기
      const { data: activeStrategyIds } = await supabase
        .from('strategies')
        .select('id')
        .eq('is_active', true)
        .eq('auto_trade_enabled', true)

      if (!activeStrategyIds || activeStrategyIds.length === 0) {
        setSignals([])
        return
      }

      const strategyIds = activeStrategyIds.map(s => s.id)

      // 최근 24시간 이내 신호만 조회
      const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()

      const { data, error } = await supabase
        .from('trading_signals')
        .select('*')
        .in('strategy_id', strategyIds)
        .gte('created_at', twentyFourHoursAgo)  // 최근 24시간 필터 추가
        .order('created_at', { ascending: false })
        .limit(100)

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
        .eq('auto_trade_enabled', true)

      if (error) throw error
      setStrategies(data || [])
    } catch (error) {
      console.error('Failed to fetch strategies:', error)
    }
  }

  const fetchMarketData = async () => {
    try {
      setMarketLoading(true)

      // RPC로 활성화된 전략의 필터링된 종목 코드 가져오기 (온라인 배포 버전과 동일한 방식)
      const { data: strategyData, error: strategyError } = await supabase
        .rpc('get_active_strategies_with_universe')

      if (strategyError) {
        console.error('전략 데이터 로드 실패:', strategyError)
        setMarketData([])
        setLastMarketUpdate(new Date())
        return
      }

      // 모니터링할 종목 코드 수집
      const monitoredStockCodes = new Set<string>()
      strategyData?.forEach((strategy: any) => {
        if (strategy.filtered_stocks && Array.isArray(strategy.filtered_stocks)) {
          strategy.filtered_stocks.forEach((code: string) => monitoredStockCodes.add(code))
        }
      })

      if (monitoredStockCodes.size === 0) {
        setMarketData([])
        setLastMarketUpdate(new Date())
        return
      }

      const stockCodesArray = Array.from(monitoredStockCodes)

      // 종목 코드로 현재가 정보 가져오기
      const { data, error } = await supabase
        .from('kw_price_current')
        .select('*')
        .in('stock_code', stockCodesArray)
        .order('updated_at', { ascending: false })

      if (error) throw error

      setMarketData(data || [])
      setLastMarketUpdate(new Date())

      // 시장 통계 계산 (상승/하락/보합)
      if (data && data.length > 0) {
        const rising = data.filter(d => d.change_rate > 0).length
        const falling = data.filter(d => d.change_rate < 0).length
        const neutral = data.filter(d => d.change_rate === 0).length
        setMarketStats({ rising, falling, neutral })
      } else {
        setMarketStats({ rising: 0, falling: 0, neutral: 0 })
      }
    } catch (error) {
      console.error('시장 데이터 로드 실패:', error)
    } finally {
      setMarketLoading(false)
    }
  }

  const fetchPendingStocks = async () => {
    try {
      // 활성화된 자동매매 전략의 매수 대기 종목 조회
      const { data: activeStrategyIds } = await supabase
        .from('strategies')
        .select('id')
        .eq('is_active', true)
        .eq('auto_trade_enabled', true)

      if (!activeStrategyIds || activeStrategyIds.length === 0) {
        setPendingStocks([])
        return
      }

      const strategyIds = activeStrategyIds.map(s => s.id)

      // 조건 근접도 80% 이상인 종목 조회 (최근 1시간 이내)
      const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString()

      const { data, error } = await supabase
        .from('strategy_monitoring')
        .select('*')
        .in('strategy_id', strategyIds)
        .gte('condition_match_score', 80)
        .lt('condition_match_score', 100)  // 100점은 이미 신호 발생
        .gte('updated_at', oneHourAgo)
        .order('condition_match_score', { ascending: false })
        .limit(50)

      if (error) throw error
      setPendingStocks(data || [])
    } catch (error) {
      console.error('매수 대기 종목 조회 실패:', error)
    }
  }

  const fetchPendingSellStocks = async () => {
    try {
      // 활성화된 자동매매 전략의 매도 대기 종목 조회 (보유 종목만!)
      const { data: activeStrategyIds } = await supabase
        .from('strategies')
        .select('id')
        .eq('is_active', true)
        .eq('auto_trade_enabled', true)

      if (!activeStrategyIds || activeStrategyIds.length === 0) {
        setPendingSellStocks([])
        return
      }

      const strategyIds = activeStrategyIds.map(s => s.id)

      // 매도 조건 근접도 80% 이상인 보유 종목 조회 (최근 1시간 이내)
      const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString()

      const { data, error } = await supabase
        .from('strategy_monitoring')
        .select('*')
        .in('strategy_id', strategyIds)
        .eq('is_held', true)  // ⭐ 보유 종목만!
        .gte('exit_condition_match_score', 80)
        .lt('exit_condition_match_score', 100)  // 100점은 이미 신호 발생
        .gte('updated_at', oneHourAgo)
        .order('exit_condition_match_score', { ascending: false })
        .limit(50)

      if (error) throw error
      setPendingSellStocks(data || [])
    } catch (error) {
      console.error('매도 대기 종목 조회 실패:', error)
    }
  }

  const fetchWorkflowStats = async () => {
    try {
      const now = new Date()

      // 1분 내 신호 개수
      const { count: count1min } = await supabase
        .from('trading_signals')
        .select('*', { count: 'exact', head: true })
        .gte('created_at', new Date(now.getTime() - 60000).toISOString())

      // 5분 내 신호 개수
      const { count: count5min } = await supabase
        .from('trading_signals')
        .select('*', { count: 'exact', head: true })
        .gte('created_at', new Date(now.getTime() - 300000).toISOString())

      // 전체 신호 개수 (총 실행 횟수)
      const { count: totalCount } = await supabase
        .from('trading_signals')
        .select('*', { count: 'exact', head: true })

      // 성공 신호 개수 (signal_type이 BUY 또는 SELL인 경우)
      const { count: successCount } = await supabase
        .from('trading_signals')
        .select('*', { count: 'exact', head: true })
        .in('signal_type', ['BUY', 'SELL'])

      const successRate = totalCount && totalCount > 0
        ? Math.round((successCount || 0) / totalCount * 100)
        : 0

      setWorkflowStats({
        last1min: count1min || 0,
        last5min: count5min || 0,
        successRate,
        totalExecutions: totalCount || 0
      })
    } catch (error) {
      console.error('워크플로우 통계 로드 실패:', error)
    }
  }

  const fetchWorkflowData = async () => {
    try {
      setWorkflowLoading(true)
      setWorkflowError(null)
      const data = await n8nClient.getAllWorkflowsSummary(20)
      setWorkflows(data)
      setLastWorkflowUpdate(new Date())
    } catch (err) {
      console.error('워크플로우 데이터 로드 실패:', err)
      setWorkflowError(String(err))
    } finally {
      setWorkflowLoading(false)
    }
  }

  const handleAccordionChange = (workflowId: string) => (_: any, isExpanded: boolean) => {
    setExpandedWorkflow(isExpanded ? workflowId : false)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success'
      case 'error':
        return 'error'
      case 'running':
        return 'info'
      case 'waiting':
        return 'warning'
      default:
        return 'default'
    }
  }

  const getStatusIcon = (status: string): React.ReactElement | undefined => {
    switch (status) {
      case 'success':
        return <CheckCircle fontSize="small" />
      case 'error':
        return <Error fontSize="small" />
      case 'running':
        return <PlayArrow fontSize="small" />
      case 'waiting':
        return <Schedule fontSize="small" />
      default:
        return undefined
    }
  }

  const formatDuration = (ms?: number) => {
    if (!ms) return '-'
    const seconds = Math.floor(ms / 1000)
    if (seconds < 60) return `${seconds}초`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}분 ${remainingSeconds}초`
  }

  const formatTime = (dateStr?: string) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleString('ko-KR', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  const filteredSignals = signals.filter(signal => {
    if (filterStrategy !== 'all' && signal.strategy_id !== filterStrategy) return false
    if (filterType !== 'all' && signal.signal_type !== filterType) return false
    return true
  })

  // 페이지네이션 계산
  const totalPages = Math.ceil(filteredSignals.length / signalsPerPage)
  const startIndex = (signalPage - 1) * signalsPerPage
  const endIndex = startIndex + signalsPerPage
  const paginatedSignals = filteredSignals.slice(startIndex, endIndex)

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setSignalPage(value)
  }

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

  const formatTimeAgo = (dateString: string) => {
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

  // 표시할 종목 데이터 (최근 10개 또는 전체)
  const displayedStocks = showAllStocks ? marketData : marketData.slice(0, 10)

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
      {/* n8n 워크플로우 실행 내역 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Stack direction="row" spacing={1} alignItems="center">
                <Bolt color="primary" />
                <Typography variant="h5" gutterBottom>
                  n8n 워크플로우 실행 내역
                </Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary">
                자동매매 워크플로우의 실행 기록 (최근 20건)
              </Typography>
            </Box>
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip
                label={marketStatus}
                color={isMarketOpen() ? 'success' : 'default'}
                size="small"
                icon={isMarketOpen() ? <CheckCircle /> : <Schedule />}
              />
              {lastWorkflowUpdate && (
                <Chip
                  icon={<Update />}
                  label={lastWorkflowUpdate.toLocaleTimeString()}
                  size="small"
                  variant="outlined"
                />
              )}
              <IconButton onClick={fetchWorkflowData} disabled={workflowLoading}>
                <Refresh />
              </IconButton>
            </Stack>
          </Stack>

          {/* 시장 상태 알림 */}
          {!isMarketOpen() && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                {marketStatus}<br />
                주식시장 휴장 중 - 실시간 업데이트 일시정지
              </Typography>
            </Alert>
          )}

          {workflowLoading && <LinearProgress sx={{ mb: 2 }} />}

          {workflowError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              n8n 연결 실패: {workflowError}
            </Alert>
          )}

          {/* 요약 통계 */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper
                sx={{
                  p: 2,
                  textAlign: 'center',
                  bgcolor: 'var(--ipc-success-bg)',
                  border: '1px solid var(--ipc-success-bg)',
                  borderRadius: 'var(--ipc-radius-sm)'
                }}
              >
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  최근 1분 성공
                </Typography>
                <Typography variant="h3" color="success.main" fontWeight="bold">
                  {workflows.filter(w => {
                    const stoppedAt = w.lastExecution?.stoppedAt
                    if (!stoppedAt || !w.lastExecution) return false
                    const diff = Date.now() - new Date(stoppedAt).getTime()
                    return diff < 60000 && w.lastExecution.status === 'success'
                  }).length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  건
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Paper
                sx={{
                  p: 2,
                  textAlign: 'center',
                  bgcolor: 'var(--ipc-danger-bg)',
                  border: '1px solid var(--ipc-danger-bg)',
                  borderRadius: 'var(--ipc-radius-sm)'
                }}
              >
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  최근 5분 실패
                </Typography>
                <Typography variant="h3" color="error.main" fontWeight="bold">
                  {workflows.filter(w => {
                    const stoppedAt = w.lastExecution?.stoppedAt
                    if (!stoppedAt || !w.lastExecution) return false
                    const diff = Date.now() - new Date(stoppedAt).getTime()
                    return diff < 300000 && w.lastExecution.status === 'error'
                  }).length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  건
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Paper
                sx={{
                  p: 2,
                  textAlign: 'center',
                  bgcolor: 'var(--ipc-info-bg)',
                  border: '1px solid var(--ipc-info-bg)',
                  borderRadius: 'var(--ipc-radius-sm)'
                }}
              >
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  평균 성공률
                </Typography>
                <Typography variant="h3" color="primary.main" fontWeight="bold">
                  {workflows.length > 0
                    ? Math.round((workflows.filter(w => w.lastExecution?.status === 'success').length / workflows.length) * 100)
                    : 0}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  최근 20건 기준
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Paper
                sx={{
                  p: 2,
                  textAlign: 'center',
                  bgcolor: 'var(--ipc-primary-light)',
                  border: '1px solid var(--ipc-primary-light)',
                  borderRadius: 'var(--ipc-radius-sm)'
                }}
              >
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  총 실행 횟수
                </Typography>
                <Typography variant="h3" sx={{ color: '#9c27b0' }} fontWeight="bold">
                  {workflows.length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  건 (최근 20건)
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          {/* 워크플로우 아코디언 리스트 */}
          {workflows.length === 0 && !workflowLoading ? (
            <Alert severity="info">
              실행된 워크플로우가 없습니다.
            </Alert>
          ) : (
            <Box sx={{ maxHeight: 600, overflow: 'auto' }}>
              {workflows.map((workflow) => (
                <Accordion
                  key={workflow.lastExecution?.id || workflow.workflowName}
                  expanded={expandedWorkflow === workflow.lastExecution?.id}
                  onChange={handleAccordionChange(workflow.lastExecution?.id || '')}
                  sx={{ mb: 1 }}
                >
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Stack direction="row" spacing={2} alignItems="center" sx={{ width: '100%' }}>
                      <Chip
                        icon={getStatusIcon(workflow.lastExecution?.status || 'waiting')}
                        label={workflow.lastExecution?.status || 'waiting'}
                        color={getStatusColor(workflow.lastExecution?.status || 'waiting') as any}
                        size="small"
                      />
                      <Typography variant="subtitle1" fontWeight="bold" sx={{ flex: 1 }}>
                        {workflow.workflowName}
                      </Typography>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Timer fontSize="small" color="action" />
                        <Typography variant="caption" color="text.secondary">
                          {formatDuration(workflow.lastExecution?.duration)}
                        </Typography>
                      </Stack>
                      <Typography variant="caption" color="text.secondary">
                        {formatTime(workflow.lastExecution?.startedAt)}
                      </Typography>
                    </Stack>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        실행 정보
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="caption" color="text.secondary">
                            실행 ID
                          </Typography>
                          <Typography variant="body2" fontFamily="monospace">
                            {workflow.lastExecution?.id || '-'}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="caption" color="text.secondary">
                            소요 시간
                          </Typography>
                          <Typography variant="body2">
                            {formatDuration(workflow.lastExecution?.duration)}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="caption" color="text.secondary">
                            시작 시간
                          </Typography>
                          <Typography variant="body2">
                            {formatTime(workflow.lastExecution?.startedAt)}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="caption" color="text.secondary">
                            종료 시간
                          </Typography>
                          <Typography variant="body2">
                            {formatTime(workflow.lastExecution?.stoppedAt)}
                          </Typography>
                        </Grid>
                      </Grid>
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="subtitle2" gutterBottom>
                      노드 실행 상세
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>노드명</TableCell>
                            <TableCell align="center">유형</TableCell>
                            <TableCell align="center">상태</TableCell>
                            <TableCell align="center">처리 항목</TableCell>
                            <TableCell align="center">실행 시간</TableCell>
                            <TableCell align="center">마지막 실행</TableCell>
                            <TableCell>에러</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {workflow.nodeExecutions && workflow.nodeExecutions.length > 0 ? (
                            workflow.nodeExecutions.map((node, idx) => (
                              <TableRow key={idx} hover>
                                <TableCell>
                                  <Typography variant="body2" fontWeight="medium">
                                    {node.nodeName}
                                  </Typography>
                                </TableCell>
                                <TableCell align="center">
                                  <Chip label={node.nodeType} size="small" variant="outlined" />
                                </TableCell>
                                <TableCell align="center">
                                  <Chip
                                    icon={getStatusIcon(node.status)}
                                    label={node.status}
                                    color={getStatusColor(node.status) as any}
                                    size="small"
                                  />
                                </TableCell>
                                <TableCell align="center">
                                  {node.itemsProcessed ?? '-'}
                                </TableCell>
                                <TableCell align="center">
                                  {formatDuration(node.executionTime)}
                                </TableCell>
                                <TableCell align="center">
                                  {formatTime(node.lastExecutedAt)}
                                </TableCell>
                                <TableCell>
                                  {node.error ? (
                                    <Tooltip title={node.error}>
                                      <Chip
                                        label="에러 발생"
                                        color="error"
                                        size="small"
                                        icon={<Error />}
                                      />
                                    </Tooltip>
                                  ) : (
                                    '-'
                                  )}
                                </TableCell>
                              </TableRow>
                            ))
                          ) : (
                            <TableRow>
                              <TableCell colSpan={7} align="center">
                                <Typography variant="body2" color="text.secondary">
                                  노드 실행 정보 없음
                                </Typography>
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}

          <Alert severity="info" sx={{ mt: 2 }}>
            워크플로우 실행 내역은 30초마다 자동으로 갱신됩니다.
          </Alert>
        </CardContent>
      </Card>

      {/* 시장 모니터링 섹션 */}
      <Card sx={{ mb: 3, border: '1px solid black' }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Stack direction="row" spacing={1} alignItems="center">
                <ShowChart color="action" />
                <Typography variant="h5" color="text.primary" gutterBottom>
                  실시간 시장 모니터링
                </Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary">
                n8n 워크플로우가 1분마다 수집하는 주요 종목 시세
              </Typography>
            </Box>
            <Stack direction="row" spacing={1} alignItems="center">
              {lastMarketUpdate && (
                <Chip
                  icon={<Update />}
                  label={lastMarketUpdate.toLocaleTimeString()}
                  size="small"
                  sx={{ bgcolor: 'action.selected', color: 'text.primary' }}
                />
              )}
              <IconButton onClick={fetchMarketData} color="primary">
                <Refresh />
              </IconButton>
            </Stack>
          </Stack>

          {marketLoading && <LinearProgress sx={{ mb: 2 }} />}

          {/* 시장 통계 카드 */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={4}>
              <Paper
                sx={{
                  p: 2,
                  textAlign: 'center',
                  bgcolor: 'var(--ipc-bg-subtle)',
                  border: '1px solid var(--ipc-border)'
                }}
              >
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  상승 종목
                </Typography>
                <Typography variant="h3" color="error.main" fontWeight="bold">
                  {marketStats.rising}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  개
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} sm={4}>
              <Paper
                sx={{
                  p: 2,
                  textAlign: 'center',
                  bgcolor: 'var(--ipc-bg-subtle)',
                  border: '1px solid var(--ipc-border)'
                }}
              >
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  하락 종목
                </Typography>
                <Typography variant="h3" color="primary.main" fontWeight="bold">
                  {marketStats.falling}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  개
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} sm={4}>
              <Paper
                sx={{
                  p: 2,
                  textAlign: 'center',
                  bgcolor: 'var(--ipc-bg-subtle)',
                  border: '1px solid var(--ipc-border)'
                }}
              >
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  보합 종목
                </Typography>
                <Typography variant="h3" color="text.secondary" fontWeight="bold">
                  {marketStats.neutral}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  개
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          {marketData.length === 0 && !marketLoading ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              자동매매 전략의 투자유니버스 종목 데이터가 없습니다.
            </Alert>
          ) : (
            <>
              {/* 시장 데이터 테이블 */}
              <Box>
                <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="subtitle1" fontWeight="medium" color="text.primary">
                    최근 업데이트 종목 ({displayedStocks.length}개)
                  </Typography>
                  {marketData.length > 10 && (
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => setShowAllStocks(!showAllStocks)}
                      color="primary"
                    >
                      {showAllStocks ? '접기 ▲' : `전체 보기 (${marketData.length}개) ▼`}
                    </Button>
                  )}
                </Stack>

                <TableContainer component={Paper} sx={{ maxHeight: showAllStocks ? 600 : 400 }}>
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
                      {displayedStocks.map((item) => (
                        <TableRow key={item.stock_code} hover>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {item.stock_name || item.stock_code}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
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
              </Box>
            </>
          )}
        </CardContent>
      </Card>

      <Divider sx={{ my: 3 }} />

      {/* 매수 대기 종목 섹션 */}
      {pendingStocks.length > 0 && (
        <Card sx={{ mb: 3, border: '1px solid black' }}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
              <Box>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Timer color="action" />
                  <Typography variant="h5" color="text.primary" gutterBottom>
                    매수 대기 종목
                  </Typography>
                </Stack>
                <Typography variant="body2" color="text.secondary">
                  조건 근접도 80% 이상 (곧 매수 신호 발생 가능)
                </Typography>
              </Box>
              <Chip
                label={`${pendingStocks.length}개 종목`}
                sx={{
                  bgcolor: 'warning.light',
                  color: 'warning.contrastText',
                  fontWeight: 'bold'
                }}
              />
            </Stack>

            <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>종목</TableCell>
                    <TableCell align="right">현재가</TableCell>
                    <TableCell align="right">조건 충족도</TableCell>
                    <TableCell align="right">업데이트</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {pendingStocks.map((stock) => {
                    const strategy = strategies.find(s => s.id === stock.strategy_id)
                    return (
                      <TableRow key={`${stock.strategy_id}-${stock.stock_code}`} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {stock.stock_name || stock.stock_code}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {stock.stock_code} {strategy && `• ${strategy.name}`}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="bold">
                            {stock.current_price?.toLocaleString() || '-'}원
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end" alignItems="center">
                            <LinearProgress
                              variant="determinate"
                              value={stock.condition_match_score}
                              sx={{
                                width: 60,
                                height: 8,
                                borderRadius: 1,
                                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: stock.condition_match_score >= 95 ? '#f44336' :
                                    stock.condition_match_score >= 90 ? '#ff9800' : '#4caf50'
                                }
                              }}
                            />
                            <Typography variant="body2" fontWeight="bold" color="error.main">
                              {stock.condition_match_score.toFixed(0)}%
                            </Typography>
                          </Stack>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="caption" color="text.secondary">
                            {new Date(stock.updated_at).toLocaleTimeString('ko-KR')}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* 매도 대기 종목 섹션 */}
      {pendingSellStocks.length > 0 && (
        <Card sx={{ mb: 3, border: '1px solid black' }}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
              <Box>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Timer color="action" />
                  <Typography variant="h5" color="text.primary" gutterBottom>
                    매도 대기 종목
                  </Typography>
                </Stack>
                <Typography variant="body2" color="text.secondary">
                  보유 종목의 매도 조건 근접도 80% 이상 (곧 매도 신호 발생 가능)
                </Typography>
              </Box>
              <Chip
                label={`${pendingSellStocks.length}개 보유종목`}
                sx={{
                  bgcolor: 'info.light',
                  color: 'info.contrastText',
                  fontWeight: 'bold'
                }}
              />
            </Stack>

            <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>종목</TableCell>
                    <TableCell align="right">현재가</TableCell>
                    <TableCell align="right">매도 조건 충족도</TableCell>
                    <TableCell align="right">업데이트</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {pendingSellStocks.map((stock) => {
                    const strategy = strategies.find(s => s.id === stock.strategy_id)
                    return (
                      <TableRow key={`sell-${stock.strategy_id}-${stock.stock_code}`} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {stock.stock_name || stock.stock_code}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {stock.stock_code} {strategy && `• ${strategy.name}`}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="bold">
                            {stock.current_price?.toLocaleString() || '-'}원
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end" alignItems="center">
                            <LinearProgress
                              variant="determinate"
                              value={stock.exit_condition_match_score}
                              sx={{
                                width: 60,
                                height: 8,
                                borderRadius: 1,
                                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: stock.exit_condition_match_score >= 95 ? '#f44336' :
                                    stock.exit_condition_match_score >= 90 ? '#ff9800' : '#2196f3'
                                }
                              }}
                            />
                            <Typography variant="body2" fontWeight="bold" color="primary.main">
                              {stock.exit_condition_match_score.toFixed(0)}%
                            </Typography>
                          </Stack>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="caption" color="text.secondary">
                            {new Date(stock.updated_at).toLocaleTimeString('ko-KR')}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* 매매 신호 섹션 */}
      <Card sx={{ mb: 3, border: '1px solid black' }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Stack direction="row" spacing={1} alignItems="center">
                <Bolt color="action" />
                <Typography variant="h5" color="text.primary" gutterBottom>
                  실시간 매매 신호
                </Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary">
                전략별 매수/매도 신호를 실시간으로 모니터링합니다
              </Typography>
            </Box>
            <Stack direction="row" spacing={1}>
              <IconButton
                onClick={() => setNotifications(!notifications)}
                color="primary"
              >
                {notifications ? <NotificationsActive /> : <NotificationsOff />}
              </IconButton>
              <IconButton onClick={fetchSignals} color="primary">
                <Refresh />
              </IconButton>
            </Stack>
          </Stack>

          <Stack direction="row" spacing={2}>
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>전략 선택</InputLabel>
              <Select
                value={filterStrategy}
                onChange={(e) => setFilterStrategy(e.target.value)}
                label="전략 선택"
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
              <InputLabel>신호 타입</InputLabel>
              <Select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                label="신호 타입"
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
              {paginatedSignals.map((signal) => {
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
                          {formatTimeAgo(signal.created_at)}
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

      {/* 페이지네이션 */}
      {filteredSignals.length > signalsPerPage && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <Pagination
            count={totalPages}
            page={signalPage}
            onChange={handlePageChange}
            color="primary"
            showFirstButton
            showLastButton
          />
        </Box>
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
