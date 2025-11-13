import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Stack,
  Button,
  Collapse,
  Alert,
  CircularProgress
} from '@mui/material'
import {
  Add,
  Refresh
} from '@mui/icons-material'
import { supabase } from '../../lib/supabase'
import PortfolioOverview from './PortfolioOverview'
import StrategyCard from './StrategyCard'
import MarketMonitor from '../MarketMonitor'
import N8nWorkflowMonitor from '../N8nWorkflowMonitor'
import PendingOrdersPanel from './PendingOrdersPanel'
import AddStrategyDialog from './AddStrategyDialog'

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
  const [activeStrategies, setActiveStrategies] = useState<ActiveStrategy[]>([])
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [loading, setLoading] = useState(true)
  const [portfolioStats, setPortfolioStats] = useState({
    totalCapital: 0,
    totalAllocated: 0,
    totalInvested: 0,
    totalValue: 0,
    totalProfit: 0,
    totalProfitRate: 0,
    activeStrategiesCount: 0,
    totalPositions: 0
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      await Promise.all([
        loadActiveStrategies(),
        loadPortfolioStats()
      ])
    } catch (error) {
      console.error('데이터 로드 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadActiveStrategies = async () => {
    try {
      const { data, error } = await supabase
        .rpc('get_active_strategies_with_universe')

      if (error) throw error

      // 전략별로 그룹화
      const grouped = (data || []).reduce((acc: any, item: any) => {
        if (!acc[item.strategy_id]) {
          acc[item.strategy_id] = {
            strategy_id: item.strategy_id,
            strategy_name: item.strategy_name,
            entry_conditions: item.entry_conditions,
            exit_conditions: item.exit_conditions,
            allocated_capital: parseFloat(item.allocated_capital) || 0,
            allocated_percent: parseFloat(item.allocated_percent) || 0,
            universes: []
          }
        }
        acc[item.strategy_id].universes.push({
          filter_id: item.filter_id,
          filter_name: item.filter_name
        })
        return acc
      }, {})

      setActiveStrategies(Object.values(grouped))
    } catch (error) {
      console.error('활성 전략 로드 실패:', error)
    }
  }

  const loadPortfolioStats = async () => {
    try {
      // 1. 활성 전략의 총 할당 자금 계산
      const { data: strategyData } = await supabase
        .rpc('get_active_strategies_with_universe')

      const totalAllocated = strategyData?.reduce((sum: number, item: any) => {
        return sum + (parseFloat(item.allocated_capital) || 0)
      }, 0) || 0

      const activeStrategiesCount = new Set(strategyData?.map((item: any) => item.strategy_id)).size

      // 2. 전체 포지션 조회
      const { data: positions, error: posError } = await supabase
        .from('positions')
        .select('*')
        .eq('status', 'open')

      if (posError) throw posError

      // 3. 현재가 정보와 조인하여 평가액 계산
      let totalInvested = 0
      let totalValue = 0

      if (positions && positions.length > 0) {
        const positionsWithPrice = await Promise.all(
          positions.map(async (pos: any) => {
            const { data: priceData } = await supabase
              .from('kw_price_current')
              .select('current_price')
              .eq('stock_code', pos.stock_code)
              .single()

            const currentPrice = priceData?.current_price || pos.avg_price
            const invested = pos.avg_price * pos.quantity
            const value = currentPrice * pos.quantity

            return { invested, value }
          })
        )

        totalInvested = positionsWithPrice.reduce((sum, p) => sum + p.invested, 0)
        totalValue = positionsWithPrice.reduce((sum, p) => sum + p.value, 0)
      }

      const totalProfit = totalValue - totalInvested
      const totalProfitRate = totalInvested > 0 ? (totalProfit / totalInvested) * 100 : 0

      setPortfolioStats({
        totalCapital: totalAllocated, // 임시: 실제로는 계좌 정보에서 가져와야 함
        totalAllocated,
        totalInvested,
        totalValue,
        totalProfit,
        totalProfitRate,
        activeStrategiesCount,
        totalPositions: positions?.length || 0
      })
    } catch (error) {
      console.error('포트폴리오 통계 로드 실패:', error)
    }
  }

  const handleStopStrategy = async (strategyId: string) => {
    if (!confirm('정말 이 전략을 중지하시겠습니까?')) {
      return
    }

    try {
      // 전략 비활성화
      const { error: strategyError } = await supabase
        .from('strategies')
        .update({
          auto_execute: false,
          auto_trade_enabled: false
        })
        .eq('id', strategyId)

      if (strategyError) throw strategyError

      // 연결된 유니버스 비활성화
      const { error: universeError } = await supabase
        .from('strategy_universes')
        .update({ is_active: false })
        .eq('strategy_id', strategyId)

      if (universeError) throw universeError

      // 데이터 새로고침
      loadData()
    } catch (error: any) {
      console.error('전략 중지 실패:', error)
      alert(`전략 중지 실패: ${error.message}`)
    }
  }

  const handleEditStrategy = (strategyId: string) => {
    // TODO: 전략 수정 다이얼로그 열기
    alert('전략 수정 기능은 준비 중입니다.')
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
        <Typography variant="h5" fontWeight="bold">
          💼 자동매매 포트폴리오
        </Typography>
        <Button
          startIcon={<Refresh />}
          onClick={loadData}
          variant="outlined"
          size="small"
        >
          새로고침
        </Button>
      </Stack>

      {/* 포트폴리오 요약 */}
      <PortfolioOverview stats={portfolioStats} />

      {/* 활성 전략 목록 */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          📈 활성 전략별 현황
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
              />
            ))}
          </Stack>
        )}
      </Box>

      {/* 새 자동매매 시작 */}
      <Box sx={{ mb: 3 }}>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setShowAddDialog(true)}
          fullWidth
          size="large"
        >
          ➕ 새 자동매매 시작
        </Button>
      </Box>

      {/* 자동매매 추가 다이얼로그 */}
      <AddStrategyDialog
        open={showAddDialog}
        onClose={() => setShowAddDialog(false)}
        onSuccess={() => {
          loadData()
        }}
      />

      {/* 대기중인 주문 */}
      <Box sx={{ mb: 3 }}>
        <PendingOrdersPanel />
      </Box>

      {/* n8n 워크플로우 활동 */}
      <Box sx={{ mb: 3 }}>
        <N8nWorkflowMonitor />
      </Box>

      {/* 실시간 시장 모니터링 */}
      <Box sx={{ mb: 3 }}>
        <MarketMonitor />
      </Box>
    </Box>
  )
}
