import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database Types
export interface User {
  id: string
  email: string
  name: string
  kiwoom_account?: string
  created_at: Date
  updated_at: Date
}

export interface Stock {
  code: string // 종목코드
  name: string // 종목명
  market: 'KOSPI' | 'KOSDAQ' | 'KONEX'
  sector?: string // 업종
  created_at: Date
  updated_at: Date
}

export interface PriceData {
  id: string
  stock_code: string
  date: Date
  open: number // 시가
  high: number // 고가
  low: number // 저가
  close: number // 종가
  volume: bigint // 거래량
  trading_value?: bigint // 거래대금
  created_at: Date
}

export interface RealtimePrice {
  id: string
  stock_code: string
  current_price: number // 현재가
  change_rate: number // 등락률
  volume: bigint // 거래량
  bid_price: number // 매수호가
  ask_price: number // 매도호가
  timestamp: Date
}

export interface Order {
  id: string
  user_id: string
  stock_code: string
  order_type: 'BUY' | 'SELL'
  order_status: 'PENDING' | 'EXECUTED' | 'CANCELLED' | 'PARTIAL'
  order_price: number
  order_quantity: number
  executed_price?: number
  executed_quantity?: number
  kiwoom_order_no?: string // 키움 주문번호
  created_at: Date
  updated_at: Date
}

export interface Portfolio {
  id: string
  user_id: string
  stock_code: string
  quantity: number // 보유수량
  avg_price: number // 평균단가
  current_price?: number // 현재가
  profit_loss?: number // 평가손익
  profit_loss_rate?: number // 평가손익률
  updated_at: Date
}

export interface Strategy {
  id: string
  user_id: string
  name: string
  description?: string
  type: 'TECHNICAL' | 'FUNDAMENTAL' | 'HYBRID'
  config: any // JSON 형태의 전략 설정
  is_active: boolean
  created_at: Date
  updated_at: Date
}

export interface BacktestResult {
  id: string
  strategy_id: string
  user_id: string
  start_date: Date
  end_date: Date
  initial_capital: number
  final_capital: number
  total_return_rate: number // 총 수익률 (%, percentage)
  max_drawdown: number // 최대 낙폭
  sharpe_ratio?: number // 샤프 비율
  win_rate?: number // 승률
  total_trades: number // 총 거래 횟수
  profitable_trades: number // 수익 거래 횟수
  results_data: any // 상세 백테스트 결과 JSON
  created_at: Date
}

export interface TradingSignal {
  id: string
  strategy_id: string
  stock_code: string
  signal_type: 'BUY' | 'SELL' | 'HOLD'
  signal_strength: number // 신호 강도 (0-100)
  price: number
  indicators: any // 사용된 지표 값들 JSON
  timestamp: Date
}

export interface AccountBalance {
  id: string
  user_id: string
  total_assets: number // 총 자산
  available_cash: number // 주문가능 현금
  total_evaluation: number // 총 평가금액
  total_profit_loss: number // 총 평가손익
  total_profit_loss_rate: number // 총 평가손익률
  updated_at: Date
}

export interface MarketIndex {
  id: string
  index_code: string // KOSPI, KOSDAQ 등
  index_name: string
  current_value: number
  change_value: number
  change_rate: number
  trading_volume: bigint
  timestamp: Date
}

export interface NewsAlert {
  id: string
  stock_code?: string
  title: string
  content: string
  source: string
  url?: string
  sentiment?: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'
  importance: 'HIGH' | 'MEDIUM' | 'LOW'
  published_at: Date
  created_at: Date
}

// Helper functions for database operations
export const dbOperations = {
  // 사용자 관련
  async createUser(userData: Partial<User>) {
    const { data, error } = await supabase
      .from('users')
      .insert(userData)
      .select()
      .single()
    
    if (error) throw error
    return data
  },

  // 주식 데이터 관련
  async upsertStockData(stockData: Partial<Stock>) {
    const { data, error } = await supabase
      .from('stocks')
      .upsert(stockData)
      .select()
      .single()
    
    if (error) throw error
    return data
  },

  // 가격 데이터 저장
  async insertPriceData(priceData: Partial<PriceData>[]) {
    const { data, error } = await supabase
      .from('price_data')
      .insert(priceData)
      .select()
    
    if (error) throw error
    return data
  },

  // 실시간 가격 업데이트
  async updateRealtimePrice(realtimeData: Partial<RealtimePrice>) {
    const { data, error } = await supabase
      .from('realtime_prices')
      .upsert(realtimeData)
      .select()
      .single()
    
    if (error) throw error
    return data
  },

  // 주문 생성
  async createOrder(orderData: Partial<Order>) {
    const { data, error } = await supabase
      .from('orders')
      .insert(orderData)
      .select()
      .single()
    
    if (error) throw error
    return data
  },

  // 포트폴리오 조회
  async getPortfolio(userId: string) {
    const { data, error } = await supabase
      .from('portfolio')
      .select('*, stocks(*)')
      .eq('user_id', userId)
    
    if (error) throw error
    return data
  },

  // 전략 저장
  async saveStrategy(strategyData: Partial<Strategy>) {
    const { data, error } = await supabase
      .from('strategies')
      .insert(strategyData)
      .select()
      .single()
    
    if (error) throw error
    return data
  },

  // 백테스트 결과 저장
  async saveBacktestResult(resultData: Partial<BacktestResult>) {
    const { data, error } = await supabase
      .from('backtest_results')
      .insert(resultData)
      .select()
      .single()
    
    if (error) throw error
    return data
  },

  // 거래 신호 저장
  async saveTradingSignal(signalData: Partial<TradingSignal>) {
    const { data, error } = await supabase
      .from('trading_signals')
      .insert(signalData)
      .select()
      .single()
    
    if (error) throw error
    return data
  }
}

// Realtime subscriptions
export const subscriptions = {
  // 실시간 가격 구독
  subscribeToRealtimePrices(stockCode: string, callback: (price: RealtimePrice) => void) {
    return supabase
      .channel(`realtime-price-${stockCode}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'realtime_prices',
          filter: `stock_code=eq.${stockCode}`
        },
        (payload) => {
          callback(payload.new as RealtimePrice)
        }
      )
      .subscribe()
  },

  // 주문 상태 구독
  subscribeToOrders(userId: string, callback: (order: Order) => void) {
    return supabase
      .channel(`orders-${userId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'orders',
          filter: `user_id=eq.${userId}`
        },
        (payload) => {
          callback(payload.new as Order)
        }
      )
      .subscribe()
  },

  // 거래 신호 구독
  subscribeToTradingSignals(strategyId: string, callback: (signal: TradingSignal) => void) {
    return supabase
      .channel(`signals-${strategyId}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'trading_signals',
          filter: `strategy_id=eq.${strategyId}`
        },
        (payload) => {
          callback(payload.new as TradingSignal)
        }
      )
      .subscribe()
  }
}