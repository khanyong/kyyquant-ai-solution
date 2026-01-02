/**
 * 전략 관리 서비스
 * Supabase와 연동하여 전략 CRUD 및 실시간 업데이트 처리
 */

import { supabase } from '@/lib/supabase'
import { RealtimeChannel } from '@supabase/supabase-js'

export interface Strategy {
  id: string
  user_id: string
  name: string
  description: string
  is_active: boolean
  conditions: {
    entry: {
      rsi?: { operator: string; value: number }
      volume?: { operator: string; value: string }
      price?: { operator: string; value: string }
      macd?: { operator: string; value: any }
      bollinger?: { operator: string; value: any }
    }
    exit: {
      profit_target: number
      stop_loss: number
      trailing_stop?: number
    }
  }
  position_size: number
  max_positions: number
  allocated_capital?: number  // 전략에 할당된 자금 (원)
  allocated_percent?: number  // 전체 계좌 잔고 대비 할당 비율 (%)
  execution_time?: {
    start: string
    end: string
  }
  total_trades?: number
  win_rate?: number
  total_profit?: number
  created_at?: string
  updated_at?: string
  // Join된 프로필 정보
  profiles?: {
    name: string
  }
  backtest_metrics?: {
    best_return: number
    avg_return?: number
    win_rate: number
    report_id: string
    mdd?: number
    total_trades?: number
    start_date?: string
    end_date?: string
  }
  backtest_count?: number
  backtest_history?: any[] // Detailed history for drill-down
  universes?: { id: string, name: string }[]
}

export interface TradingSignal {
  id: string
  strategy_id: string
  stock_code: string
  stock_name: string
  signal_type: 'BUY' | 'SELL' | 'HOLD'
  signal_strength: number
  current_price: number
  volume: number
  indicators?: any
  created_at: string
}


export interface Position {
  id: string
  strategy_id: string
  stock_code: string
  stock_name: string
  quantity: number
  avg_price: number
  current_price: number
  unrealized_pnl: number
  unrealized_pnl_rate: number
  entry_time: string
  is_active: boolean
  target_price?: number
  stop_loss_price?: number
}

export interface StrategyExecution {
  id: string
  strategy_id: string
  execution_time: string
  status: 'running' | 'completed' | 'failed'
  scanned_stocks: number
  signals_generated: number
  orders_placed: number
  error_message?: string
}

class StrategyService {
  private realtimeChannel: RealtimeChannel | null = null
  private signalChannel: RealtimeChannel | null = null

  /**
   * 전략 목록 조회
   */
  async getStrategies(userId?: string): Promise<Strategy[]> {
    try {
      let query = supabase.from('strategies').select('*')

      if (userId) {
        query = query.eq('user_id', userId)
      }

      const { data, error } = await query.order('created_at', { ascending: false })

      if (error) throw error
      return data || []
    } catch (error) {
      console.error('전략 조회 실패:', error)
      return []
    }
  }

  /**
   * 전략 마켓용 전략 목록 조회 (전체 공개 전략)
   * 수익률 순으로 정렬하여 반환
   */
  /**
   * Backtest 결과와 Profile 정보를 수동으로 병합하여 안정성 확보
   */
  async getMarketStrategies(): Promise<Strategy[]> {
    try {
      // 1. 전략 조회 (활성 여부 관계없이 조회, 최근 생성된 순)
      // 사용자가 백테스트만 수행한 전략도 마켓에 표시되기를 원함
      const { data: strategies, error } = await supabase
        .from('strategies')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(500)

      if (error) throw error
      if (!strategies || strategies.length === 0) return []

      // 2. 작성자 정보 조회 (user_id 기반)
      const userIds = Array.from(new Set(strategies.map(s => s.user_id).filter(id => id)))

      let profileMap = new Map<string, { name: string }>()
      if (userIds.length > 0) {
        try {
          const { data: profiles } = await supabase
            .from('profiles')
            .select('id, name')
            .in('id', userIds)

          if (profiles) {
            profiles.forEach((p: any) => profileMap.set(p.id, { name: p.name }))
          }
        } catch (e) {
          console.warn('프로필 정보 조회 실패:', e)
        }
      }

      // 3. 백테스트 결과 조회 (strategy_id 기반)
      const strategyIds = strategies.map(s => s.id)

      // Store ALL backtests per strategy for aggregation
      let backtestsByStrategy = new Map<string, any[]>()

      if (strategyIds.length > 0) {
        try {
          // Fetch ALL backtests for these strategies to aggregate
          const { data: backtests } = await supabase
            .from('backtest_results')
            .select('strategy_id, total_return_rate, win_rate, id, max_drawdown, total_trades, start_date, end_date, created_at, sharpe_ratio, sortino_ratio')
            .in('strategy_id', strategyIds)
            .order('created_at', { ascending: false }) // Sort by date for history

          if (backtests) {
            backtests.forEach(bt => {
              const list = backtestsByStrategy.get(bt.strategy_id) || []
              list.push(bt)
              backtestsByStrategy.set(bt.strategy_id, list)
            })
          }
        } catch (e) {
          console.warn('백테스트 정보 조회 실패:', e)
        }
      }


      // Fetch Universe Links
      const universesByStrategy = new Map<string, { id: string, name: string }[]>()
      if (strategyIds.length > 0) {
        try {
          // 1. Link strategy to filters
          const { data: links } = await supabase
            .from('strategy_universes')
            .select('strategy_id, investment_filter_id')
            .in('strategy_id', strategyIds)
            .eq('is_active', true)

          if (links && links.length > 0) {
            const filterIds = Array.from(new Set(links.map(l => l.investment_filter_id)))
            // 2. Fetch filter details
            if (filterIds.length > 0) {
              const { data: filters } = await supabase
                .from('kw_investment_filters')
                .select('id, name')
                .in('id', filterIds)

              const filterMap = new Map<string, string>()
              filters?.forEach(f => filterMap.set(f.id, f.name))

              links.forEach(l => {
                const filterName = filterMap.get(l.investment_filter_id)
                if (filterName) {
                  const list = universesByStrategy.get(l.strategy_id) || []
                  list.push({ id: l.investment_filter_id, name: filterName })
                  universesByStrategy.set(l.strategy_id, list)
                }
              })
            }
          }
        } catch (e) {
          console.warn('유니버스 정보 조회 실패:', e)
        }
      }

      // 4. 데이터 병합
      const mergedStrategies = strategies.map(s => {
        const profile = profileMap.get(s.user_id)
        const history = backtestsByStrategy.get(s.id) || []

        let bestRun: any = null
        let avgReturn = 0
        let avgWinRate = 0

        if (history.length > 0) {
          // Find Best Run by Total Return
          bestRun = history.reduce((prev, current) => (Number(prev.total_return_rate || 0) > Number(current.total_return_rate || 0)) ? prev : current)

          // Calculate Averages
          const totalRet = history.reduce((sum, item) => sum + Number(item.total_return_rate || 0), 0)
          avgReturn = totalRet / history.length

          const totalWin = history.reduce((sum, item) => sum + Number(item.win_rate || 0), 0)
          avgWinRate = totalWin / history.length
        }

        return {
          ...s,
          profiles: profile || { name: 'Unknown' },
          universes: universesByStrategy.get(s.id) || [],
          backtest_count: history.length,
          backtest_history: history,
          backtest_metrics: bestRun ? {
            best_return: bestRun.total_return_rate,
            avg_return: avgReturn,
            win_rate: bestRun.win_rate, // Show best run's win rate or average? Usually Best Context shows Best metrics.
            report_id: bestRun.id,
            mdd: bestRun.max_drawdown,
            total_trades: bestRun.total_trades,
            start_date: bestRun.start_date,
            end_date: bestRun.end_date
          } : undefined
        }
      })

      // 5. 정렬: (실전 수익률 vs 백테스트 수익률) 중 더 높은 것을 기준으로 내림차순 정렬
      mergedStrategies.sort((a, b) => {
        const aReturn = Math.max(a.total_profit || -Infinity, a.backtest_metrics?.avg_return || -Infinity)
        const bReturn = Math.max(b.total_profit || -Infinity, b.backtest_metrics?.avg_return || -Infinity)

        // 둘 다 -Infinity인 경우 (데이터 없음)
        if (aReturn === -Infinity && bReturn === -Infinity) return 0
        if (aReturn === -Infinity) return 1
        if (bReturn === -Infinity) return -1

        return bReturn - aReturn
      })

      return mergedStrategies
    } catch (error) {
      console.error('마켓 전략 조회 실패:', error)
      return []
    }
  }

  /**
   * 전략 복사 (가져오기)
   */
  async copyStrategy(originalStrategyId: string): Promise<Strategy | null> {
    try {
      // 1. 원본 전략 조회
      const original = await this.getStrategy(originalStrategyId)
      if (!original) throw new Error('전략을 찾을 수 없습니다')

      // 2. 현재 사용자 확인
      const user = await supabase.auth.getUser()
      if (!user.data.user) throw new Error('로그인이 필요합니다')

      // 3. 복사본 생성
      const newStrategy: Partial<Strategy> = {
        user_id: user.data.user.id,
        name: `[Copy] ${original.name}`,
        description: original.description,
        is_active: false, // 복사 시 비활성 상태로 시작
        conditions: original.conditions,
        position_size: original.position_size,
        max_positions: original.max_positions,
        // 성과 지표 초기화
        total_trades: 0,
        win_rate: 0,
        total_profit: 0,
        allocated_capital: 0,
        allocated_percent: 0
      }

      return await this.createStrategy(newStrategy)
    } catch (error) {
      console.error('전략 복사 실패:', error)
      return null
    }
  }

  /**
   * 전략 상세 조회
   */
  async getStrategy(strategyId: string): Promise<Strategy | null> {
    try {
      const { data, error } = await supabase
        .from('strategies')
        .select('*')
        .eq('id', strategyId)
        .single()

      if (error) throw error
      return data
    } catch (error) {
      console.error('전략 상세 조회 실패:', error)
      return null
    }
  }

  /**
   * 전략 생성
   */
  async createStrategy(strategy: Partial<Strategy>): Promise<Strategy | null> {
    try {
      const user = await supabase.auth.getUser()
      if (!user.data.user) throw new Error('로그인이 필요합니다')

      const { data, error } = await supabase
        .from('strategies')
        .insert({
          ...strategy,
          user_id: user.data.user.id,
          is_active: false,
          total_trades: 0,
          win_rate: 0,
          total_profit: 0
        })
        .select()
        .single()

      if (error) throw error
      return data
    } catch (error) {
      console.error('전략 생성 실패:', error)
      return null
    }
  }

  /**
   * 전략 업데이트
   */
  async updateStrategy(strategyId: string, updates: Partial<Strategy>): Promise<boolean> {
    try {
      const { error } = await supabase
        .from('strategies')
        .update(updates)
        .eq('id', strategyId)

      if (error) throw error
      return true
    } catch (error) {
      console.error('전략 업데이트 실패:', error)
      return false
    }
  }

  /**
   * 전략 삭제
   */
  async deleteStrategy(strategyId: string): Promise<boolean> {
    try {
      const { error } = await supabase
        .from('strategies')
        .delete()
        .eq('id', strategyId)

      if (error) throw error
      return true
    } catch (error) {
      console.error('전략 삭제 실패:', error)
      return false
    }
  }

  /**
   * 전략 활성화/비활성화
   */
  async toggleStrategy(strategyId: string, isActive: boolean): Promise<boolean> {
    return this.updateStrategy(strategyId, { is_active: isActive })
  }

  /**
   * 전략 실행
   */
  async executeStrategy(strategyId: string, testMode: boolean = true): Promise<StrategyExecution | null> {
    try {
      // API 호출로 전략 실행
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/strategies/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_id: strategyId,
          test_mode: testMode
        })
      })

      const data = await response.json()
      if (data.success) {
        return data.execution
      }
      throw new Error(data.message || '전략 실행 실패')
    } catch (error) {
      console.error('전략 실행 실패:', error)
      return null
    }
  }

  /**
   * 전략 실행 기록 조회
   */
  async getExecutions(strategyId: string): Promise<StrategyExecution[]> {
    try {
      const { data, error } = await supabase
        .from('strategy_executions')
        .select('*')
        .eq('strategy_id', strategyId)
        .order('execution_time', { ascending: false })
        .limit(10)

      if (error) throw error
      return data || []
    } catch (error) {
      console.error('실행 기록 조회 실패:', error)
      return []
    }
  }

  /**
   * 매매 신호 조회
   */
  async getSignals(strategyId?: string, limit: number = 20): Promise<TradingSignal[]> {
    try {
      let query = supabase
        .from('trading_signals')
        .select('*')

      if (strategyId) {
        query = query.eq('strategy_id', strategyId)
      }

      const { data, error } = await query
        .order('created_at', { ascending: false })
        .limit(limit)

      if (error) throw error
      return data || []
    } catch (error) {
      console.error('신호 조회 실패:', error)
      return []
    }
  }

  /**
   * 포지션 조회
   */
  async getPositions(strategyId?: string): Promise<Position[]> {
    try {
      let query = supabase
        .from('positions')
        .select('*')
        .eq('is_active', true)

      if (strategyId) {
        query = query.eq('strategy_id', strategyId)
      }

      const { data, error } = await query.order('entry_time', { ascending: false })

      if (error) throw error
      return data || []
    } catch (error) {
      console.error('포지션 조회 실패:', error)
      return []
    }
  }

  /**
   * 전략 성과 조회
   */
  async getPerformance(strategyId: string): Promise<any> {
    try {
      // 포지션에서 성과 계산
      const { data: positions, error } = await supabase
        .from('positions')
        .select('*')
        .eq('strategy_id', strategyId)

      if (error) throw error

      let totalProfit = 0
      let winCount = 0
      let loseCount = 0
      let activePositions = 0

      positions?.forEach(pos => {
        if (pos.is_active) {
          activePositions++
          totalProfit += pos.unrealized_pnl || 0
        } else {
          const pnl = pos.realized_pnl || 0
          totalProfit += pnl
          if (pnl > 0) winCount++
          else if (pnl < 0) loseCount++
        }
      })

      const totalTrades = winCount + loseCount
      const winRate = totalTrades > 0 ? (winCount / totalTrades) * 100 : 0

      return {
        totalProfit,
        winCount,
        loseCount,
        totalTrades,
        winRate,
        activePositions
      }
    } catch (error) {
      console.error('성과 조회 실패:', error)
      return null
    }
  }

  /**
   * 실시간 전략 업데이트 구독
   */
  subscribeToStrategies(callback: (payload: any) => void): RealtimeChannel {
    this.unsubscribeFromStrategies()

    this.realtimeChannel = supabase
      .channel('strategies-changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'strategies'
        },
        (payload) => {
          console.log('전략 업데이트:', payload)
          callback(payload)
        }
      )
      .subscribe()

    return this.realtimeChannel
  }

  /**
   * 실시간 신호 구독
   */
  subscribeToSignals(strategyId: string, callback: (signal: TradingSignal) => void): RealtimeChannel {
    this.unsubscribeFromSignals()

    this.signalChannel = supabase
      .channel('signals-changes')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'trading_signals',
          filter: `strategy_id=eq.${strategyId}`
        },
        (payload) => {
          console.log('새 신호:', payload)
          callback(payload.new as TradingSignal)
        }
      )
      .subscribe()

    return this.signalChannel
  }

  /**
   * 구독 해제
   */
  unsubscribeFromStrategies() {
    if (this.realtimeChannel) {
      supabase.removeChannel(this.realtimeChannel)
      this.realtimeChannel = null
    }
  }

  unsubscribeFromSignals() {
    if (this.signalChannel) {
      supabase.removeChannel(this.signalChannel)
      this.signalChannel = null
    }
  }

  /**
   * 모든 구독 해제
   */
  unsubscribeAll() {
    this.unsubscribeFromStrategies()
    this.unsubscribeFromSignals()
  }
}

export const strategyService = new StrategyService()
export default strategyService
