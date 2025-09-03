import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

const supabase = createClient(supabaseUrl, supabaseAnonKey)

export interface StockPrice {
  stock_code: string
  stock_name?: string
  current_price: number
  change: number
  change_rate: number
  volume: number
  timestamp: string
}

export interface Portfolio {
  stock_code: string
  stock_name: string
  quantity: number
  avg_price: number
  current_price: number
  profit_loss: number
  profit_rate: number
}

export interface Order {
  stock_code: string
  stock_name?: string
  order_type: 'BUY' | 'SELL'
  order_method: 'LIMIT' | 'MARKET'
  quantity: number
  price: number
  status: 'PENDING' | 'PARTIAL' | 'EXECUTED' | 'CANCELLED'
}

class KiwoomService {
  private ws: WebSocket | null = null
  private wsUrl = import.meta.env.VITE_KIWOOM_WS_URL || 'ws://localhost:8765'
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  
  constructor() {
    this.connect()
    this.setupRealtimeSubscriptions()
  }
  
  private connect() {
    try {
      this.ws = new WebSocket(this.wsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket 연결 성공')
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.handleMessage(data)
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket 오류:', error)
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket 연결 종료')
        this.handleReconnect()
      }
    } catch (error) {
      console.error('WebSocket 연결 실패:', error)
      this.handleReconnect()
    }
  }
  
  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`)
      setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts)
    }
  }
  
  private handleMessage(data: any) {
    switch (data.type) {
      case 'stock_update':
        // 실시간 주식 데이터 처리
        this.handleStockUpdate(data.data)
        break
      case 'balance_update':
        // 잔고 업데이트 처리
        this.handleBalanceUpdate(data.data)
        break
      case 'order_executed':
        // 주문 체결 처리
        this.handleOrderExecuted(data.data)
        break
      default:
        console.log('Unknown message type:', data.type)
    }
  }
  
  private handleStockUpdate(data: StockPrice) {
    // Redux store 업데이트 또는 이벤트 발생
    window.dispatchEvent(new CustomEvent('stockUpdate', { detail: data }))
  }
  
  private handleBalanceUpdate(data: Portfolio[]) {
    window.dispatchEvent(new CustomEvent('balanceUpdate', { detail: data }))
  }
  
  private handleOrderExecuted(data: any) {
    window.dispatchEvent(new CustomEvent('orderExecuted', { detail: data }))
  }
  
  // Supabase Realtime 구독 설정
  private setupRealtimeSubscriptions() {
    // 실시간 주가 구독
    supabase
      .channel('stock-prices')
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'stock_prices'
      }, (payload) => {
        this.handleStockUpdate(payload.new as StockPrice)
      })
      .subscribe()
    
    // 포트폴리오 변경 구독
    supabase
      .channel('portfolio')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'portfolio'
      }, (payload) => {
        console.log('Portfolio changed:', payload)
      })
      .subscribe()
    
    // 주문 상태 변경 구독
    supabase
      .channel('orders')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'orders'
      }, (payload) => {
        console.log('Order status changed:', payload)
      })
      .subscribe()
  }
  
  // WebSocket을 통한 명령 전송
  private sendCommand(command: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(command))
    } else {
      console.error('WebSocket not connected')
    }
  }
  
  // 실시간 데이터 구독
  subscribeStock(stockCode: string) {
    this.sendCommand({
      type: 'subscribe',
      stock_code: stockCode
    })
  }
  
  // 실시간 데이터 구독 해제
  unsubscribeStock(stockCode: string) {
    this.sendCommand({
      type: 'unsubscribe',
      stock_code: stockCode
    })
  }
  
  // 주문 전송
  async sendOrder(order: Order): Promise<boolean> {
    return new Promise((resolve) => {
      const handleOrderResult = (event: MessageEvent) => {
        const data = JSON.parse(event.data)
        if (data.type === 'order_result') {
          this.ws?.removeEventListener('message', handleOrderResult)
          resolve(data.success)
        }
      }
      
      if (this.ws) {
        this.ws.addEventListener('message', handleOrderResult)
        this.sendCommand({
          type: 'order',
          order_data: {
            stock_code: order.stock_code,
            order_type: order.order_type === 'BUY' ? 1 : 2,
            quantity: order.quantity,
            price: order.price,
            hoga_gb: order.order_method === 'MARKET' ? '03' : '00'
          }
        })
      } else {
        resolve(false)
      }
    })
  }
  
  // 잔고 조회
  requestBalance() {
    this.sendCommand({
      type: 'get_balance'
    })
  }
  
  // Supabase에서 데이터 조회
  async getStockPrices(stockCode: string, limit = 100) {
    const { data, error } = await supabase
      .from('stock_prices')
      .select('*')
      .eq('stock_code', stockCode)
      .order('timestamp', { ascending: false })
      .limit(limit)
    
    if (error) {
      console.error('Error fetching stock prices:', error)
      return []
    }
    
    return data
  }
  
  async getPortfolio() {
    const { data, error } = await supabase
      .from('portfolio')
      .select('*')
      .order('stock_code')
    
    if (error) {
      console.error('Error fetching portfolio:', error)
      return []
    }
    
    return data
  }
  
  async getOrders(status?: string) {
    let query = supabase
      .from('orders')
      .select('*')
      .order('order_time', { ascending: false })
    
    if (status) {
      query = query.eq('status', status)
    }
    
    const { data, error } = await query
    
    if (error) {
      console.error('Error fetching orders:', error)
      return []
    }
    
    return data
  }
  
  async getWatchlist() {
    const { data, error } = await supabase
      .from('watchlist')
      .select('*')
      .eq('is_monitoring', true)
      .order('created_at', { ascending: false })
    
    if (error) {
      console.error('Error fetching watchlist:', error)
      return []
    }
    
    return data
  }
  
  async addToWatchlist(stockCode: string, stockName: string, targetPrice?: number) {
    const { data, error } = await supabase
      .from('watchlist')
      .insert({
        stock_code: stockCode,
        stock_name: stockName,
        target_price: targetPrice
      })
    
    if (error) {
      console.error('Error adding to watchlist:', error)
      return false
    }
    
    // WebSocket으로도 구독 시작
    this.subscribeStock(stockCode)
    
    return true
  }
  
  async removeFromWatchlist(stockCode: string) {
    const { error } = await supabase
      .from('watchlist')
      .delete()
      .eq('stock_code', stockCode)
    
    if (error) {
      console.error('Error removing from watchlist:', error)
      return false
    }
    
    // WebSocket 구독 해제
    this.unsubscribeStock(stockCode)
    
    return true
  }
  
  // 일봉 데이터 조회
  async getDailyPrices(stockCode: string, days = 30) {
    const { data, error } = await supabase
      .from('daily_prices')
      .select('*')
      .eq('stock_code', stockCode)
      .order('trade_date', { ascending: false })
      .limit(days)
    
    if (error) {
      console.error('Error fetching daily prices:', error)
      return []
    }
    
    return data.reverse() // 차트를 위해 오래된 데이터부터 정렬
  }
  
  // 분봉 데이터 조회
  async getMinutePrices(stockCode: string, minutes = 60) {
    const { data, error } = await supabase
      .from('minute_prices')
      .select('*')
      .eq('stock_code', stockCode)
      .order('timestamp', { ascending: false })
      .limit(minutes)
    
    if (error) {
      console.error('Error fetching minute prices:', error)
      return []
    }
    
    return data.reverse()
  }
  
  // 연결 상태 확인
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
  
  // 서비스 종료
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    // Supabase 구독 해제
    supabase.removeAllChannels()
  }
}

export default new KiwoomService()