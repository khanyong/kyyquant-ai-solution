import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemButton,
  Typography,
  Box,
  Chip,
  Stack,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
  Alert,
  CircularProgress,
  Divider,
  Paper,
  Avatar,
  Tabs,
  Tab,
  Badge,
  FormControl,
  Select,
  MenuItem,
  InputLabel
} from '@mui/material'
import {
  ShowChart,
  TrendingUp,
  TrendingDown,
  Business,
  CalendarToday,
  Speed,
  Search,
  FilterList,
  Info,
  Delete,
  ContentCopy,
  Visibility,
  Star,
  StarBorder,
  AccessTime,
  AccountBalance,
  QueryStats,
  Assessment,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Public,
  Lock
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'
import { authService } from '../services/auth'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'

interface StrategyStats {
  executionCount: number
  averageReturn: number
  winRate: number
  includedStocks: number
  lastExecuted: string | null
  backtestResults?: {
    totalReturn: number
    sharpeRatio: number
    maxDrawdown: number
  }
}

interface SavedStrategy {
  id: string
  name: string
  description: string
  strategy_data: any
  created_at: string
  updated_at: string
  is_public?: boolean
  user_id?: string
  stats?: StrategyStats
  tags?: string[]
  // Legacy fields for backward compatibility
  indicators?: any
  entry_conditions?: any
  exit_conditions?: any
  risk_management?: any
  config?: any
  parameters?: any
  isFavorite?: boolean
  // Extracted fields (populated after processing)
  buyConditions?: any[]
  sellConditions?: any[]
  riskManagement?: any
}

interface StrategyLoaderProps {
  open: boolean
  onClose: () => void
  onLoad: (strategy: any) => void
  currentUserId?: string
}

const StrategyLoader: React.FC<StrategyLoaderProps> = ({
  open,
  onClose,
  onLoad,
  currentUserId
}) => {
  const [strategies, setStrategies] = useState<SavedStrategy[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTab, setSelectedTab] = useState(0)
  const [selectedStrategy, setSelectedStrategy] = useState<SavedStrategy | null>(null)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [strategyToDelete, setStrategyToDelete] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<'name' | 'created_at' | 'updated_at'>('updated_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  useEffect(() => {
    if (open) {
      loadStrategies()
    }
  }, [open, selectedTab, sortBy, sortOrder])

  const loadStrategies = async () => {
    setLoading(true)
    try {
      const user = await authService.getCurrentUser()
      if (!user) {
        console.warn('User not logged in')
        setLoading(false)
        return
      }

      // 기본 쿼리 - 모든 전략 가져오기
      let query = supabase
        .from('strategies')
        .select('*')

      // 탭에 따라 필터링
      if (selectedTab === 0) {
        // 내 전략만
        query = query.eq('user_id', user.id)
      } else if (selectedTab === 1) {
        // 공유된 전략 (모든 사용자)
        query = query.eq('is_public', true)
      } else if (selectedTab === 2) {
        // 즐겨찾기 (TODO: 차후 구현)
        query = query.eq('user_id', user.id).eq('is_favorite', true)
      } else if (selectedTab === 3) {
        // 모든 전략 (개발용)
        // 필터링 없음 - 모든 전략 표시
      }

      // 정렬 적용
      query = query.order(sortBy, { ascending: sortOrder === 'asc' })

      const { data, error } = await query

      if (error) throw error

      // 각 전략에 대한 통계 정보 계산
      const strategiesWithStats = await Promise.all(
        (data || []).map(async (strategy) => {
          const stats = await calculateStrategyStats(strategy)
          return {
            ...strategy,
            stats
          }
        })
      )

      setStrategies(strategiesWithStats)
    } catch (error) {
      console.error('Failed to load strategies:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateStrategyStats = async (strategy: any): Promise<StrategyStats> => {
    // 백테스트 결과 조회
    const { data: backtestData } = await supabase
      .from('backtest_results')
      .select('*')
      .eq('strategy_id', strategy.id)
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    // 전략 실행 기록 조회
    const { data: executionData, count } = await supabase
      .from('strategy_executions')
      .select('*', { count: 'exact' })
      .eq('strategy_id', strategy.id)

    // 포함된 종목 수 계산
    let includedStocks = 0
    if (strategy.strategy_data?.buyConditions) {
      const stockSymbols = new Set()
      strategy.strategy_data.buyConditions.forEach((condition: any) => {
        if (condition.stocks) {
          condition.stocks.forEach((stock: string) => stockSymbols.add(stock))
        }
      })
      includedStocks = stockSymbols.size
    }

    // 승률 및 평균 수익률 계산
    let winRate = 0
    let averageReturn = 0
    if (backtestData?.results) {
      const trades = backtestData.results.trades || []
      const wins = trades.filter((t: any) => t.return > 0).length
      winRate = trades.length > 0 ? (wins / trades.length) * 100 : 0
      averageReturn = trades.reduce((sum: number, t: any) => sum + t.return, 0) / (trades.length || 1)
    }

    return {
      executionCount: count || 0,
      averageReturn: averageReturn,
      winRate: winRate,
      includedStocks: includedStocks,
      lastExecuted: executionData?.[0]?.created_at || null,
      backtestResults: backtestData ? {
        totalReturn: backtestData.total_return_rate || 0,
        sharpeRatio: backtestData.sharpe_ratio || 0,
        maxDrawdown: backtestData.max_drawdown || 0
      } : undefined
    }
  }

  const handleStrategySelect = (strategy: SavedStrategy) => {
    console.log('=== Strategy selected ===')
    console.log('Raw strategy:', strategy)
    console.log('strategy_data:', strategy.strategy_data)
    console.log('config:', strategy.config)
    console.log('entry_conditions:', strategy.entry_conditions)
    console.log('exit_conditions:', strategy.exit_conditions)

    let extractedStrategy: any = { ...strategy }

    // 1순위: strategy_data에서 직접 추출
    if (strategy.strategy_data) {
      console.log('📦 Using strategy_data')
      const sd = strategy.strategy_data

      extractedStrategy = {
        ...strategy,
        buyConditions: sd.buyConditions || sd.entry_conditions?.buy || [],
        sellConditions: sd.sellConditions || sd.exit_conditions?.sell || [],
        indicators: sd.indicators || [],
        riskManagement: sd.riskManagement || {
          stopLoss: sd.stopLoss,
          takeProfit: sd.takeProfit,
          trailingStop: sd.trailingStop,
          trailingStopPercent: sd.trailingStopPercent,
          positionSize: sd.positionSize,
          maxPositions: sd.maxPositions
        }
      }
    }

    // 2순위: config 객체에서 추출
    if (strategy.config) {
      console.log('⚙️ Checking config object')
      const cfg = strategy.config

      extractedStrategy = {
        ...extractedStrategy,
        buyConditions: extractedStrategy.buyConditions?.length > 0
          ? extractedStrategy.buyConditions
          : (cfg.buyConditions || strategy.entry_conditions?.buy || []),
        sellConditions: extractedStrategy.sellConditions?.length > 0
          ? extractedStrategy.sellConditions
          : (cfg.sellConditions || strategy.exit_conditions?.sell || []),
        indicators: extractedStrategy.indicators?.length > 0
          ? extractedStrategy.indicators
          : (cfg.indicators || strategy.indicators?.list || []),
        riskManagement: extractedStrategy.riskManagement || strategy.risk_management || {
          stopLoss: cfg.stopLoss,
          takeProfit: cfg.takeProfit,
          trailingStop: cfg.trailingStop,
          trailingStopPercent: cfg.trailingStopPercent,
          positionSize: cfg.positionSize,
          maxPositions: cfg.maxPositions
        }
      }
    }

    // 3순위: parameters (레거시)
    if (strategy.parameters && (!extractedStrategy.buyConditions?.length && !extractedStrategy.sellConditions?.length)) {
      console.log('🗂️ Using parameters (legacy)')
      const params = strategy.parameters

      extractedStrategy = {
        ...extractedStrategy,
        buyConditions: params.buyConditions || [],
        sellConditions: params.sellConditions || [],
        indicators: params.indicators || [],
        riskManagement: {
          stopLoss: params.stopLoss,
          takeProfit: params.takeProfit,
          trailingStop: params.trailingStop,
          trailingStopPercent: params.trailingStopPercent
        }
      }
    }

    // 4순위: 최상위 레벨 필드 (entry_conditions, exit_conditions)
    if (!extractedStrategy.buyConditions?.length && strategy.entry_conditions?.buy) {
      console.log('📋 Using entry_conditions.buy')
      extractedStrategy.buyConditions = strategy.entry_conditions.buy
    }

    if (!extractedStrategy.sellConditions?.length && strategy.exit_conditions?.sell) {
      console.log('📋 Using exit_conditions.sell')
      extractedStrategy.sellConditions = strategy.exit_conditions.sell
    }

    console.log('✨ Final extracted strategy:', {
      name: extractedStrategy.name,
      buyConditionsCount: extractedStrategy.buyConditions?.length,
      sellConditionsCount: extractedStrategy.sellConditions?.length,
      buyConditions: extractedStrategy.buyConditions,
      sellConditions: extractedStrategy.sellConditions,
      riskManagement: extractedStrategy.riskManagement
    })

    setSelectedStrategy(extractedStrategy)
  }

  const handleLoad = () => {
    console.log('handleLoad called, selectedStrategy:', selectedStrategy)
    console.log('onLoad function:', onLoad)
    console.log('onClose function:', onClose)

    if (selectedStrategy) {
      // handleStrategySelect에서 이미 데이터 추출되어 있으므로 그대로 사용
      console.log('✨ Loading strategy data:', {
        name: selectedStrategy.name,
        buyConditionsCount: selectedStrategy.buyConditions?.length,
        sellConditionsCount: selectedStrategy.sellConditions?.length,
        riskManagement: selectedStrategy.riskManagement
      })

      onLoad(selectedStrategy)
      onClose()
    } else {
      console.warn('No strategy selected')
      alert('전략을 선택해주세요.')
    }
  }

  const handleDelete = async () => {
    if (!strategyToDelete) return

    try {
      const { error } = await supabase
        .from('strategies')
        .delete()
        .eq('id', strategyToDelete)

      if (error) throw error

      setStrategies(strategies.filter(s => s.id !== strategyToDelete))
      setDeleteConfirmOpen(false)
      setStrategyToDelete(null)
      if (selectedStrategy?.id === strategyToDelete) {
        setSelectedStrategy(null)
      }
    } catch (error) {
      console.error('Failed to delete strategy:', error)
    }
  }

  const handleDuplicate = async (strategy: SavedStrategy) => {
    try {
      const user = await authService.getCurrentUser()
      if (!user) return

      const newStrategy = {
        ...strategy.strategy_data,
        name: `${strategy.name} (복사본)`,
        description: `${strategy.description} - 복사본`
      }

      const { error } = await supabase
        .from('strategies')
        .insert({
          name: newStrategy.name,
          description: newStrategy.description,
          strategy_data: newStrategy,
          user_id: user.id,
          is_public: false
        })

      if (error) throw error

      loadStrategies()
    } catch (error) {
      console.error('Failed to duplicate strategy:', error)
    }
  }

  const getStatusChip = (stats?: StrategyStats) => {
    if (!stats?.backtestResults) {
      return <Chip label="미검증" size="small" color="default" />
    }

    const { totalReturn } = stats.backtestResults
    if (totalReturn > 10) {
      return <Chip label="우수" size="small" color="success" icon={<CheckCircle />} />
    } else if (totalReturn > 0) {
      return <Chip label="양호" size="small" color="info" icon={<Info />} />
    } else {
      return <Chip label="주의" size="small" color="warning" icon={<Warning />} />
    }
  }

  // 전략 조건 조합 특성 요약
  const getStrategyConditionSummary = (strategy: SavedStrategy) => {
    const conditions: string[] = []
    const strategyData = strategy.strategy_data
    
    if (!strategyData) return '조건 없음'
    
    // 지표 매핑
    const indicatorMap: { [key: string]: string } = {
      'RSI': 'RSI',
      'MACD': 'MACD',
      'MA': '이평선',
      'SMA': '단순이평',
      'EMA': '지수이평',
      'VOLUME': '거래량',
      'BB': '볼린저',
      'BOLLINGER': '볼린저',
      'STOCHASTIC': '스토캐스틱',
      'CCI': 'CCI',
      'DMI': 'DMI',
      'OBV': 'OBV',
      'VWAP': 'VWAP'
    }
    
    const getIndicatorName = (indicator: string) => {
      const upperIndicator = indicator.toUpperCase().split('_')[0]
      return indicatorMap[upperIndicator] || upperIndicator
    }
    
    // 지표 기반 조건 확인
    if (strategyData.indicators?.length > 0) {
      const indicatorNames = new Set<string>()
      strategyData.indicators.forEach((ind: any) => {
        if (typeof ind === 'string') {
          indicatorNames.add(getIndicatorName(ind))
        } else if (ind.name) {
          indicatorNames.add(getIndicatorName(ind.name))
        } else if (ind.type) {
          indicatorNames.add(getIndicatorName(ind.type))
        }
      })
      if (indicatorNames.size > 0) {
        const names = Array.from(indicatorNames)
        conditions.push(`📊 ${names.slice(0, 3).join('+')}${names.length > 3 ? ` 외 ${names.length - 3}개` : ''}`)
      }
    }
    
    // 매수 조건 확인
    if (strategyData.buyConditions?.length > 0) {
      const buyIndicators = new Set<string>()
      let hasComplex = false
      
      strategyData.buyConditions.forEach((cond: any) => {
        if (cond.indicator) {
          buyIndicators.add(getIndicatorName(cond.indicator))
        }
        if (cond.conditions?.length > 1) {
          hasComplex = true
        }
      })
      
      if (buyIndicators.size > 0) {
        const buyStr = Array.from(buyIndicators).slice(0, 2).join('+')
        conditions.push(`📈 매수: ${buyStr}${hasComplex ? '(복합)' : ''}`)
      }
    }
    
    // 매도 조건 확인
    if (strategyData.sellConditions?.length > 0) {
      const sellIndicators = new Set<string>()
      
      strategyData.sellConditions.forEach((cond: any) => {
        if (cond.indicator) {
          sellIndicators.add(getIndicatorName(cond.indicator))
        }
      })
      
      if (sellIndicators.size > 0) {
        conditions.push(`📉 매도: ${Array.from(sellIndicators).slice(0, 2).join('+')}`)
      }
    }
    
    // 단계별 전략 확인
    if (strategyData.useStageBasedStrategy) {
      const buyStages = strategyData.buyStageStrategy
      const stageIndicators: string[] = []
      
      if (buyStages?.stage1?.indicators?.length > 0) {
        stageIndicators.push(getIndicatorName(buyStages.stage1.indicators[0]))
      }
      if (buyStages?.stage2?.indicators?.length > 0) {
        stageIndicators.push(getIndicatorName(buyStages.stage2.indicators[0]))
      }
      if (buyStages?.stage3?.indicators?.length > 0) {
        stageIndicators.push(getIndicatorName(buyStages.stage3.indicators[0]))
      }
      
      if (stageIndicators.length > 0) {
        conditions.push(`🎯 ${stageIndicators.length}단계: ${stageIndicators.join('→')}`)
      }
    }
    
    // 리스크 관리 설정
    const riskConditions: string[] = []
    if (strategyData.riskManagement) {
      const rm = strategyData.riskManagement
      if (rm.stopLoss && rm.stopLoss !== 0) {
        riskConditions.push(`손절${Math.abs(rm.stopLoss)}%`)
      }
      if (rm.takeProfit && rm.takeProfit !== 0) {
        riskConditions.push(`익절${rm.takeProfit}%`)
      }
      if (rm.trailingStop) {
        riskConditions.push('추적손절')
      }
    }
    
    if (riskConditions.length > 0) {
      conditions.push(`⚠️ ${riskConditions.join('/')}`)
    }
    
    return conditions.length > 0 ? conditions.join(' ') : '조건 미설정'
  }

  // 필터링 및 정렬 적용
  const filteredStrategies = strategies
    .filter(strategy =>
      strategy.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      strategy.description?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      let compareValue = 0
      
      switch (sortBy) {
        case 'name':
          compareValue = a.name.localeCompare(b.name)
          break
        case 'created_at':
          compareValue = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          break
        case 'updated_at':
          compareValue = new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime()
          break
      }
      
      return sortOrder === 'asc' ? compareValue : -compareValue
    })

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <DialogTitle>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">전략 불러오기</Typography>
            <Stack direction="row" spacing={2}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>정렬</InputLabel>
                <Select
                  value={sortBy}
                  label="정렬"
                  onChange={(e) => {
                    setSortBy(e.target.value as any)
                  }}
                >
                  <MenuItem value="name">이름</MenuItem>
                  <MenuItem value="created_at">생성일</MenuItem>
                  <MenuItem value="updated_at">수정일</MenuItem>
                </Select>
              </FormControl>
              <FormControl size="small" sx={{ minWidth: 100 }}>
                <Select
                  value={sortOrder}
                  onChange={(e) => {
                    setSortOrder(e.target.value as any)
                  }}
                >
                  <MenuItem value="asc">오름차순</MenuItem>
                  <MenuItem value="desc">내림차순</MenuItem>
                </Select>
              </FormControl>
              <TextField
                size="small"
                placeholder="전략 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  )
                }}
                sx={{ width: 250 }}
              />
            </Stack>
          </Stack>
        </DialogTitle>

        <DialogContent dividers>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs value={selectedTab} onChange={(_, v) => setSelectedTab(v)}>
              <Tab label="내 전략" />
              <Tab label="공유된 전략" />
              <Tab label="즐겨찾기" icon={<Star />} iconPosition="end" />
              <Tab 
                label={
                  <Box display="flex" alignItems="center" gap={1}>
                    <span>모든 전략</span>
                    <Chip label="임시" size="small" color="warning" />
                  </Box>
                } 
              />
            </Tabs>
          </Box>

          {selectedTab === 3 && (
            <Alert severity="warning" icon={<Warning />} sx={{ mb: 2 }}>
              <Typography variant="subtitle2">개발 모드 전용</Typography>
              <Typography variant="body2">
                이 탭은 개발 중에만 사용되며, 모든 사용자의 전략을 볼 수 있습니다.
                정식 서비스에서는 제거될 예정입니다.
              </Typography>
            </Alert>
          )}

          {loading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : filteredStrategies.length === 0 ? (
            <Alert severity="info">
              {searchTerm ? 
                `"${searchTerm}"에 대한 검색 결과가 없습니다.` : 
                selectedTab === 0 ? '아직 저장한 전략이 없습니다. 새로운 전략을 만들어보세요!' :
                selectedTab === 1 ? '공유된 전략이 없습니다.' :
                selectedTab === 2 ? '즐겨찾기한 전략이 없습니다.' :
                '전략이 없습니다.'
              }
            </Alert>
          ) : (
            <Box mb={2}>
              <Typography variant="body2" color="text.secondary">
                총 {filteredStrategies.length}개의 전략
                {selectedTab === 1 && ' (공유됨)'}
                {selectedTab === 3 && ' (전체)'}
              </Typography>
            </Box>
          )}
          {!loading && filteredStrategies.length > 0 && (
            <Grid container spacing={2}>
              {filteredStrategies.map((strategy) => (
                <Grid item xs={12} md={6} key={strategy.id}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      border: selectedStrategy?.id === strategy.id ? 2 : 1,
                      borderColor: selectedStrategy?.id === strategy.id ? 'primary.main' : 'divider',
                      backgroundColor: selectedStrategy?.id === strategy.id ? 'action.selected' : 'background.paper',
                      '&:hover': {
                        boxShadow: 2,
                        transform: 'translateY(-2px)',
                        transition: 'all 0.2s'
                      }
                    }}
                    onClick={() => {
                      console.log('Card clicked for strategy:', strategy.name, strategy.id)
                      handleStrategySelect(strategy)
                    }}
                  >
                    <CardContent>
                      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" mb={1}>
                        <Box>
                          <Stack direction="row" alignItems="center" spacing={1} mb={0.5}>
                            <Typography variant="h6">
                              {strategy.name}
                            </Typography>
                            {strategy.is_public ? (
                              <Tooltip title="공유된 전략">
                                <Public fontSize="small" color="primary" />
                              </Tooltip>
                            ) : (
                              <Tooltip title="비공개 전략">
                                <Lock fontSize="small" color="action" />
                              </Tooltip>
                            )}
                          </Stack>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            {strategy.description || '설명 없음'}
                          </Typography>
                          <Box mt={1}>
                            <Typography 
                              variant="caption" 
                              sx={{ 
                                display: 'inline-block',
                                backgroundColor: (theme) => theme.palette.mode === 'dark' ? 'rgba(144, 202, 249, 0.16)' : 'rgba(25, 118, 210, 0.08)',
                                color: 'primary.main',
                                px: 1.5,
                                py: 0.5,
                                borderRadius: 1,
                                fontWeight: 500,
                                fontSize: '0.75rem',
                                border: '1px solid',
                                borderColor: 'primary.light'
                              }}
                            >
                              {getStrategyConditionSummary(strategy)}
                            </Typography>
                          </Box>
                        </Box>
                        {getStatusChip(strategy.stats)}
                      </Stack>

                      <Divider sx={{ my: 1.5 }} />

                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Stack spacing={1}>
                            <Box display="flex" alignItems="center" gap={1}>
                              <QueryStats fontSize="small" color="action" />
                              <Typography variant="body2">
                                실행 횟수: {strategy.stats?.executionCount || 0}회
                              </Typography>
                            </Box>
                            <Box display="flex" alignItems="center" gap={1}>
                              <TrendingUp fontSize="small" color="success" />
                              <Typography variant="body2">
                                평균 수익률: {strategy.stats?.averageReturn?.toFixed(2) || 0}%
                              </Typography>
                            </Box>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Assessment fontSize="small" color="info" />
                              <Typography variant="body2">
                                승률: {strategy.stats?.winRate?.toFixed(1) || 0}%
                              </Typography>
                            </Box>
                          </Stack>
                        </Grid>
                        <Grid item xs={6}>
                          <Stack spacing={1}>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Business fontSize="small" color="action" />
                              <Typography variant="body2">
                                종목 수: {strategy.stats?.includedStocks || 0}개
                              </Typography>
                            </Box>
                            {strategy.stats?.backtestResults && (
                              <>
                                <Box display="flex" alignItems="center" gap={1}>
                                  <AccountBalance fontSize="small" color="primary" />
                                  <Typography variant="body2">
                                    총 수익: {strategy.stats.backtestResults.totalReturn.toFixed(2)}%
                                  </Typography>
                                </Box>
                                <Box display="flex" alignItems="center" gap={1}>
                                  <TrendingDown fontSize="small" color="error" />
                                  <Typography variant="body2">
                                    MDD: {strategy.stats.backtestResults.maxDrawdown.toFixed(2)}%
                                  </Typography>
                                </Box>
                              </>
                            )}
                          </Stack>
                        </Grid>
                      </Grid>

                      <Box mt={2}>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Box>
                            <Typography variant="caption" color="text.secondary" display="block">
                              생성: {strategy.created_at && 
                                new Date(strategy.created_at).toLocaleDateString('ko-KR', {
                                  year: 'numeric',
                                  month: 'short',
                                  day: 'numeric'
                                })
                              }
                            </Typography>
                            <Typography variant="caption" color="text.secondary" display="block">
                              수정: {strategy.updated_at && 
                                formatDistanceToNow(new Date(strategy.updated_at), { 
                                  addSuffix: true, 
                                  locale: ko 
                                })
                              }
                            </Typography>
                          </Box>
                          <Stack direction="row" spacing={1}>
                            {strategy.tags?.map(tag => (
                              <Chip key={tag} label={tag} size="small" />
                            ))}
                          </Stack>
                        </Stack>
                      </Box>
                    </CardContent>
                    
                    <CardActions>
                      <Stack direction="row" spacing={1} width="100%" justifyContent="flex-end">
                        <Tooltip title="미리보기">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="복사">
                          <IconButton 
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDuplicate(strategy)
                            }}
                          >
                            <ContentCopy />
                          </IconButton>
                        </Tooltip>
                        {strategy.user_id === currentUserId && (
                          <Tooltip title="삭제">
                            <IconButton 
                              size="small" 
                              color="error"
                              onClick={(e) => {
                                e.stopPropagation()
                                setStrategyToDelete(strategy.id)
                                setDeleteConfirmOpen(true)
                              }}
                            >
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Stack>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose}>취소</Button>
          <Button 
            onClick={() => {
              console.log('Load button clicked!')
              console.log('Current selectedStrategy:', selectedStrategy)
              handleLoad()
            }} 
            variant="contained" 
            disabled={!selectedStrategy}
          >
            불러오기
          </Button>
        </DialogActions>
      </Dialog>

      {/* 삭제 확인 다이얼로그 */}
      <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)}>
        <DialogTitle>전략 삭제</DialogTitle>
        <DialogContent>
          <Typography>
            이 전략을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>취소</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            삭제
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

export default StrategyLoader