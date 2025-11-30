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
