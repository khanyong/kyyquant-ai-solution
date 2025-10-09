import { supabase } from './supabase'

export interface BacktestResultData {
  id?: string
  user_id?: string
  strategy_id?: string
  strategy_name?: string
  start_date: string
  end_date: string
  test_period_start?: string
  test_period_end?: string
  initial_capital: number
  final_capital?: number
  total_return_rate: number  // 수익률 (%, percentage)
  max_drawdown: number
  sharpe_ratio?: number
  sortino_ratio?: number
  treynor_ratio?: number
  win_rate?: number
  total_trades: number
  profitable_trades?: number
  winning_trades?: number
  losing_trades?: number
  avg_profit?: number
  avg_loss?: number
  profit_factor?: number
  recovery_factor?: number
  volatility?: number
  // JSONB fields
  trades?: any
  daily_returns?: any
  equity_curve?: any
  investment_settings?: any
  strategy_conditions?: any
  filter_conditions?: any
  metadata?: any
  // Legacy fields
  results_data?: any
  trade_details?: any
  created_at?: string
  updated_at?: string
}

export const backtestStorageService = {
  async saveResult(result: BacktestResultData): Promise<{ data: any, error: any }> {
    try {
      console.log('🔐 Checking authentication...')
      const { data: userData, error: userError } = await supabase.auth.getUser()

      if (userError) {
        console.error('❌ Auth error:', userError)
        return { data: null, error: `Authentication error: ${userError.message}` }
      }

      if (!userData?.user) {
        console.error('❌ No user data found')
        return { data: null, error: 'User not authenticated' }
      }

      console.log('✅ User authenticated:', {
        userId: userData.user.id,
        email: userData.user.email
      })

      const resultToSave = {
        ...result,
        user_id: userData.user.id,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }

      console.log('💾 Attempting to save backtest result:', {
        userId: resultToSave.user_id,
        strategyName: resultToSave.strategy_name,
        totalReturnRate: resultToSave.total_return_rate
      })

      const { data, error } = await supabase
        .from('backtest_results')
        .insert([resultToSave])
        .select()
        .single()

      if (error) {
        console.error('❌ Error saving backtest result:', {
          code: error.code,
          message: error.message,
          details: error.details,
          hint: error.hint
        })
        return { data: null, error }
      }

      console.log('✅ Backtest result saved successfully:', data.id)
      return { data, error: null }
    } catch (error) {
      console.error('❌ Exception in saveResult:', error)
      return { data: null, error }
    }
  },

  async getResults(filters?: {
    user_id?: string
    strategy_name?: string
    start_date?: string
    end_date?: string
    min_return?: number
    max_return?: number
    limit?: number
    offset?: number
    order_by?: string
    order_direction?: 'asc' | 'desc'
  }): Promise<{ data: BacktestResultData[] | null, error: any }> {
    try {
      const { data: userData, error: userError } = await supabase.auth.getUser()
      
      if (userError || !userData?.user) {
        return { data: null, error: 'User not authenticated' }
      }

      let query = supabase
        .from('backtest_results')
        .select('*')
        .eq('user_id', userData.user.id)

      if (filters?.strategy_name) {
        query = query.ilike('strategy_name', `%${filters.strategy_name}%`)
      }

      if (filters?.start_date) {
        query = query.gte('start_date', filters.start_date)
      }

      if (filters?.end_date) {
        query = query.lte('end_date', filters.end_date)
      }

      if (filters?.min_return !== undefined) {
        query = query.gte('total_return_rate', filters.min_return)
      }

      if (filters?.max_return !== undefined) {
        query = query.lte('total_return_rate', filters.max_return)
      }

      const orderBy = filters?.order_by || 'created_at'
      const orderDirection = filters?.order_direction || 'desc'
      query = query.order(orderBy, { ascending: orderDirection === 'asc' })

      if (filters?.limit) {
        query = query.limit(filters.limit)
      }

      if (filters?.offset) {
        query = query.range(filters.offset, filters.offset + (filters.limit || 10) - 1)
      }

      const { data, error } = await query

      if (error) {
        console.error('Error fetching backtest results:', error)
        return { data: null, error }
      }

      return { data, error: null }
    } catch (error) {
      console.error('Error in getResults:', error)
      return { data: null, error }
    }
  },

  async getResultById(id: string): Promise<{ data: BacktestResultData | null, error: any }> {
    try {
      const { data: userData, error: userError } = await supabase.auth.getUser()
      
      if (userError || !userData?.user) {
        return { data: null, error: 'User not authenticated' }
      }

      const { data, error } = await supabase
        .from('backtest_results')
        .select('*')
        .eq('id', id)
        .eq('user_id', userData.user.id)
        .single()

      if (error) {
        console.error('Error fetching backtest result:', error)
        return { data: null, error }
      }

      return { data, error: null }
    } catch (error) {
      console.error('Error in getResultById:', error)
      return { data: null, error }
    }
  },

  async deleteResult(id: string): Promise<{ error: any }> {
    try {
      const { data: userData, error: userError } = await supabase.auth.getUser()
      
      if (userError || !userData?.user) {
        return { error: 'User not authenticated' }
      }

      const { error } = await supabase
        .from('backtest_results')
        .delete()
        .eq('id', id)
        .eq('user_id', userData.user.id)

      if (error) {
        console.error('Error deleting backtest result:', error)
        return { error }
      }

      return { error: null }
    } catch (error) {
      console.error('Error in deleteResult:', error)
      return { error }
    }
  },

  async updateResult(id: string, updates: Partial<BacktestResultData>): Promise<{ data: any, error: any }> {
    try {
      const { data: userData, error: userError } = await supabase.auth.getUser()
      
      if (userError || !userData?.user) {
        return { data: null, error: 'User not authenticated' }
      }

      const { data, error } = await supabase
        .from('backtest_results')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
        .eq('user_id', userData.user.id)
        .select()
        .single()

      if (error) {
        console.error('Error updating backtest result:', error)
        return { data: null, error }
      }

      return { data, error: null }
    } catch (error) {
      console.error('Error in updateResult:', error)
      return { data: null, error }
    }
  },

  async getResultsComparison(ids: string[]): Promise<{ data: BacktestResultData[] | null, error: any }> {
    try {
      const { data: userData, error: userError } = await supabase.auth.getUser()
      
      if (userError || !userData?.user) {
        return { data: null, error: 'User not authenticated' }
      }

      const { data, error } = await supabase
        .from('backtest_results')
        .select('*')
        .in('id', ids)
        .eq('user_id', userData.user.id)

      if (error) {
        console.error('Error fetching comparison results:', error)
        return { data: null, error }
      }

      return { data, error: null }
    } catch (error) {
      console.error('Error in getResultsComparison:', error)
      return { data: null, error }
    }
  },

  async getStatistics(): Promise<{ data: any, error: any }> {
    try {
      const { data: userData, error: userError } = await supabase.auth.getUser()
      
      if (userError || !userData?.user) {
        return { data: null, error: 'User not authenticated' }
      }

      const { data, error } = await supabase
        .from('backtest_results')
        .select('total_return_rate, sharpe_ratio, max_drawdown, win_rate, total_trades')
        .eq('user_id', userData.user.id)

      if (error) {
        console.error('Error fetching statistics:', error)
        return { data: null, error }
      }

      if (!data || data.length === 0) {
        return {
          data: {
            total_results: 0,
            avg_return: 0,
            best_return: 0,
            worst_return: 0,
            avg_sharpe: 0,
            avg_drawdown: 0,
            avg_win_rate: 0,
            total_trades: 0
          },
          error: null
        }
      }

      const stats = {
        total_results: data.length,
        avg_return: data.reduce((sum, r) => sum + (r.total_return_rate || 0), 0) / data.length,
        best_return: Math.max(...data.map(r => r.total_return_rate || 0)),
        worst_return: Math.min(...data.map(r => r.total_return_rate || 0)),
        avg_sharpe: data.reduce((sum, r) => sum + (r.sharpe_ratio || 0), 0) / data.length,
        avg_drawdown: data.reduce((sum, r) => sum + (r.max_drawdown || 0), 0) / data.length,
        avg_win_rate: data.reduce((sum, r) => sum + (r.win_rate || 0), 0) / data.length,
        total_trades: data.reduce((sum, r) => sum + (r.total_trades || 0), 0)
      }

      return { data: stats, error: null }
    } catch (error) {
      console.error('Error in getStatistics:', error)
      return { data: null, error }
    }
  }
}