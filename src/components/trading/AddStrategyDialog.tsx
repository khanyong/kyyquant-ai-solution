import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Stack,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  TextField,
  InputAdornment,
  Divider,
  Pagination,
  Paper,
  Chip,
  Alert,
  FormControl,
  InputLabel,
  OutlinedInput
} from '@mui/material'
import {
  Search,
  CheckCircle,
  RadioButtonUnchecked,
  CheckCircleOutline
} from '@mui/icons-material'
import { supabase } from '../../lib/supabase'
import OrderPriceStrategySelector from './OrderPriceStrategySelector'

interface Strategy {
  id: string
  name: string
  entry_conditions: any
  exit_conditions: any
}

interface InvestmentFilter {
  id: string
  name: string
  filtered_stocks_count: number
  filtered_stocks: string[]
}

interface OrderPriceStrategy {
  buy: {
    type: 'best_ask' | 'best_bid' | 'mid_price' | 'market'
    offset: number
  }
  sell: {
    type: 'best_bid' | 'best_ask' | 'mid_price' | 'market'
    offset: number
  }
}

interface AddStrategyDialogProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

const ITEMS_PER_PAGE = 10

const ORDER_PRICE_LABELS: Record<string, string> = {
  best_ask: '매도1호가',
  best_bid: '매수1호가',
  mid_price: '중간가',
  market: '시장가'
}

export default function AddStrategyDialog({ open, onClose, onSuccess }: AddStrategyDialogProps) {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [filters, setFilters] = useState<InvestmentFilter[]>([])

  const [selectedStrategyId, setSelectedStrategyId] = useState<string>('')
  const [selectedFilterIds, setSelectedFilterIds] = useState<string[]>([])

  const [allocatedCapital, setAllocatedCapital] = useState<number>(0)
  const [allocatedPercent, setAllocatedPercent] = useState<number>(0)

  const [orderPriceStrategy, setOrderPriceStrategy] = useState<OrderPriceStrategy>({
    buy: { type: 'best_ask', offset: 10 },
    sell: { type: 'best_bid', offset: -10 }
  })

  const [strategySearch, setStrategySearch] = useState('')
  const [universeSearch, setUniverseSearch] = useState('')
  const [strategyPage, setStrategyPage] = useState(1)
  const [universePage, setUniversePage] = useState(1)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (open) {
      loadStrategies()
      loadFilters()
    }
  }, [open])

  const loadStrategies = async () => {
    try {
      const { data, error } = await supabase
        .from('strategies')
        .select('id, name, entry_conditions, exit_conditions, auto_execute')
        .eq('auto_execute', false) // 이미 활성화된 전략 제외
        .order('created_at', { ascending: false })

      if (error) throw error
      setStrategies(data || [])
    } catch (error: any) {
      console.error('전략 로드 실패:', error)
      setError('전략을 불러오는데 실패했습니다.')
    }
  }

  const loadFilters = async () => {
    try {
      const { data, error } = await supabase
        .from('kw_investment_filters')
        .select('id, name, filtered_stocks_count, filtered_stocks')
        .eq('is_active', true)
        .order('created_at', { ascending: false })

      if (error) throw error
      setFilters(data || [])
    } catch (error: any) {
      console.error('필터 로드 실패:', error)
      setError('투자유니버스를 불러오는데 실패했습니다.')
    }
  }

  const handleToggleFilter = (filterId: string) => {
    setSelectedFilterIds(prev =>
      prev.includes(filterId)
        ? prev.filter(id => id !== filterId)
        : [...prev, filterId]
    )
  }

  const handleSave = async () => {
    if (!selectedStrategyId) {
      setError('전략을 선택해주세요')
      return
    }

    if (selectedFilterIds.length === 0) {
      setError('투자유니버스를 1개 이상 선택해주세요')
      return
    }

    if (allocatedPercent <= 0) {
      setError('할당 비율을 입력해주세요 (0보다 커야 합니다)')
      return
    }

    try {
      setLoading(true)
      setError('')

      // 1. 전략 활성화 및 자금 할당, 주문 가격 전략 저장
      const { error: strategyError } = await supabase
        .from('strategies')
        .update({
          auto_execute: true,
          auto_trade_enabled: true,
          is_active: true,
          allocated_capital: allocatedCapital || 0,
          allocated_percent: allocatedPercent || 0,
          order_price_strategy: orderPriceStrategy
        })
        .eq('id', selectedStrategyId)

      if (strategyError) throw strategyError

      // 2. 선택된 투자유니버스들과 연결
      const connections = selectedFilterIds.map(filterId => ({
        strategy_id: selectedStrategyId,
        investment_filter_id: filterId,
        is_active: true
      }))

      const { error: connectError } = await supabase
        .from('strategy_universes')
        .upsert(connections, {
          onConflict: 'strategy_id,investment_filter_id'
        })

      if (connectError) throw connectError

      // 성공
      onSuccess()
      handleClose()
    } catch (error: any) {
      console.error('자동매매 시작 실패:', error)
      setError(`자동매매 시작 실패: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setSelectedStrategyId('')
    setSelectedFilterIds([])
    setAllocatedCapital(0)
    setAllocatedPercent(0)
    setOrderPriceStrategy({
      buy: { type: 'best_ask', offset: 10 },
      sell: { type: 'best_bid', offset: -10 }
    })
    setStrategySearch('')
    setUniverseSearch('')
    setStrategyPage(1)
    setUniversePage(1)
    setError('')
    onClose()
  }

  // 필터링된 전략 목록
  const filteredStrategies = strategies.filter(s =>
    s.name.toLowerCase().includes(strategySearch.toLowerCase())
  )
  const paginatedStrategies = filteredStrategies.slice(
    (strategyPage - 1) * ITEMS_PER_PAGE,
    strategyPage * ITEMS_PER_PAGE
  )
  const strategyPageCount = Math.ceil(filteredStrategies.length / ITEMS_PER_PAGE)

  // 필터링된 투자유니버스 목록
  const filteredUniverses = filters.filter(f =>
    f.name.toLowerCase().includes(universeSearch.toLowerCase())
  )
  const paginatedUniverses = filteredUniverses.slice(
    (universePage - 1) * ITEMS_PER_PAGE,
    universePage * ITEMS_PER_PAGE
  )
  const universePageCount = Math.ceil(filteredUniverses.length / ITEMS_PER_PAGE)

  const selectedStrategy = strategies.find(s => s.id === selectedStrategyId)
  const selectedUniverses = filters.filter(f => selectedFilterIds.includes(f.id))

  // 총 종목 수 계산 (중복 제외)
  const totalStocksCount = selectedUniverses.length > 0
    ? new Set(selectedUniverses.flatMap(u => u.filtered_stocks || [])).size
    : 0

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="lg"
      fullWidth
    >
      <DialogTitle>
        <Typography variant="h6" fontWeight="bold">
          ➕ 새 자동매매 전략 추가
        </Typography>
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <Stack spacing={3}>
          {/* 1단계: 전략 선택 */}
          <Box>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              📋 1단계: 전략 선택
            </Typography>

            <TextField
              fullWidth
              size="small"
              placeholder="전략명으로 검색..."
              value={strategySearch}
              onChange={(e) => {
                setStrategySearch(e.target.value)
                setStrategyPage(1)
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                )
              }}
              sx={{ mb: 2 }}
            />

            {strategies.length === 0 ? (
              <Alert severity="info">
                사용 가능한 전략이 없습니다. 전략을 먼저 생성해주세요.
              </Alert>
            ) : filteredStrategies.length === 0 ? (
              <Alert severity="info">
                검색 결과가 없습니다.
              </Alert>
            ) : (
              <>
                <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
                  <List disablePadding>
                    {paginatedStrategies.map((strategy, index) => (
                      <React.Fragment key={strategy.id}>
                        {index > 0 && <Divider />}
                        <ListItem disablePadding>
                          <ListItemButton
                            selected={selectedStrategyId === strategy.id}
                            onClick={() => setSelectedStrategyId(strategy.id)}
                          >
                            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                              {selectedStrategyId === strategy.id ? (
                                <CheckCircle color="primary" sx={{ mr: 2 }} />
                              ) : (
                                <RadioButtonUnchecked color="disabled" sx={{ mr: 2 }} />
                              )}
                              <Box sx={{ flex: 1 }}>
                                <Typography variant="body1" fontWeight="medium">
                                  {strategy.name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  매수 {strategy.entry_conditions?.buy?.length || 0}개 조건
                                </Typography>
                              </Box>
                            </Box>
                          </ListItemButton>
                        </ListItem>
                      </React.Fragment>
                    ))}
                  </List>
                </Paper>

                {strategyPageCount > 1 && (
                  <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                    <Pagination
                      count={strategyPageCount}
                      page={strategyPage}
                      onChange={(e, page) => setStrategyPage(page)}
                      size="small"
                    />
                  </Box>
                )}
              </>
            )}
          </Box>

          {/* 2단계: 투자유니버스 선택 */}
          <Box>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              🌐 2단계: 투자유니버스 선택 (다중)
            </Typography>

            <TextField
              fullWidth
              size="small"
              placeholder="유니버스명으로 검색..."
              value={universeSearch}
              onChange={(e) => {
                setUniverseSearch(e.target.value)
                setUniversePage(1)
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                )
              }}
              sx={{ mb: 2 }}
            />

            {filters.length === 0 ? (
              <Alert severity="info">
                사용 가능한 투자유니버스가 없습니다.
              </Alert>
            ) : filteredUniverses.length === 0 ? (
              <Alert severity="info">
                검색 결과가 없습니다.
              </Alert>
            ) : (
              <>
                <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
                  <List disablePadding>
                    {paginatedUniverses.map((filter, index) => (
                      <React.Fragment key={filter.id}>
                        {index > 0 && <Divider />}
                        <ListItem disablePadding>
                          <ListItemButton onClick={() => handleToggleFilter(filter.id)}>
                            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                              {selectedFilterIds.includes(filter.id) ? (
                                <CheckCircleOutline color="primary" sx={{ mr: 2 }} />
                              ) : (
                                <RadioButtonUnchecked color="disabled" sx={{ mr: 2 }} />
                              )}
                              <Box sx={{ flex: 1 }}>
                                <Typography variant="body1" fontWeight="medium">
                                  {filter.name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {filter.filtered_stocks_count || filter.filtered_stocks?.length || 0}개 종목
                                </Typography>
                              </Box>
                            </Box>
                          </ListItemButton>
                        </ListItem>
                      </React.Fragment>
                    ))}
                  </List>
                </Paper>

                {universePageCount > 1 && (
                  <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                    <Pagination
                      count={universePageCount}
                      page={universePage}
                      onChange={(e, page) => setUniversePage(page)}
                      size="small"
                    />
                  </Box>
                )}
              </>
            )}
          </Box>

          {/* 3단계: 자금 할당 */}
          <Box>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              💰 3단계: 자금 할당
            </Typography>

            <Stack direction="row" spacing={2}>
              <FormControl fullWidth>
                <InputLabel>할당 비율 (%)</InputLabel>
                <OutlinedInput
                  type="number"
                  value={allocatedPercent}
                  onChange={(e) => setAllocatedPercent(parseFloat(e.target.value) || 0)}
                  label="할당 비율 (%)"
                  endAdornment={<InputAdornment position="end">%</InputAdornment>}
                />
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>할당 금액 (원)</InputLabel>
                <OutlinedInput
                  type="number"
                  value={allocatedCapital}
                  onChange={(e) => setAllocatedCapital(parseFloat(e.target.value) || 0)}
                  label="할당 금액 (원)"
                  endAdornment={<InputAdornment position="end">원</InputAdornment>}
                />
              </FormControl>
            </Stack>
          </Box>

          {/* 4단계: 주문 가격 전략 */}
          <Box>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              📊 4단계: 주문 가격 전략
            </Typography>
            <OrderPriceStrategySelector
              value={orderPriceStrategy}
              onChange={setOrderPriceStrategy}
            />
          </Box>

          {/* 선택 요약 */}
          {(selectedStrategy || selectedUniverses.length > 0) && (
            <Paper sx={{ p: 2, bgcolor: 'primary.50' }}>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                ✓ 선택 요약
              </Typography>
              <Stack spacing={1}>
                {selectedStrategy && (
                  <Typography variant="body2">
                    전략: <strong>{selectedStrategy.name}</strong>
                  </Typography>
                )}
                {selectedUniverses.length > 0 && (
                  <Typography variant="body2">
                    투자유니버스: <strong>{selectedUniverses.map(u => u.name).join(', ')}</strong> ({totalStocksCount}개 종목)
                  </Typography>
                )}
                {allocatedPercent > 0 && (
                  <Typography variant="body2">
                    할당: <strong>{allocatedPercent}%</strong> {allocatedCapital > 0 && `(${allocatedCapital.toLocaleString()}원)`}
                  </Typography>
                )}
                <Typography variant="body2">
                  주문 가격: 매수 <strong>{ORDER_PRICE_LABELS[orderPriceStrategy.buy.type]}</strong>
                  {orderPriceStrategy.buy.offset !== 0 && ` (${orderPriceStrategy.buy.offset > 0 ? '+' : ''}${orderPriceStrategy.buy.offset}원)`},
                  매도 <strong>{ORDER_PRICE_LABELS[orderPriceStrategy.sell.type]}</strong>
                  {orderPriceStrategy.sell.offset !== 0 && ` (${orderPriceStrategy.sell.offset > 0 ? '+' : ''}${orderPriceStrategy.sell.offset}원)`}
                </Typography>
              </Stack>
            </Paper>
          )}
        </Stack>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          취소
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={loading || !selectedStrategyId || selectedFilterIds.length === 0 || allocatedPercent <= 0}
        >
          {loading ? '저장 중...' : '자동매매 시작'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
