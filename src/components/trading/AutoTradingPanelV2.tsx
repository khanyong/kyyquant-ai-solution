import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Stack,
  Button,
  Collapse,
  Alert,
  CircularProgress,
  Chip,
  Paper
} from '@mui/material'
import {
  Add,
  Refresh,
  Work,
  ShowChart
} from '@mui/icons-material'
import { useAppSelector } from '../../hooks/redux'
import { supabase } from '../../lib/supabase'
import { systemService, SystemStatus } from '../../services/systemService'
import PortfolioOverview from './PortfolioOverview'
import PortfolioHoldingsTable from './PortfolioHoldingsTable'
import StrategyCard from './StrategyCard'
import EmergencyControlPanel from './EmergencyControlPanel'
import StrategyVerificationPanel from '../StrategyVerificationPanel'
import AddStrategyDialog from './AddStrategyDialog'
import MyStrategyConfig from '../strategy/MyStrategyConfig'

interface ActiveStrategy {
  strategy_id: string
  strategy_name: string
  entry_conditions: any
  exit_conditions: any
  universes: {
    filter_id: string
    filter_name: string
  }[]
  allocated_capital: number
  allocated_percent: number
}

export default function AutoTradingPanelV2() {
  const { user, tradingMode } = useAppSelector(state => state.auth)
  const [loading, setLoading] = useState(false)
  const [activeStrategies, setActiveStrategies] = useState<ActiveStrategy[]>([])
  const [portfolioStats, setPortfolioStats] = useState<any>({})
  const [positions, setPositions] = useState<any[]>([])
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [editingStrategy, setEditingStrategy] = useState<ActiveStrategy | null>(null)

  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [tradingContext, setTradingContext] = useState<SystemStatus['trading_context'] | null>(null)

  // Derived Accessor for Current Account Number
  const currentAccountNo = tradingContext
    ? (tradingMode === 'test'
      ? tradingContext.accounts?.MOCK || tradingContext.active_account_no
      : tradingContext.accounts?.LIVE || tradingContext.active_account_no)
    : undefined

  const loadActiveStrategies = async () => {
    try {
      const { data, error } = await supabase
        .rpc('get_active_strategies_with_universe')

      if (error) throw error

      // [NEW] RPC now returns unique strategies with 'universes' JSONB array
      // No need to reduce/group manualy anymore.
      const formatted: ActiveStrategy[] = (data || []).map((item: any) => ({
        strategy_id: item.strategy_id,
        strategy_name: item.strategy_name,
        entry_conditions: item.entry_conditions,
        exit_conditions: item.exit_conditions,
        allocated_capital: parseFloat(item.allocated_capital) || 0,
        allocated_percent: parseFloat(item.allocated_percent) || 0,
        universes: (item.universes || []).map((u: any) => ({
          filter_id: u.universe_id,
          filter_name: u.universe_name
        }))
      }))

      setActiveStrategies(formatted)
    } catch (error) {
      console.error('활성 전략 로드 실패:', error)
    }
  }

  const loadPortfolioStats = async (targetAccountNo: string) => {
    try {
      // 1. 활성 전략의 총 할당 자금 계산
      const { data: strategyData } = await supabase
        .rpc('get_active_strategies_with_universe')

      // [NEW] Strategy data is already unique per strategy
      const totalAllocated = (strategyData || []).reduce((sum: number, item: any) => {
        return sum + (parseFloat(item.allocated_capital) || 0)
      }, 0)

      const activeStrategiesCount = (strategyData || []).length

      console.log('Total allocated:', totalAllocated)
      console.log('Active strategies count:', activeStrategiesCount)

      // 1.5 Fetch Real Account Balance (Filtered by Session Context)
      let realTotalAssets = 0
      let realCash = 0

      if (targetAccountNo) {
        const { data: balanceData } = await supabase
          .from('account_balance')
          .select('*')
          .eq('account_no', targetAccountNo) // <--- CRITICAL FIX: Bind to Session Account
          .order('updated_at', { ascending: false })
          .limit(1)
          .maybeSingle()

        realTotalAssets = parseFloat(balanceData?.total_assets) || 0
        realCash = parseFloat(balanceData?.available_cash) || 0
      } else {
        console.warn("No active account number in context. Skipping balance fetch.")
      }

      // 2. 전체 포지션 조회
      const { data: positions, error: posError } = await supabase
        .from('portfolio')
        .select('*')
      // .eq('quantity', 'gt.0') # If needed, but portfolio usually implies ownership

      if (posError) throw posError

      // 3. 현재가 정보와 조인하여 평가액 계산
      let totalInvested = 0
      let totalValue = 0
      let positionsWithPrice: any[] = []

      if (positions && positions.length > 0) {
        positionsWithPrice = await Promise.all(
          positions.map(async (pos: any) => {
            const { data: priceData } = await supabase
              .from('kw_price_current')
              .select('current_price, stock_name') // Fetch stock_name too if needed?
              .eq('stock_code', pos.stock_code)
              .single()

            const currentPrice = priceData?.current_price || pos.avg_price
            // Ensure we have a name
            const stockName = priceData?.stock_name || pos.stock_name || 'Unknown'

            const invested = pos.avg_price * pos.quantity
            const value = currentPrice * pos.quantity

            // [FIX] Use DB value (Net Profit from Kiwoom) if available, otherwise calculate (Gross)
            const netProfit = pos.profit_loss
            const calculatedProfit = value - invested
            const finalProfit = netProfit !== null && netProfit !== undefined ? netProfit : calculatedProfit

            const finalProfitRate = invested > 0 ? (finalProfit / invested) * 100 : 0

            return {
              stock_code: pos.stock_code,
              stock_name: stockName,
              quantity: pos.quantity,
              avg_price: pos.avg_price,
              current_price: currentPrice,
              profit_loss: finalProfit,
              profit_loss_rate: finalProfitRate,
              invested,
              value
            }
          })
        )

        totalInvested = positionsWithPrice.reduce((sum, p) => sum + p.invested, 0)
        totalValue = positionsWithPrice.reduce((sum, p) => sum + p.value, 0)
      }

      // [FIX] Sum individual profits (Net) instead of calculating Gross difference
      const totalProfit = positionsWithPrice.reduce((sum, p) => sum + p.profit_loss, 0)
      const totalProfitRate = totalInvested > 0 ? (totalProfit / totalInvested) * 100 : 0

      const newStats = {
        totalCapital: realTotalAssets,
        totalAllocated,
        totalInvested,
        totalValue,
        totalProfit,
        totalProfitRate,
        activeStrategiesCount,
        totalPositions: positions?.length || 0,
        realCash: realCash // Optional: Pass cash if needed by Overview component
      }

      setPortfolioStats(newStats)
      setPositions(positionsWithPrice || [])
    } catch (error) {
      console.error('포트폴리오 통계 로드 실패:', error)
    }
  }

  // 1. Init: Fetch Trading Context
  useEffect(() => {
    const initContext = async () => {
      try {
        const status = await systemService.getStatus()
        setTradingContext(status.trading_context)
      } catch (err) {
        console.error("Failed to load trading context:", err)
      }
    }
    initContext()
  }, [])

  // 2. Main Data Fetch (Only after Context is ready)
  useEffect(() => {
    if (user && tradingContext) {
      // Determine Account Number based on Redux Mode
      const targetAccount = tradingMode === 'test'
        ? tradingContext.accounts?.MOCK || tradingContext.active_account_no
        : tradingContext.accounts?.LIVE || tradingContext.active_account_no

      fetchPortfolioStats(targetAccount)
      const interval = setInterval(() => fetchPortfolioStats(targetAccount, true), 30000) // 30s refresh (Silent)
      return () => clearInterval(interval)
    }
  }, [user, tradingContext, tradingMode])

  // Combined Loader (Renamed from loadData)
  const fetchPortfolioStats = async (targetAccountNo: string, silent = false) => {
    try {
      if (!silent) setLoading(true)

      await Promise.all([
        loadActiveStrategies(),
        loadPortfolioStats(targetAccountNo)
      ])
      setLastUpdated(new Date())
    } catch (error) {
      console.error('데이터 로드 실패:', error)
    } finally {
      if (!silent) setLoading(false)
    }
  }

  // Helper for manual refreshes
  const refreshData = () => {
    if (tradingContext) {
      const targetAccount = tradingMode === 'test'
        ? tradingContext.accounts?.MOCK || tradingContext.active_account_no
        : tradingContext.accounts?.LIVE || tradingContext.active_account_no

      fetchPortfolioStats(targetAccount)
    }
  }

  // ... (rest of code)

  const handleSyncAccount = async () => {
    try {
      setLoading(true)
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001'
      alert('동기화 시작: 요청을 보낼 주소는 [' + apiUrl + '] 입니다.') // Debugging

      const response = await fetch(`${apiUrl}/api/sync/account`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: user?.id })
      })

      if (!response.ok) {
        throw new Error('Sync failed')
      }

      const result = await response.json()
      // alert(`동기화 완료!\n종목수: ${result.holdings_updated}\n잔고성공여부: ${result.balance_updated}\n\n[디버그 정보]\n재계산됨: ${result.debug?.recalc_triggered}\n보유종목수(서버): ${result.debug?.holdings_count}\n사용자ID: ${result.debug?.user_id}`)

      const debugInfo = result.debug || {}
      alert(`[동기화 결과]\n` +
        `모드: ${debugInfo.mode || 'UNKNOWN'} (URL: ${debugInfo.url})\n` +
        `AppKey: ${debugInfo.key_prefix}\n` +
        `계좌번호: ${debugInfo.account_no}\n` +
        `에러상세: ${debugInfo.error_detail || '없음'}\n` +
        `잔고갱신: ${result.balance_updated ? '성공' : '실패/스킵'}\n` +
        `보유종목변경: ${result.holdings_updated}건`)

      await refreshData()
    } catch (error) {
      console.error('계좌 동기화 실패:', error)
      alert('계좌 동기화에 실패했습니다. 백엔드 로그를 확인해주세요.')
    } finally {
      setLoading(false)
    }
  }



  // ... (Strategies handlers same as before)
  const handleStopStrategy = async (strategyId: string) => {
    // ... (Keep existing implementation)
    if (!confirm('정말 이 전략을 중지하시겠습니까?\n\n자동매매가 중지되지만 전략은 유지됩니다.')) {
      return
    }

    try {
      const { data: strategy, error: fetchError } = await supabase
        .from('strategies')
        .select('allocated_capital, user_id')
        .eq('id', strategyId)
        .single()

      if (fetchError) throw fetchError

      const releasedCapital = strategy.allocated_capital || 0

      const { error: strategyError } = await supabase
        .from('strategies')
        .update({
          auto_execute: false,
          auto_trade_enabled: false,
          allocated_capital: 0,
          allocated_percent: 0
        })
        .eq('id', strategyId)

      if (strategyError) throw strategyError

      if (releasedCapital > 0) {
        const { data: balance, error: balanceError } = await supabase
          .from('kw_account_balance')
          .select('available_cash')
          .eq('user_id', strategy.user_id)
          .order('updated_at', { ascending: false })
          .limit(1)
          .single()

        if (balanceError) throw balanceError

        const { error: cashError } = await supabase
          .from('kw_account_balance')
          .update({
            available_cash: balance.available_cash + releasedCapital,
            updated_at: new Date().toISOString()
          })
          .eq('user_id', strategy.user_id)

        if (cashError) throw cashError
      }

      const { error: universeError } = await supabase
        .from('strategy_universes')
        .update({ is_active: false })
        .eq('strategy_id', strategyId)

      if (universeError) throw universeError

      refreshData()
    } catch (error: any) {
      console.error('전략 중지 실패:', error)
      alert(`전략 중지 실패: ${error.message}`)
    }
  }

  const handleDeleteStrategy = async (strategyId: string) => {
    if (!confirm('정말 이 전략을 삭제하시겠습니까?\n\n⚠️ 삭제된 전략은 목록에서 제거되며, 자동매매도 중지됩니다.\n이 작업은 되돌릴 수 없습니다.')) {
      return
    }

    try {
      const { data: strategy, error: fetchError } = await supabase
        .from('strategies')
        .select('allocated_capital, user_id')
        .eq('id', strategyId)
        .single()

      if (fetchError) throw fetchError

      const releasedCapital = strategy.allocated_capital || 0

      const { error: strategyError } = await supabase
        .from('strategies')
        .update({
          is_active: false,
          auto_execute: false,
          auto_trade_enabled: false,
          allocated_capital: 0,
          allocated_percent: 0
        })
        .eq('id', strategyId)

      if (strategyError) throw strategyError

      if (releasedCapital > 0) {
        const { data: balance, error: balanceError } = await supabase
          .from('kw_account_balance')
          .select('available_cash')
          .eq('user_id', strategy.user_id)
          .order('updated_at', { ascending: false })
          .limit(1)
          .single()

        if (balanceError) throw balanceError

        const { error: cashError } = await supabase
          .from('kw_account_balance')
          .update({
            available_cash: balance.available_cash + releasedCapital,
            updated_at: new Date().toISOString()
          })
          .eq('user_id', strategy.user_id)

        if (cashError) throw cashError
      }

      const { error: universeError } = await supabase
        .from('strategy_universes')
        .update({ is_active: false })
        .eq('strategy_id', strategyId)

      if (universeError) throw universeError

      refreshData()
      refreshData()
    } catch (error: any) {
      console.error('전략 삭제 실패:', error)

      // [NEW] Handle Session/Auth Errors explicitly
      if (error.message?.includes('JWT') || error.code === 'PGRST301' || error.status === 401) {
        alert('세션이 만료되었습니다. 페이지를 새로고침하여 다시 로그인해주세요.')
        window.location.reload()
      } else {
        alert(`전략 삭제 실패: ${error.message}`)
      }
    }
  }

  const handleEditStrategy = (strategyId: string) => {
    const strategy = activeStrategies.find(s => s.strategy_id === strategyId)
    if (strategy) {
      setEditingStrategy(strategy)
      // setShowEditDialog(true) // OLD
      // Use Config Dialog instead
      // We need to map ActiveStrategy (RPC result) to Strategy (Table row) structure roughly
      // But MyStrategyConfig just needs { id: ... } to fetch details.
      // So let's reuse editingStrategy state but open the new dialog.
      setShowEditDialog(true)
    }
  }

  // Wrapper for Config Dialog Close
  const handleConfigClose = () => {
    setShowEditDialog(false)
    setEditingStrategy(null)
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* 헤더 */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h5" fontWeight="bold" fontFamily="serif" sx={{ display: 'flex', alignItems: 'center' }}>
          <Work sx={{ mr: 1, color: 'text.primary' }} /> 자동매매 포트폴리오
        </Typography>
        <Stack direction="row" spacing={1}>
          <Button
            startIcon={<Refresh />}
            onClick={handleSyncAccount}
            variant="outlined"
            size="small"
            sx={{ whiteSpace: 'nowrap', minWidth: 'fit-content', color: 'text.primary', borderColor: 'rgba(0,0,0,0.23)' }}
          >
            계좌 동기화
          </Button>

          <Chip
            label={tradingMode === 'live' ? "실전투자" : "모의투자"}
            color={tradingMode === 'live' ? "error" : "default"}
            variant="filled"
            sx={{ fontWeight: 'bold', height: 30 }}
          />

          <Button
            startIcon={<Refresh />}
            onClick={refreshData}
            variant="outlined"
            size="small"
            sx={{ whiteSpace: 'nowrap', minWidth: 'fit-content', color: 'text.secondary', borderColor: 'rgba(0,0,0,0.23)' }}
          >
            새로고침
          </Button>
        </Stack>
      </Stack>

      {/* 포트폴리오 요약 */}
      <PortfolioOverview
        stats={portfolioStats}
        activeStrategies={activeStrategies}
        positions={positions}
        lastUpdated={lastUpdated}
      />

      {/* 새 자동매매 시작 (Top Banner) */}
      <Box sx={{ mb: 4, mt: 1 }}>
        <Paper
          elevation={0}
          sx={{
            p: 3,
            // Professional Gradient matching page tone (Dark Slate/Blue)
            background: 'linear-gradient(90deg, #263238 0%, #37474F 100%)',
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            // borderLeft: '6px solid #4CAF50', // REMOVED per user request
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}
        >
          <Box>
            <Typography variant="h6" fontWeight="bold" sx={{ color: 'white', mb: 0.5 }}>
              새로운 자동매매 전략 시작하기
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
              검증된 알고리즘을 선택하고 자금을 할당하여 자동으로 수익을 창출하세요.
            </Typography>
          </Box>

          <Button
            variant="contained"
            onClick={() => setShowAddDialog(true)}
            sx={{
              bgcolor: 'white',
              color: '#37474F',
              fontWeight: 'bold',
              px: 3,
              py: 1,
              '&:hover': {
                bgcolor: '#f5f5f5',
                transform: 'translateY(-1px)'
              }
            }}
          >
            전략 생성
          </Button>
        </Paper>
      </Box>

      {/* 보유 종목 현황 리스트 (NEW) */}
      <PortfolioHoldingsTable positions={positions} />

      {/* 활성 전략 목록 */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" fontWeight="bold" gutterBottom fontFamily="serif" sx={{ display: 'flex', alignItems: 'center' }}>
          <ShowChart sx={{ mr: 1, color: 'text.primary' }} /> 활성 전략별 현황
          <Chip label="Source: 전략설정" size="small" variant="outlined" sx={{ ml: 1, verticalAlign: 'middle', borderColor: 'text.secondary', color: 'text.secondary' }} />
          {lastUpdated && (
            <Typography variant="caption" color="text.secondary" sx={{ ml: 1, verticalAlign: 'middle' }}>
              ({lastUpdated.toLocaleString('ko-KR')})
            </Typography>
          )}
        </Typography>

        {activeStrategies.length === 0 ? (
          <Alert severity="info" sx={{ mb: 2 }}>
            활성화된 자동매매 전략이 없습니다. 아래 버튼을 클릭하여 새 전략을 추가하세요.
          </Alert>
        ) : (
          <Stack spacing={2}>
            {activeStrategies.map((strategy) => (
              <StrategyCard
                key={strategy.strategy_id}
                strategyId={strategy.strategy_id}
                strategyName={strategy.strategy_name}
                universes={strategy.universes}
                allocatedCapital={strategy.allocated_capital}
                allocatedPercent={strategy.allocated_percent}
                onStop={() => handleStopStrategy(strategy.strategy_id)}
                onEdit={() => handleEditStrategy(strategy.strategy_id)}
                onDelete={() => handleDeleteStrategy(strategy.strategy_id)}
              />
            ))}
          </Stack>
        )}
      </Box>

      {/* 전략 검증 패널 (전체 종목 스캔) */}
      <StrategyVerificationPanel />




      {/* 긴급 대응 센터 (Emergency Control) */}
      <Box sx={{ mb: 3 }}>
        <EmergencyControlPanel onOpComplete={refreshData} />
      </Box>

      {/* 자동매매 추가 다이얼로그 */}
      <AddStrategyDialog
        open={showAddDialog}
        accountNo={currentAccountNo}
        onClose={() => setShowAddDialog(false)}
        onSuccess={() => {
          refreshData()
        }}
      />

      {/* 자동매매 수정 다이얼로그 */}


      {/* 전략 설정 (MyStrategyConfig) - Replaces EditStrategyDialog */}
      {editingStrategy && (
        <MyStrategyConfig
          open={showEditDialog}
          onClose={() => {
            setShowEditDialog(false)
            setEditingStrategy(null)
          }}
          // Adapt ActiveStrategy to Strategy interface expectation (min { id, name })
          strategy={{
            id: editingStrategy.strategy_id,
            name: editingStrategy.strategy_name,
            is_active: true, // Default assumption, dialog will fetch real status
            allocated_capital: editingStrategy.allocated_capital
            // Other fields not strictly needed for fetch
          } as any}
          onSave={() => {
            refreshData()
          }}
        />
      )}

    </Box >
  )
}
