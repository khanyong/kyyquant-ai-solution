import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Stack,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Alert,
  CircularProgress,
  Divider,
  Snackbar,
  TextField,
  InputAdornment,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Pagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material'
import {
  PlayArrow,
  Stop,
  Refresh,
  Search,
  CheckCircleOutline,
  RadioButtonUnchecked,
  CheckCircle
} from '@mui/icons-material'
import { supabase } from '../../lib/supabase'

interface Strategy {
  id: string
  name: string
  entry_conditions: any
  exit_conditions: any
  config?: any
  targetProfit?: any
  stopLoss?: any
  auto_execute: boolean
  is_active: boolean
  created_at?: string
}

interface InvestmentFilter {
  id: string
  name: string
  filtered_stocks_count: number
  filtered_stocks: string[]
  created_at?: string
}

interface ActiveAutoTrading {
  strategy_id: string
  strategy_name: string
  universes: {
    filter_id: string
    filter_name: string
  }[]
  signalCount?: number
}

const ITEMS_PER_PAGE = 10

const AutoTradingPanel: React.FC = () => {
  // State
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [filters, setFilters] = useState<InvestmentFilter[]>([])
  const [activeAutoTrading, setActiveAutoTrading] = useState<ActiveAutoTrading[]>([])

  const [selectedStrategyId, setSelectedStrategyId] = useState<string>('')
  const [selectedFilterIds, setSelectedFilterIds] = useState<string[]>([])

  // Search and filter state
  const [strategySearch, setStrategySearch] = useState('')
  const [universeSearch, setUniverseSearch] = useState('')
  const [strategyPage, setStrategyPage] = useState(1)
  const [universePage, setUniversePage] = useState(1)

  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  // Snackbar state
  const [snackbar, setSnackbar] = useState<{
    open: boolean
    message: string
    severity: 'success' | 'error' | 'info'
  }>({ open: false, message: '', severity: 'info' })

  const showMessage = (message: string, severity: 'success' | 'error' | 'info' = 'info') => {
    setSnackbar({ open: true, message, severity })
  }

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false })
  }

  // 초기 데이터 로드
  useEffect(() => {
    loadStrategies()
    loadFilters()
    loadActiveAutoTrading()
  }, [])

  // 전략 목록 로드
  const loadStrategies = async () => {
    try {
      const { data, error } = await supabase
        .from('strategies')
        .select('id, name, entry_conditions, exit_conditions, auto_execute, is_active, created_at')
        .order('created_at', { ascending: false })

      if (error) throw error
      setStrategies(data || [])
    } catch (error: any) {
      console.error('전략 로드 실패:', error)
      showMessage('전략 로드 실패', 'error')
    }
  }

  // 투자유니버스 목록 로드
  const loadFilters = async () => {
    try {
      const { data, error } = await supabase
        .from('kw_investment_filters')
        .select('id, name, filtered_stocks_count, filtered_stocks, created_at')
        .eq('is_active', true)
        .order('created_at', { ascending: false })

      if (error) throw error
      setFilters(data || [])
    } catch (error: any) {
      console.error('필터 로드 실패:', error)
      showMessage('투자유니버스 로드 실패', 'error')
    }
  }

  // 활성 자동매매 목록 조회
  const loadActiveAutoTrading = async () => {
    try {
      setRefreshing(true)
      const { data, error } = await supabase
        .rpc('get_active_strategies_with_universe')

      if (error) throw error

      // 전략별로 그룹화
      const grouped = (data || []).reduce((acc: any, item: any) => {
        if (!acc[item.strategy_id]) {
          acc[item.strategy_id] = {
            strategy_id: item.strategy_id,
            strategy_name: item.strategy_name,
            universes: []
          }
        }
        acc[item.strategy_id].universes.push({
          filter_id: item.filter_id,
          filter_name: item.filter_name
        })
        return acc
      }, {})

      const result = Object.values(grouped)
      setActiveAutoTrading(result as ActiveAutoTrading[])

      // 각 전략의 신호 개수 조회
      for (const item of result as ActiveAutoTrading[]) {
        loadSignalCount(item.strategy_id)
      }
    } catch (error: any) {
      console.error('활성 자동매매 조회 실패:', error)
    } finally {
      setRefreshing(false)
    }
  }

  // 신호 개수 조회
  const loadSignalCount = async (strategyId: string) => {
    try {
      const { count, error } = await supabase
        .from('trading_signals')
        .select('*', { count: 'exact', head: true })
        .eq('strategy_id', strategyId)
        .gte('created_at', new Date(Date.now() - 24*60*60*1000).toISOString())

      if (error) throw error

      setActiveAutoTrading(prev => prev.map(item =>
        item.strategy_id === strategyId
          ? { ...item, signalCount: count || 0 }
          : item
      ))
    } catch (error: any) {
      console.error('신호 개수 조회 실패:', error)
    }
  }

  // 자동매매 시작
  const handleStartAutoTrading = async () => {
    if (!selectedStrategyId) {
      showMessage('전략을 선택해주세요', 'error')
      return
    }

    if (selectedFilterIds.length === 0) {
      showMessage('투자유니버스를 1개 이상 선택해주세요', 'error')
      return
    }

    try {
      setLoading(true)

      // 1. 전략 auto_execute 활성화
      const { error: strategyError } = await supabase
        .from('strategies')
        .update({
          auto_execute: true,
          auto_trade_enabled: true,
          is_active: true
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

      showMessage('자동매매가 시작되었습니다!', 'success')

      // 초기화
      setSelectedStrategyId('')
      setSelectedFilterIds([])

      // 새로고침
      loadStrategies()
      loadActiveAutoTrading()
    } catch (error: any) {
      console.error('자동매매 시작 실패:', error)
      showMessage(`자동매매 시작 실패: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // 자동매매 중지
  const handleStopAutoTrading = async (strategyId: string) => {
    if (!confirm('정말 자동매매를 중지하시겠습니까?')) {
      return
    }

    try {
      setLoading(true)

      // 1. 전략 비활성화
      const { error: strategyError } = await supabase
        .from('strategies')
        .update({
          auto_execute: false,
          auto_trade_enabled: false
        })
        .eq('id', strategyId)

      if (strategyError) throw strategyError

      // 2. 연결된 유니버스 비활성화
      const { error: connectError } = await supabase
        .from('strategy_universes')
        .update({ is_active: false })
        .eq('strategy_id', strategyId)

      if (connectError) throw connectError

      showMessage('자동매매가 중지되었습니다', 'success')

      // 새로고침
      loadStrategies()
      loadActiveAutoTrading()
    } catch (error: any) {
      console.error('자동매매 중지 실패:', error)
      showMessage(`자동매매 중지 실패: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // 필터 선택 토글
  const handleToggleFilter = (filterId: string) => {
    setSelectedFilterIds(prev =>
      prev.includes(filterId)
        ? prev.filter(id => id !== filterId)
        : [...prev, filterId]
    )
  }

  // 필터링된 전략 목록
  const availableStrategies = strategies.filter(s => !s.auto_execute)
  const filteredStrategies = availableStrategies.filter(s =>
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
    <Box sx={{ p: 3 }}>
      {/* 헤더 */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h5">자동매매</Typography>
        <Button
          startIcon={<Refresh />}
          onClick={loadActiveAutoTrading}
          disabled={refreshing}
          size="small"
        >
          새로고침
        </Button>
      </Stack>

      {/* 자동매매 설정 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          새 자동매매 시작
        </Typography>
        <Typography variant="caption" color="text.secondary" gutterBottom display="block">
          단계 1/2
        </Typography>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ display: 'flex', gap: 3, minHeight: 500 }}>
          {/* 1단계: 전략 선택 */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              📋 1단계: 전략 선택 (단일)
            </Typography>

            {/* 검색 */}
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

            {/* 전략 리스트 */}
            {availableStrategies.length === 0 ? (
              <Alert severity="info">
                사용 가능한 전략이 없습니다. 모든 전략이 이미 활성화되었거나 전략을 먼저 생성해주세요.
              </Alert>
            ) : filteredStrategies.length === 0 ? (
              <Alert severity="info">
                검색 결과가 없습니다.
              </Alert>
            ) : (
              <>
                <Paper variant="outlined" sx={{ maxHeight: 350, overflow: 'auto' }}>
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
                                  📊 매수 {strategy.entry_conditions?.buy?.length || 0}개 조건
                                </Typography>
                              </Box>
                            </Box>
                          </ListItemButton>
                        </ListItem>
                      </React.Fragment>
                    ))}
                  </List>
                </Paper>

                {/* 페이지네이션 */}
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

                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {(strategyPage - 1) * ITEMS_PER_PAGE + 1}-
                  {Math.min(strategyPage * ITEMS_PER_PAGE, filteredStrategies.length)} / {filteredStrategies.length}개 전략
                </Typography>
              </>
            )}
          </Box>

          {/* 선택된 전략 상세 정보 */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              선택된 전략
            </Typography>

            {selectedStrategy ? (
              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'primary.50' }}>
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      ✓ {selectedStrategy.name}
                    </Typography>
                  </Box>

                  <Divider />

                  <Box>
                    <Typography variant="subtitle2" gutterBottom fontWeight="bold">
                      매수조건 ({selectedStrategy.entry_conditions?.buy?.length || 0}개):
                    </Typography>
                    {selectedStrategy.entry_conditions?.buy?.length > 0 ? (
                      <Box component="ul" sx={{ m: 0, pl: 2 }}>
                        {selectedStrategy.entry_conditions.buy.map((cond: any, idx: number) => (
                          <Typography key={idx} variant="body2" component="li" sx={{ mb: 0.5 }}>
                            {cond.left} {cond.operator} {cond.right}
                          </Typography>
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        조건 없음
                      </Typography>
                    )}
                  </Box>

                  <Box>
                    <Typography variant="subtitle2" gutterBottom fontWeight="bold">
                      매도조건 ({selectedStrategy.exit_conditions?.sell?.length || 0}개):
                    </Typography>
                    {selectedStrategy.exit_conditions?.sell?.length > 0 ? (
                      <Box component="ul" sx={{ m: 0, pl: 2 }}>
                        {selectedStrategy.exit_conditions.sell.map((cond: any, idx: number) => (
                          <Typography key={idx} variant="body2" component="li" sx={{ mb: 0.5 }}>
                            {cond.left} {cond.operator} {cond.right}
                          </Typography>
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        수동 매도
                      </Typography>
                    )}
                  </Box>

                  {selectedStrategy.created_at && (
                    <Typography variant="caption" color="text.secondary">
                      생성일: {new Date(selectedStrategy.created_at).toLocaleDateString()}
                    </Typography>
                  )}
                </Stack>
              </Paper>
            ) : (
              <Alert severity="info">
                왼쪽에서 전략을 선택하면 상세 정보가 표시됩니다.
              </Alert>
            )}
          </Box>
        </Box>

        <Divider sx={{ my: 3 }} />

        <Typography variant="caption" color="text.secondary" gutterBottom display="block">
          단계 2/2
        </Typography>

        <Box sx={{ display: 'flex', gap: 3, minHeight: 500 }}>
          {/* 2단계: 투자유니버스 선택 */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              🌐 2단계: 투자유니버스 선택 (다중 가능)
            </Typography>

            {/* 검색 */}
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

            {/* 투자유니버스 리스트 */}
            {filters.length === 0 ? (
              <Alert severity="info">
                저장된 투자유니버스가 없습니다. 먼저 종목 필터링에서 유니버스를 생성해주세요.
              </Alert>
            ) : filteredUniverses.length === 0 ? (
              <Alert severity="info">
                검색 결과가 없습니다.
              </Alert>
            ) : (
              <>
                <Paper variant="outlined" sx={{ maxHeight: 350, overflow: 'auto' }}>
                  <List disablePadding>
                    {paginatedUniverses.map((filter, index) => (
                      <React.Fragment key={filter.id}>
                        {index > 0 && <Divider />}
                        <ListItem disablePadding>
                          <ListItemButton
                            selected={selectedFilterIds.includes(filter.id)}
                            onClick={() => handleToggleFilter(filter.id)}
                          >
                            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                              {selectedFilterIds.includes(filter.id) ? (
                                <CheckCircle color="success" sx={{ mr: 2 }} />
                              ) : (
                                <RadioButtonUnchecked color="disabled" sx={{ mr: 2 }} />
                              )}
                              <Box sx={{ flex: 1 }}>
                                <Typography variant="body1" fontWeight="medium">
                                  {filter.name}
                                </Typography>
                                <Chip
                                  label={`${filter.filtered_stocks_count}개 종목`}
                                  size="small"
                                  sx={{ mt: 0.5 }}
                                />
                              </Box>
                            </Box>
                          </ListItemButton>
                        </ListItem>
                      </React.Fragment>
                    ))}
                  </List>
                </Paper>

                {/* 페이지네이션 */}
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

                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {(universePage - 1) * ITEMS_PER_PAGE + 1}-
                  {Math.min(universePage * ITEMS_PER_PAGE, filteredUniverses.length)} / {filteredUniverses.length}개 유니버스
                </Typography>
              </>
            )}
          </Box>

          {/* 선택된 투자유니버스 상세 정보 */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              선택된 유니버스 ({selectedFilterIds.length}개)
            </Typography>

            {selectedUniverses.length > 0 ? (
              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'success.50' }}>
                <Stack spacing={2}>
                  {selectedUniverses.map(universe => (
                    <Box key={universe.id}>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <CheckCircle color="success" fontSize="small" />
                        <Typography variant="subtitle2" fontWeight="bold">
                          {universe.name}
                        </Typography>
                      </Stack>
                      <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
                        📈 {universe.filtered_stocks_count}개 종목
                      </Typography>
                      {universe.filtered_stocks && universe.filtered_stocks.length > 0 && (
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 3, display: 'block', mt: 0.5 }}>
                          {universe.filtered_stocks.slice(0, 5).join(', ')}...
                        </Typography>
                      )}
                      {selectedUniverses.length > 1 && <Divider sx={{ mt: 1.5 }} />}
                    </Box>
                  ))}

                  <Box sx={{ bgcolor: 'info.50', p: 1.5, borderRadius: 1, mt: 2 }}>
                    <Typography variant="body2" color="info.main" fontWeight="bold">
                      💡 팁
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      여러 유니버스를 선택하면 각각 독립적으로 모니터링됩니다.
                    </Typography>
                    <Typography variant="body2" fontWeight="bold" sx={{ mt: 1 }}>
                      총 {totalStocksCount}개 종목 (중복 제외)
                    </Typography>
                  </Box>
                </Stack>
              </Paper>
            ) : (
              <Alert severity="info">
                왼쪽에서 투자유니버스를 선택하면 상세 정보가 표시됩니다.
              </Alert>
            )}
          </Box>
        </Box>

        {/* 시작 버튼 */}
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <Button
            variant="outlined"
            onClick={() => {
              setSelectedStrategyId('')
              setSelectedFilterIds([])
              setStrategySearch('')
              setUniverseSearch('')
              setStrategyPage(1)
              setUniversePage(1)
            }}
          >
            초기화
          </Button>
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
            onClick={handleStartAutoTrading}
            disabled={loading || !selectedStrategyId || selectedFilterIds.length === 0}
            size="large"
          >
            자동매매 시작
          </Button>
        </Box>
      </Paper>

      <Divider sx={{ my: 3 }} />

      {/* 활성 자동매매 현황 */}
      <Typography variant="h6" gutterBottom>
        활성 자동매매 현황
      </Typography>

      {activeAutoTrading.length === 0 ? (
        <Alert severity="info">
          활성화된 자동매매가 없습니다. 위에서 전략과 투자유니버스를 선택하여 시작하세요.
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>전략명</TableCell>
                <TableCell>투자유니버스</TableCell>
                <TableCell align="center">24시간 신호</TableCell>
                <TableCell align="center">상태</TableCell>
                <TableCell align="center">관리</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {activeAutoTrading.map(item => (
                <TableRow key={item.strategy_id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="bold">
                      {item.strategy_name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={0.5} flexWrap="wrap">
                      {item.universes.map(u => (
                        <Chip
                          key={u.filter_id}
                          label={u.filter_name}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Stack>
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={`${item.signalCount ?? '...'} 개`}
                      size="small"
                      color={item.signalCount && item.signalCount > 0 ? 'success' : 'default'}
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      icon={<CheckCircleOutline />}
                      label="활성"
                      color="success"
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleStopAutoTrading(item.strategy_id)}
                      disabled={loading}
                    >
                      <Stop />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default AutoTradingPanel
