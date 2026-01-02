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
   * 계좌 정보를 Supabase에 저장 (user_api_keys 사용)
   */
  async saveAccountToSupabase(
    userId: string,
    account: KiwoomAccount,
    tokenData: TokenResponse
  ): Promise<void> {
    const isTest = account.account_type === 'mock'
    const keyName = isTest ? '모의투자' : '실전투자'

    // 1. Save Account Number
    await supabase.from('user_api_keys').upsert({
      user_id: userId,
      provider: 'kiwoom',
      key_type: 'account_number',
      key_name: keyName,
      encrypted_value: btoa(account.account_number), // Simple base64 for now, real app should encrypt
      is_test_mode: isTest,
      is_active: true
    }, { onConflict: 'user_id,provider,key_type,key_name' })

    // 2. Save Tokens (Optional: if we need to store them)
    // We store them as separate keys for now to match the consolidated schema pattern
    await supabase.from('user_api_keys').upsert({
      user_id: userId,
      provider: 'kiwoom',
      key_type: 'access_token',
      key_name: keyName,
      encrypted_value: btoa(tokenData.access_token),
      is_test_mode: isTest,
      is_active: true
    }, { onConflict: 'user_id,provider,key_type,key_name' })

    await supabase.from('user_api_keys').upsert({
      user_id: userId,
      provider: 'kiwoom',
      key_type: 'refresh_token',
      key_name: keyName,
      encrypted_value: btoa(tokenData.refresh_token),
      is_test_mode: isTest,
      is_active: true
    }, { onConflict: 'user_id,provider,key_type,key_name' })
  }

  /**
   * 저장된 계좌 목록 조회
   */
  async getSavedAccounts(userId: string): Promise<any[]> {
    // 1. Get Accounts from user_api_keys
    const { data, error } = await supabase
      .from('user_api_keys')
      .select('*')
      .eq('user_id', userId)
      .eq('key_type', 'account_number')
      .eq('is_active', true)

    if (error) {
      console.error('Failed to fetch saved accounts:', error)
      return []
    }

    if (!data) return []

    // Map to expected format
    return data.map(item => ({
      id: item.id,
      account_number: atob(item.encrypted_value), // decode base64
      account_name: item.key_name,
      account_type: item.is_test_mode ? 'mock' : 'real',
      is_connected: true, // simplified
      is_active: true
    }))
  }

  /**
   * 토큰 만료 체크 및 자동 갱신 (Simplified for consolidated schema)
   * Note: With consolidated schema, token management might need a dedicated table if complex expiry logic is needed.
   * For now, resolving simple fetch.
   */
  async checkAndRefreshToken(accountId: string): Promise<string> {
    // In consolidated schema, 'accountId' is the UUID row in user_api_keys
    // Implementation omitted for brevity as User is focused on visibility first.
    // Logic would be: find the corresponding 'refresh_token' row and update 'access_token' row.
    console.log("Token refresh requested for", accountId)
    return ""
  }

  /**
   * 계좌 연결 해제
   */
  async disconnectAccount(accountId: string): Promise<void> {
    const { error } = await supabase
      .from('user_api_keys')
      .update({ is_active: false })
      .eq('id', accountId)

    if (error) throw error
  }
}

// 싱글톤 인스턴스
export const kiwoomAuth = new KiwoomAuthService()