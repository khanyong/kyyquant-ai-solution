import { supabase, dbOperations } from '../lib/supabase'
import type { 
  Stock, 
  PriceData, 
  RealtimePrice, 
  Order, 
  Portfolio,
  AccountBalance 
} from '../lib/supabase'

// 키움 API 데이터를 Supabase에 동기화하는 서비스
export class KiwoomSupabaseService {
  private userId: string | null = null

  constructor(userId?: string) {
    this.userId = userId || null
  }

  // 종목 정보 동기화
  async syncStockInfo(stockData: {
    code: string
    name: string
    market: 'KOSPI' | 'KOSDAQ' | 'KONEX'
    sector?: string
  }) {
    try {
      return await dbOperations.upsertStockData(stockData)
    } catch (error) {
      console.error('Failed to sync stock info:', error)
      throw error
    }
  }

  // 일별 가격 데이터 저장
  async saveDailyPriceData(priceDataArray: Array<{
    stock_code: string
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
    trading_value?: number
  }>) {
    try {
      const formattedData = priceDataArray.map(data => ({
        ...data,
        date: new Date(data.date),
        volume: BigInt(data.volume),
        trading_value: data.trading_value ? BigInt(data.trading_value) : undefined
      }))
      return await dbOperations.insertPriceData(formattedData)
    } catch (error) {
      console.error('Failed to save price data:', error)
      throw error
    }
  }

  // 실시간 가격 업데이트
  async updateRealtimePrice(stockCode: string, priceInfo: {
    current_price: number
    change_rate: number
    volume: number
    bid_price?: number
    ask_price?: number
  }) {
    try {
      return await dbOperations.updateRealtimePrice({
        stock_code: stockCode,
        ...priceInfo,
        volume: BigInt(priceInfo.volume),
        timestamp: new Date()
      })
    } catch (error) {
      console.error('Failed to update realtime price:', error)
      throw error
    }
  }

  // 주문 생성
  async createOrder(orderData: {
    stock_code: string
    order_type: 'BUY' | 'SELL'
    order_price: number
    order_quantity: number
    kiwoom_order_no?: string
  }) {
    if (!this.userId) {
      throw new Error('User ID is required for creating orders')
    }

    try {
      return await dbOperations.createOrder({
        user_id: this.userId,
        order_status: 'PENDING',
        ...orderData
      })
    } catch (error) {
      console.error('Failed to create order:', error)
      throw error
    }
  }

  // 주문 상태 업데이트
  async updateOrderStatus(orderId: string, status: {
    order_status: 'PENDING' | 'EXECUTED' | 'CANCELLED' | 'PARTIAL'
    executed_price?: number
    executed_quantity?: number
  }) {
    try {
      const { data, error } = await supabase
        .from('orders')
        .update(status)
        .eq('id', orderId)
        .select()
        .single()

      if (error) throw error
      return data
    } catch (error) {
      console.error('Failed to update order status:', error)
      throw error
    }
  }

  // 포트폴리오 업데이트
  async updatePortfolio(portfolioData: {
    stock_code: string
    quantity: number
    avg_price: number
  }) {
    if (!this.userId) {
      throw new Error('User ID is required for portfolio update')
    }

    try {
      const { data, error } = await supabase
        .from('portfolio')
        .upsert({
          user_id: this.userId,
          ...portfolioData,
          updated_at: new Date()
        })
        .select()
        .single()

      if (error) throw error
      return data
    } catch (error) {
      console.error('Failed to update portfolio:', error)
      throw error
    }
  }

  // 계좌 잔고 업데이트
  async updateAccountBalance(balanceData: {
    total_assets: number
    available_cash: number
    total_evaluation: number
    total_profit_loss?: number
    total_profit_loss_rate?: number
  }) {
    if (!this.userId) {
      throw new Error('User ID is required for balance update')
    }

    try {
      const { data, error } = await supabase
        .from('account_balance')
        .upsert({
          user_id: this.userId,
          ...balanceData,
          updated_at: new Date()
        })
        .select()
        .single()

      if (error) throw error
      return data
    } catch (error) {
      console.error('Failed to update account balance:', error)
      throw error
    }
  }

  // 시장 지수 업데이트
  async updateMarketIndex(indexData: {
    index_code: string
    index_name: string
    current_value: number
    change_value: number
    change_rate: number
    trading_volume?: number
  }) {
    try {
      const { data, error } = await supabase
        .from('market_index')
        .upsert({
          ...indexData,
          timestamp: new Date()
        })
        .select()
        .single()

      if (error) throw error
      return data
    } catch (error) {
      console.error('Failed to update market index:', error)
      throw error
    }
  }

  // 일별 가격 데이터 조회
  async getPriceHistory(stockCode: string, days: number = 30) {
    try {
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - days)

      const { data, error } = await supabase
        .from('price_data')
        .select('*')
        .eq('stock_code', stockCode)
        .gte('date', startDate.toISOString())
        .order('date', { ascending: false })

      if (error) throw error
      return data
    } catch (error) {
      console.error('Failed to get price history:', error)
      throw error
    }
  }

  // 사용자 포트폴리오 조회
  async getUserPortfolio() {
    if (!this.userId) {
      throw new Error('User ID is required')
    }

    try {
      return await dbOperations.getPortfolio(this.userId)
    } catch (error) {
      console.error('Failed to get portfolio:', error)
      throw error
    }
  }

  // 사용자 주문 내역 조회
  async getUserOrders(status?: string) {
    if (!this.userId) {
      throw new Error('User ID is required')
    }

    try {
      let query = supabase
        .from('orders')
        .select('*, stocks(*)')
        .eq('user_id', this.userId)
        .order('created_at', { ascending: false })

      if (status) {
        query = query.eq('order_status', status)
      }

      const { data, error } = await query
      if (error) throw error
      return data
    } catch (error) {
      console.error('Failed to get user orders:', error)
      throw error
    }
  }

  // 종목 검색
  async searchStocks(searchTerm: string) {
    try {
      const { data, error } = await supabase
        .from('stocks')
        .select('*')
        .or(`name.ilike.%${searchTerm}%,code.ilike.%${searchTerm}%`)
        .limit(20)

      if (error) throw error
      return data
    } catch (error) {
      console.error('Failed to search stocks:', error)
      throw error
    }
  }

  // 인기 종목 조회
  async getPopularStocks(limit: number = 10) {
    try {
      const { data, error } = await supabase
        .from('realtime_prices')
        .select('*, stocks(*)')
        .order('volume', { ascending: false })
        .limit(limit)

      if (error) throw error
      return data
    } catch (error) {
      console.error('Failed to get popular stocks:', error)
      throw error
    }
  }

  // 뉴스/공시 저장
  async saveNewsAlert(newsData: {
    stock_code?: string
    title: string
    content: string
    source: string
    url?: string
    sentiment?: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'
    importance: 'HIGH' | 'MEDIUM' | 'LOW'
    published_at: Date
  }) {
    try {
      const { data, error } = await supabase
        .from('news_alerts')
        .insert(newsData)
        .select()
        .single()

      if (error) throw error
      return data
    } catch (error) {
      console.error('Failed to save news alert:', error)
      throw error
    }
  }
}

// 싱글톤 인스턴스
let kiwoomSupabaseInstance: KiwoomSupabaseService | null = null

export const getKiwoomSupabaseService = (userId?: string) => {
  if (!kiwoomSupabaseInstance || (userId && kiwoomSupabaseInstance['userId'] !== userId)) {
    kiwoomSupabaseInstance = new KiwoomSupabaseService(userId)
  }
  return kiwoomSupabaseInstance
}