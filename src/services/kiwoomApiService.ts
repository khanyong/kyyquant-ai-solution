
import axios from 'axios'

// Backend API URL (Proxy to Kiwoom)
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export interface KiwoomApiConfig {
  baseUrl: string
  isTestMode: boolean
}

export class KiwoomApiService {
  private static instance: KiwoomApiService | null = null
  private config: KiwoomApiConfig = {
    baseUrl: BASE_URL,
    isTestMode: true
  }

  private constructor() { }

  static getInstance(): KiwoomApiService {
    if (!this.instance) {
      this.instance = new KiwoomApiService()
    }
    return this.instance
  }

  /**
   * Initialize Service (Just verify backend connection)
   */
  async initialize(userId: string, testMode: boolean = true): Promise<void> {
    this.config.isTestMode = testMode
    // Optionally check backend status: GET /api/account/status
    console.log(`[KiwoomService] Initialized (Targeting Backend: ${this.config.baseUrl})`)
  }

  getConfig(): KiwoomApiConfig | null {
    return this.config
  }

  /**
   * Get Current Price via Backend
   * GET /api/market/price/{stockCode}
   */
  async getCurrentPrice(stockCode: string): Promise<any> {
    try {
      const response = await axios.get(`${this.config.baseUrl}/api/market/price/${stockCode}`)
      return response.data
    } catch (error) {
      console.error('Error getting current price:', error)
      throw error
    }
  }

  /**
   * Place Buy Order via Backend
   * POST /api/order/buy
   */
  async buyStock(stockCode: string, quantity: number, price: number): Promise<any> {
    try {
      const response = await axios.post(`${this.config.baseUrl}/api/order/buy`, {
        stock_code: stockCode,
        quantity: quantity,
        price: price,
        order_type: 'buy'
      })
      return response.data
    } catch (error) {
      console.error('Error placing buy order:', error)
      throw error
    }
  }

  /**
   * Place Sell Order via Backend
   * POST /api/order/sell
   */
  async sellStock(stockCode: string, quantity: number, price: number): Promise<any> {
    try {
      const response = await axios.post(`${this.config.baseUrl}/api/order/sell`, {
        stock_code: stockCode,
        quantity: quantity,
        price: price,
        order_type: 'sell'
      })
      return response.data
    } catch (error) {
      console.error('Error placing sell order:', error)
      throw error
    }
  }

  /**
   * Get Account Balance via Backend
   * GET /api/account/balance
   */
  async getAccountBalance(): Promise<any> {
    try {
      const response = await axios.get(`${this.config.baseUrl}/api/account/balance`)
      return response.data
    } catch (error) {
      console.error('Error getting account balance:', error)
      throw error
    }
  }

  /**
   * Switch Mode (Mock / Real)
   * Note: Backend mode is determined by Backend env vars, 
   * but we can store local preference here if needed.
   */
  async switchMode(userId: string, testMode: boolean): Promise<void> {
    this.config.isTestMode = testMode
    // If backend supports dynamic switching, call endpoint here.
    // Currently backend mode is env-based (KIWOOM_IS_DEMO).
  }

  isInTestMode(): boolean {
    return this.config.isTestMode
  }
}

// Export singleton instance
export const kiwoomApi = KiwoomApiService.getInstance()