import { supabase } from '../lib/supabase'

export interface KiwoomApiKeys {
  appKey: string | null
  appSecret: string | null
  accountNumber: string | null
  certPassword: string | null
}

export interface KiwoomApiConfig {
  baseUrl: string
  appKey: string
  appSecret: string
  accountNumber?: string
  isTestMode: boolean
}

export class KiwoomApiService {
  private static instance: KiwoomApiService | null = null
  private config: KiwoomApiConfig | null = null
  private isTestMode: boolean = true

  private constructor() {}

  static getInstance(): KiwoomApiService {
    if (!this.instance) {
      this.instance = new KiwoomApiService()
    }
    return this.instance
  }

  /**
   * 현재 사용자의 API 키 가져오기
   */
  async loadUserApiKeys(userId: string, testMode: boolean = true): Promise<KiwoomApiKeys> {
    try {
      console.log(`Loading Kiwoom API keys for user ${userId} (${testMode ? 'test' : 'live'} mode)`)

      const { data, error } = await supabase
        .from('user_api_keys')
        .select('*')
        .eq('user_id', userId)
        .eq('provider', 'kiwoom')
        .eq('is_test_mode', testMode)
        .eq('is_active', true)

      if (error) {
        throw new Error(`Failed to load API keys: ${error.message}`)
      }

      if (!data || data.length === 0) {
        throw new Error(`No ${testMode ? 'test' : 'live'} mode API keys found for Kiwoom`)
      }

      // API 키 정리
      const keys: KiwoomApiKeys = {
        appKey: null,
        appSecret: null,
        accountNumber: null,
        certPassword: null
      }

      data.forEach(key => {
        // Base64 디코딩
        const decodedValue = atob(key.encrypted_value)
        
        switch (key.key_type) {
          case 'app_key':
            keys.appKey = decodedValue
            break
          case 'app_secret':
            keys.appSecret = decodedValue
            break
          case 'account_number':
            keys.accountNumber = decodedValue
            break
          case 'cert_password':
            keys.certPassword = decodedValue
            break
        }
      })

      if (!keys.appKey || !keys.appSecret) {
        throw new Error('App Key and App Secret are required')
      }

      console.log('API keys loaded successfully')
      return keys
    } catch (error) {
      console.error('Error loading API keys:', error)
      throw error
    }
  }

  /**
   * API 설정 초기화
   */
  async initialize(userId: string, testMode: boolean = true): Promise<void> {
    try {
      const keys = await this.loadUserApiKeys(userId, testMode)
      
      this.config = {
        baseUrl: testMode 
          ? 'https://openapivts.koreainvestment.com:29443' // 모의투자
          : 'https://openapi.koreainvestment.com:9443',     // 실전투자
        appKey: keys.appKey!,
        appSecret: keys.appSecret!,
        accountNumber: keys.accountNumber || undefined,
        isTestMode: testMode
      }
      
      this.isTestMode = testMode
      
      console.log(`KiwoomApiService initialized in ${testMode ? 'TEST' : 'LIVE'} mode`)
    } catch (error) {
      console.error('Failed to initialize KiwoomApiService:', error)
      throw error
    }
  }

  /**
   * 현재 설정 가져오기
   */
  getConfig(): KiwoomApiConfig | null {
    return this.config
  }

  /**
   * 접근 토큰 발급
   */
  async getAccessToken(): Promise<string> {
    if (!this.config) {
      throw new Error('KiwoomApiService not initialized')
    }

    try {
      const response = await fetch(`${this.config.baseUrl}/oauth2/tokenP`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          grant_type: 'client_credentials',
          appkey: this.config.appKey,
          appsecret: this.config.appSecret
        })
      })

      const data = await response.json()
      
      if (data.access_token) {
        console.log('Access token obtained successfully')
        return data.access_token
      } else {
        throw new Error('Failed to obtain access token')
      }
    } catch (error) {
      console.error('Error getting access token:', error)
      throw error
    }
  }

  /**
   * 주식 현재가 조회
   */
  async getCurrentPrice(stockCode: string): Promise<any> {
    if (!this.config) {
      throw new Error('KiwoomApiService not initialized')
    }

    try {
      const token = await this.getAccessToken()
      
      const response = await fetch(`${this.config.baseUrl}/uapi/domestic-stock/v1/quotations/inquire-price`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'authorization': `Bearer ${token}`,
          'appkey': this.config.appKey,
          'appsecret': this.config.appSecret,
          'tr_id': this.isTestMode ? 'VTTC0802U' : 'FHKST01010100'
        },
        body: JSON.stringify({
          fid_cond_mrkt_div_code: 'J',
          fid_input_iscd: stockCode
        })
      })

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error getting current price:', error)
      throw error
    }
  }

  /**
   * 주식 매수 주문
   */
  async buyStock(stockCode: string, quantity: number, price: number): Promise<any> {
    if (!this.config) {
      throw new Error('KiwoomApiService not initialized')
    }

    if (!this.config.accountNumber) {
      throw new Error('Account number not configured')
    }

    try {
      const token = await this.getAccessToken()
      
      const response = await fetch(`${this.config.baseUrl}/uapi/domestic-stock/v1/trading/order-cash`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'authorization': `Bearer ${token}`,
          'appkey': this.config.appKey,
          'appsecret': this.config.appSecret,
          'tr_id': this.isTestMode ? 'VTTC0802U' : 'TTTC0802U'
        },
        body: JSON.stringify({
          CANO: this.config.accountNumber.substring(0, 8),
          ACNT_PRDT_CD: this.config.accountNumber.substring(8, 10),
          PDNO: stockCode,
          ORD_DVSN: '00', // 지정가
          ORD_QTY: quantity.toString(),
          ORD_UNPR: price.toString()
        })
      })

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error placing buy order:', error)
      throw error
    }
  }

  /**
   * 주식 매도 주문
   */
  async sellStock(stockCode: string, quantity: number, price: number): Promise<any> {
    if (!this.config) {
      throw new Error('KiwoomApiService not initialized')
    }

    if (!this.config.accountNumber) {
      throw new Error('Account number not configured')
    }

    try {
      const token = await this.getAccessToken()
      
      const response = await fetch(`${this.config.baseUrl}/uapi/domestic-stock/v1/trading/order-cash`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'authorization': `Bearer ${token}`,
          'appkey': this.config.appKey,
          'appsecret': this.config.appSecret,
          'tr_id': this.isTestMode ? 'VTTC0801U' : 'TTTC0801U'
        },
        body: JSON.stringify({
          CANO: this.config.accountNumber.substring(0, 8),
          ACNT_PRDT_CD: this.config.accountNumber.substring(8, 10),
          PDNO: stockCode,
          ORD_DVSN: '00', // 지정가
          ORD_QTY: quantity.toString(),
          ORD_UNPR: price.toString()
        })
      })

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error placing sell order:', error)
      throw error
    }
  }

  /**
   * 계좌 잔고 조회
   */
  async getAccountBalance(): Promise<any> {
    if (!this.config) {
      throw new Error('KiwoomApiService not initialized')
    }

    if (!this.config.accountNumber) {
      throw new Error('Account number not configured')
    }

    try {
      const token = await this.getAccessToken()
      
      const response = await fetch(`${this.config.baseUrl}/uapi/domestic-stock/v1/trading/inquire-balance`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'authorization': `Bearer ${token}`,
          'appkey': this.config.appKey,
          'appsecret': this.config.appSecret,
          'tr_id': this.isTestMode ? 'VTTC8434R' : 'TTTC8434R'
        },
        body: JSON.stringify({
          CANO: this.config.accountNumber.substring(0, 8),
          ACNT_PRDT_CD: this.config.accountNumber.substring(8, 10),
          AFHR_FLPR_YN: 'N',
          OFL_YN: '',
          INQR_DVSN: '02',
          UNPR_DVSN: '01',
          FUND_STTL_ICLD_YN: 'N',
          FNCG_AMT_AUTO_RDPT_YN: 'N',
          PRCS_DVSN: '01',
          CTX_AREA_FK100: '',
          CTX_AREA_NK100: ''
        })
      })

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error getting account balance:', error)
      throw error
    }
  }

  /**
   * 모드 전환
   */
  async switchMode(userId: string, testMode: boolean): Promise<void> {
    await this.initialize(userId, testMode)
  }

  /**
   * 현재 모드 확인
   */
  isInTestMode(): boolean {
    return this.isTestMode
  }
}

// Export singleton instance
export const kiwoomApi = KiwoomApiService.getInstance()