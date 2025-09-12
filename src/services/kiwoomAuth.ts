import { supabase } from '../lib/supabase'

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  scope: string
}

export interface KiwoomAccount {
  account_number: string
  account_name: string
  account_type: 'mock' | 'real'
  broker: string
}

export class KiwoomAuthService {
  private readonly BASE_URL = 'https://openapi.kiwoom.com'
  private readonly MOCK_URL = 'https://openapivts.kiwoom.com' // 모의투자 URL
  
  // 환경변수에서 읽어올 값들 (실제로는 .env에서 관리)
  private readonly CLIENT_ID = import.meta.env.VITE_KIWOOM_CLIENT_ID || ''
  private readonly CLIENT_SECRET = import.meta.env.VITE_KIWOOM_CLIENT_SECRET || ''
  private readonly REDIRECT_URI = import.meta.env.VITE_KIWOOM_REDIRECT_URI || 'http://localhost:3000/auth/callback'
  
  /**
   * OAuth 인증 URL 생성
   */
  getAuthorizationUrl(accountType: 'mock' | 'real'): string {
    const baseUrl = accountType === 'mock' 
      ? `${this.MOCK_URL}/oauth2/authorize`
      : `${this.BASE_URL}/oauth2/authorize`
    
    const params = new URLSearchParams({
      response_type: 'code',
      client_id: this.CLIENT_ID,
      redirect_uri: this.REDIRECT_URI,
      scope: 'account trading',
      state: accountType // accountType을 state로 전달
    })
    
    return `${baseUrl}?${params}`
  }
  
  /**
   * Authorization Code를 Access Token으로 교환
   */
  async getAccessToken(code: string, accountType: 'mock' | 'real'): Promise<TokenResponse> {
    const tokenUrl = accountType === 'mock'
      ? `${this.MOCK_URL}/oauth2/token`
      : `${this.BASE_URL}/oauth2/token`
    
    const response = await fetch(tokenUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: this.CLIENT_ID,
        client_secret: this.CLIENT_SECRET,
        code,
        redirect_uri: this.REDIRECT_URI
      })
    })
    
    if (!response.ok) {
      const error = await response.text()
      throw new Error(`Token exchange failed: ${error}`)
    }
    
    return response.json()
  }
  
  /**
   * Refresh Token으로 Access Token 갱신
   */
  async refreshToken(refreshToken: string, accountType: 'mock' | 'real'): Promise<TokenResponse> {
    const tokenUrl = accountType === 'mock'
      ? `${this.MOCK_URL}/oauth2/token`
      : `${this.BASE_URL}/oauth2/token`
    
    const response = await fetch(tokenUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        client_id: this.CLIENT_ID,
        client_secret: this.CLIENT_SECRET,
        refresh_token: refreshToken
      })
    })
    
    if (!response.ok) {
      const error = await response.text()
      throw new Error(`Token refresh failed: ${error}`)
    }
    
    return response.json()
  }
  
  /**
   * 계좌 정보 조회
   */
  async getAccounts(accessToken: string, accountType: 'mock' | 'real'): Promise<KiwoomAccount[]> {
    const apiUrl = accountType === 'mock'
      ? `${this.MOCK_URL}/v1/accounts`
      : `${this.BASE_URL}/v1/accounts`
    
    const response = await fetch(apiUrl, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      const error = await response.text()
      throw new Error(`Failed to fetch accounts: ${error}`)
    }
    
    const data = await response.json()
    
    // 계좌 정보 형식 변환
    return data.accounts.map((acc: any) => ({
      account_number: acc.account_no,
      account_name: acc.account_name,
      account_type: accountType,
      broker: 'kiwoom'
    }))
  }
  
  /**
   * 계좌 정보를 Supabase에 저장
   */
  async saveAccountToSupabase(
    userId: string,
    account: KiwoomAccount,
    tokenData: TokenResponse
  ): Promise<void> {
    const { error } = await supabase
      .from('user_trading_accounts')
      .upsert({
        user_id: userId,
        account_type: account.account_type,
        account_number: account.account_number,
        account_name: account.account_name,
        broker: account.broker,
        access_token: tokenData.access_token,
        refresh_token: tokenData.refresh_token,
        token_expires_at: new Date(Date.now() + tokenData.expires_in * 1000).toISOString(),
        is_connected: true,
        is_active: true,
        last_sync_at: new Date().toISOString()
      }, {
        onConflict: 'user_id,account_number,broker'
      })
    
    if (error) {
      console.error('Failed to save account:', error)
      throw error
    }
  }
  
  /**
   * 저장된 계좌 목록 조회
   */
  async getSavedAccounts(userId: string): Promise<any[]> {
    const { data, error } = await supabase
      .from('user_trading_accounts')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
    
    if (error) {
      console.error('Failed to fetch saved accounts:', error)
      throw error
    }
    
    return data || []
  }
  
  /**
   * 토큰 만료 체크 및 자동 갱신
   */
  async checkAndRefreshToken(accountId: string): Promise<string> {
    const { data: account, error } = await supabase
      .from('user_trading_accounts')
      .select('*')
      .eq('id', accountId)
      .single()
    
    if (error || !account) {
      throw new Error('Account not found')
    }
    
    const tokenExpiresAt = new Date(account.token_expires_at)
    const now = new Date()
    
    // 토큰이 만료되었거나 5분 이내에 만료될 예정이면 갱신
    if (tokenExpiresAt <= new Date(now.getTime() + 5 * 60 * 1000)) {
      try {
        const newTokenData = await this.refreshToken(
          account.refresh_token,
          account.account_type
        )
        
        // 새 토큰 정보 업데이트
        await supabase
          .from('user_trading_accounts')
          .update({
            access_token: newTokenData.access_token,
            refresh_token: newTokenData.refresh_token,
            token_expires_at: new Date(Date.now() + newTokenData.expires_in * 1000).toISOString(),
            last_sync_at: new Date().toISOString()
          })
          .eq('id', accountId)
        
        return newTokenData.access_token
      } catch (error) {
        console.error('Failed to refresh token:', error)
        
        // 토큰 갱신 실패 시 연결 상태 업데이트
        await supabase
          .from('user_trading_accounts')
          .update({
            is_connected: false,
            is_active: false
          })
          .eq('id', accountId)
        
        throw error
      }
    }
    
    return account.access_token
  }
  
  /**
   * 계좌 연결 해제
   */
  async disconnectAccount(accountId: string): Promise<void> {
    const { error } = await supabase
      .from('user_trading_accounts')
      .update({
        access_token: null,
        refresh_token: null,
        token_expires_at: null,
        is_connected: false,
        is_active: false
      })
      .eq('id', accountId)
    
    if (error) {
      console.error('Failed to disconnect account:', error)
      throw error
    }
  }
}

// 싱글톤 인스턴스
export const kiwoomAuth = new KiwoomAuthService()