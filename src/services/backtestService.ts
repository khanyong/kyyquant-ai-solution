import { supabase } from '../lib/supabase'

// 백테스트 관련 타입 정의
export interface BacktestResult {
  id: string
  strategy_id: string
  strategy_name: string
  user_id: string
  start_date: string
  end_date: string
  initial_capital: number
  final_capital: number
  total_return: number
  annual_return: number
  max_drawdown: number
  max_drawdown_duration: number
  volatility: number
  sharpe_ratio: number
  sortino_ratio: number
  calmar_ratio: number
  beta: number
  alpha: number
  win_rate: number
  total_trades: number
  profitable_trades: number
  avg_win: number
  avg_loss: number
  profit_factor: number
  avg_holding_days: number
  max_consecutive_wins: number
  max_consecutive_losses: number
  max_positions: number
  avg_positions: number
  turnover: number
  results_data: any
  created_at: string
}

export interface BacktestTrade {
  id: string
  backtest_id: string
  trade_date: string
  stock_code: string
  stock_name: string
  action: 'BUY' | 'SELL'
  price: number
  quantity: number
  amount: number
  commission: number
  returns: number
  holding_days: number
  profit_loss: number
}

export interface BacktestDailyReturn {
  id: string
  backtest_id: string
  date: string
  portfolio_value: number
  daily_return: number
  cumulative_return: number
  drawdown: number
  positions_count: number
  cash_balance: number
}

export interface BacktestMonthlyReturn {
  id: string
  backtest_id: string
  year: number
  month: number
  monthly_return: number
  trades_count: number
  win_rate: number
  avg_gain: number
  avg_loss: number
}

export interface BacktestSectorPerformance {
  id: string
  backtest_id: string
  sector: string
  trades_count: number
  total_return: number
  win_rate: number
  avg_return: number
  total_profit: number
  total_loss: number
  best_trade: number
  worst_trade: number
  avg_holding_days: number
}

export interface BacktestRiskMetric {
  id: string
  backtest_id: string
  metric_name: string
  metric_value: number
  metric_description: string
}

export interface BacktestPosition {
  id: string
  backtest_id: string
  date: string
  stock_code: string
  stock_name: string
  quantity: number
  avg_price: number
  current_price: number
  market_value: number
  unrealized_pnl: number
  weight: number
}

export interface BacktestBenchmark {
  id: string
  backtest_id: string
  benchmark_name: string
  total_return: number
  annual_return: number
  volatility: number
  sharpe_ratio: number
  correlation: number
}

export interface BacktestSummaryStats {
  id: string
  backtest_id: string
  stat_category: string
  stat_name: string
  stat_value: number
  stat_unit: string
}

// 백테스트 서비스 클래스
export class BacktestService {
  // 백테스트 결과 목록 조회
  static async getBacktestResults(userId?: string) {
    try {
      let query = supabase
        .from('backtest_results')
        .select('*')
        .order('created_at', { ascending: false })

      if (userId) {
        query = query.eq('user_id', userId)
      }

      const { data, error } = await query

      if (error) throw error
      return data as BacktestResult[]
    } catch (error) {
      console.error('Error fetching backtest results:', error)
      throw error
    }
  }

  // 특정 백테스트 결과 상세 조회
  static async getBacktestDetail(backtestId: string) {
    try {
      const { data, error } = await supabase
        .from('backtest_results')
        .select('*')
        .eq('id', backtestId)
        .single()

      if (error) throw error
      return data as BacktestResult
    } catch (error) {
      console.error('Error fetching backtest detail:', error)
      throw error
    }
  }

  // 백테스트 거래 내역 조회
  static async getBacktestTrades(backtestId: string) {
    try {
      const { data, error } = await supabase
        .from('backtest_trades')
        .select('*')
        .eq('backtest_id', backtestId)
        .order('trade_date', { ascending: false })

      if (error) throw error
      return data as BacktestTrade[]
    } catch (error) {
      console.error('Error fetching backtest trades:', error)
      throw error
    }
  }

  // 백테스트 일별 수익률 조회
  static async getBacktestDailyReturns(backtestId: string) {
    try {
      const { data, error } = await supabase
        .from('backtest_daily_returns')
        .select('*')
        .eq('backtest_id', backtestId)
        .order('date', { ascending: true })

      if (error) throw error
      return data as BacktestDailyReturn[]
    } catch (error) {
      console.error('Error fetching daily returns:', error)
      throw error
    }
  }

  // 백테스트 월별 수익률 조회
  static async getBacktestMonthlyReturns(backtestId: string) {
    try {
      const { data, error } = await supabase
        .from('backtest_monthly_returns')
        .select('*')
        .eq('backtest_id', backtestId)
        .order('year', { ascending: true })
        .order('month', { ascending: true })

      if (error) throw error
      return data as BacktestMonthlyReturn[]
    } catch (error) {
      console.error('Error fetching monthly returns:', error)
      throw error
    }
  }

  // 백테스트 섹터별 성과 조회
  static async getBacktestSectorPerformance(backtestId: string) {
    try {
      const { data, error } = await supabase
        .from('backtest_sector_performance')
        .select('*')
        .eq('backtest_id', backtestId)
        .order('total_return', { ascending: false })

      if (error) throw error
      return data as BacktestSectorPerformance[]
    } catch (error) {
      console.error('Error fetching sector performance:', error)
      throw error
    }
  }

  // 백테스트 리스크 지표 조회
  static async getBacktestRiskMetrics(backtestId: string) {
    try {
      const { data, error } = await supabase
        .from('backtest_risk_metrics')
        .select('*')
        .eq('backtest_id', backtestId)

      if (error) throw error
      return data as BacktestRiskMetric[]
    } catch (error) {
      console.error('Error fetching risk metrics:', error)
      throw error
    }
  }

  // 백테스트 포지션 히스토리 조회
  static async getBacktestPositions(backtestId: string, date?: string) {
    try {
      let query = supabase
        .from('backtest_positions')
        .select('*')
        .eq('backtest_id', backtestId)

      if (date) {
        query = query.eq('date', date)
      }

      query = query.order('date', { ascending: false })

      const { data, error } = await query

      if (error) throw error
      return data as BacktestPosition[]
    } catch (error) {
      console.error('Error fetching positions:', error)
      throw error
    }
  }

  // 백테스트 벤치마크 비교 조회
  static async getBacktestBenchmark(backtestId: string) {
    try {
      const { data, error } = await supabase
        .from('backtest_benchmark')
        .select('*')
        .eq('backtest_id', backtestId)

      if (error) throw error
      return data as BacktestBenchmark[]
    } catch (error) {
      console.error('Error fetching benchmark:', error)
      throw error
    }
  }

  // 백테스트 요약 통계 조회
  static async getBacktestSummaryStats(backtestId: string, category?: string) {
    try {
      let query = supabase
        .from('backtest_summary_stats')
        .select('*')
        .eq('backtest_id', backtestId)

      if (category) {
        query = query.eq('stat_category', category)
      }

      const { data, error } = await query

      if (error) throw error
      return data as BacktestSummaryStats[]
    } catch (error) {
      console.error('Error fetching summary stats:', error)
      throw error
    }
  }

  // 여러 백테스트 결과 비교
  static async compareBacktests(backtestIds: string[]) {
    try {
      const { data, error } = await supabase
        .from('backtest_results')
        .select('*')
        .in('id', backtestIds)

      if (error) throw error
      return data as BacktestResult[]
    } catch (error) {
      console.error('Error comparing backtests:', error)
      throw error
    }
  }

  // 백테스트 결과 저장
  static async saveBacktestResult(result: Partial<BacktestResult>) {
    try {
      const { data, error } = await supabase
        .from('backtest_results')
        .insert(result)
        .select()
        .single()

      if (error) throw error
      return data as BacktestResult
    } catch (error) {
      console.error('Error saving backtest result:', error)
      throw error
    }
  }

  // 백테스트 거래 내역 저장
  static async saveBacktestTrades(trades: Partial<BacktestTrade>[]) {
    try {
      const { data, error } = await supabase
        .from('backtest_trades')
        .insert(trades)
        .select()

      if (error) throw error
      return data as BacktestTrade[]
    } catch (error) {
      console.error('Error saving backtest trades:', error)
      throw error
    }
  }

  // 백테스트 일별 수익률 저장
  static async saveBacktestDailyReturns(returns: Partial<BacktestDailyReturn>[]) {
    try {
      const { data, error } = await supabase
        .from('backtest_daily_returns')
        .insert(returns)
        .select()

      if (error) throw error
      return data as BacktestDailyReturn[]
    } catch (error) {
      console.error('Error saving daily returns:', error)
      throw error
    }
  }

  // 백테스트 월별 수익률 저장
  static async saveBacktestMonthlyReturns(returns: Partial<BacktestMonthlyReturn>[]) {
    try {
      const { data, error } = await supabase
        .from('backtest_monthly_returns')
        .insert(returns)
        .select()

      if (error) throw error
      return data as BacktestMonthlyReturn[]
    } catch (error) {
      console.error('Error saving monthly returns:', error)
      throw error
    }
  }

  // 백테스트 섹터별 성과 저장
  static async saveBacktestSectorPerformance(performance: Partial<BacktestSectorPerformance>[]) {
    try {
      const { data, error } = await supabase
        .from('backtest_sector_performance')
        .insert(performance)
        .select()

      if (error) throw error
      return data as BacktestSectorPerformance[]
    } catch (error) {
      console.error('Error saving sector performance:', error)
      throw error
    }
  }

  // 백테스트 삭제
  static async deleteBacktest(backtestId: string) {
    try {
      const { error } = await supabase
        .from('backtest_results')
        .delete()
        .eq('id', backtestId)

      if (error) throw error
      return true
    } catch (error) {
      console.error('Error deleting backtest:', error)
      throw error
    }
  }

  // 실시간 백테스트 진행 상황 구독
  static subscribeToBacktestProgress(backtestId: string, callback: (progress: any) => void) {
    return supabase
      .channel(`backtest-progress-${backtestId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'backtest_execution_logs',
          filter: `backtest_id=eq.${backtestId}`
        },
        (payload) => {
          callback(payload.new)
        }
      )
      .subscribe()
  }

  // 최근 백테스트 결과 요약 조회
  static async getRecentBacktestsSummary(userId: string, limit: number = 5) {
    try {
      const { data, error } = await supabase
        .from('backtest_results')
        .select('id, strategy_name, total_return, sharpe_ratio, win_rate, created_at')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(limit)

      if (error) throw error
      return data
    } catch (error) {
      console.error('Error fetching recent backtests:', error)
      throw error
    }
  }

  // 백테스트 목록 조회
  static async getBacktestList() {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('User not authenticated')

      const { data, error } = await supabase
        .from('backtest_results')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })

      if (error) throw error
      return data || []
    } catch (error) {
      console.error('Error fetching backtest list:', error)
      return []
    }
  }
}