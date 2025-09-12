import { supabase } from '../lib/supabase'

/**
 * Supabase Vault를 사용한 보안 강화 키움 인증 서비스
 * 
 * 특징:
 * - 모든 토큰은 Vault를 통해 암호화 저장
 * - 사용자별 고유 암호화 키 사용
 * - 토큰 접근 로그 자동 기록
 * - 만료된 토큰 자동 정리
 */

export interface SecureTokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  scope: string
}

export interface SecureAccount {
  id: string
  account_type: 'mock' | 'real'
  account_number: string
  account_name: string
  broker: string
  is_connected: boolean
  is_active: boolean
  token_status: 'valid' | 'expired' | 'unknown'
  current_balance?: number
  available_balance?: number
}

export class KiwoomAuthSecureService {
  private readonly BASE_URL = 'https://openapi.kiwoom.com'
  private readonly MOCK_URL = 'https://openapivts.kiwoom.com'
  
  // 환경변수는 서버사이드에서만 사용
  // 클라이언트는 Edge Function을 통해 간접 접근
  private readonly REDIRECT_URI = import.meta.env.VITE_KIWOOM_REDIRECT_URI || 'http://localhost:3000/auth/callback'
  
  /**
   * OAuth 인증 URL 생성 (클라이언트 사이드)
   */
  getAuthorizationUrl(accountType: 'mock' | 'real'): string {
    const baseUrl = accountType === 'mock' 
      ? `${this.MOCK_URL}/oauth2/authorize`
      : `${this.BASE_URL}/oauth2/authorize`
    
    // Client ID는 Edge Function에서 처리
    const params = new URLSearchParams({
      response_type: 'code',
      redirect_uri: this.REDIRECT_URI,
      scope: 'account trading',
      state: accountType
    })
    
    return `${baseUrl}?${params}`
  }
  
  /**
   * Authorization Code를 Access Token으로 교환 (Edge Function 호출)
   */
  async exchangeCodeForToken(
    code: string, 
    accountType: 'mock' | 'real',
    userId: string
  ): Promise<{ success: boolean; accountId?: string; error?: string }> {
    try {
      // Supabase Edge Function 호출
      const { data, error } = await supabase.functions.invoke('kiwoom-auth-exchange', {
        body: {
          code,
          accountType,
          userId,
          redirectUri: this.REDIRECT_URI
        }
      })
      
      if (error) throw error
      
      return data
    } catch (error) {
      console.error('Token exchange failed:', error)
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Token exchange failed' 
      }
    }
  }
  
  /**
   * 암호화된 계좌 정보 저장 (데이터베이스 함수 호출)
   */
  async saveSecureAccount(
    userId: string,
    accountType: 'mock' | 'real',
    accountNumber: string,
    accountName: string,
    accessToken: string,
    refreshToken: string,
    expiresIn: number
  ): Promise<{ success: boolean; accountId?: string; error?: string }> {
    try {
      const tokenExpiresAt = new Date(Date.now() + expiresIn * 1000).toISOString()
      
      // 데이터베이스 함수 호출 (자동 암호화)
      const { data, error } = await supabase.rpc('save_trading_account', {
        p_user_id: userId,
        p_account_type: accountType,
        p_account_number: accountNumber,
        p_account_name: accountName,
        p_access_token: accessToken,
        p_refresh_token: refreshToken,
        p_token_expires_at: tokenExpiresAt
      })
      
      if (error) throw error
      
      // 접근 로그 기록
      await this.logTokenAccess(userId, data, 'encrypt', true)
      
      return { success: true, accountId: data }
    } catch (error) {
      console.error('Failed to save secure account:', error)
      
      // 실패 로그 기록
      await this.logTokenAccess(userId, null, 'encrypt', false, error)
      
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Failed to save account' 
      }
    }
  }
  
  /**
   * 암호화된 토큰 조회 (복호화 포함)
   */
  async getSecureTokens(
    accountId: string,
    userId: string
  ): Promise<{ accessToken?: string; refreshToken?: string; error?: string }> {
    try {
      // 데이터베이스 함수 호출 (자동 복호화)
      const { data, error } = await supabase.rpc('get_trading_account_with_tokens', {
        p_account_id: accountId,
        p_user_id: userId
      })
      
      if (error) throw error
      if (!data || data.length === 0) throw new Error('Account not found')
      
      const account = data[0]
      
      // 접근 로그 기록
      await this.logTokenAccess(userId, accountId, 'decrypt', true)
      
      return {
        accessToken: account.access_token,
        refreshToken: account.refresh_token
      }
    } catch (error) {
      console.error('Failed to get secure tokens:', error)
      
      // 실패 로그 기록
      await this.logTokenAccess(userId, accountId, 'decrypt', false, error)
      
      return { 
        error: error instanceof Error ? error.message : 'Failed to get tokens' 
      }
    }
  }
  
  /**
   * 보안 계좌 목록 조회 (민감한 정보 제외)
   */
  async getSecureAccounts(userId: string): Promise<SecureAccount[]> {
    try {
      const { data, error } = await supabase
        .from('user_trading_accounts_view')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
      
      if (error) throw error
      
      return (data || []).map(account => ({
        id: account.id,
        account_type: account.account_type,
        account_number: account.account_number,
        account_name: account.account_name,
        broker: account.broker,
        is_connected: account.is_connected,
        is_active: account.is_active,
        token_status: account.token_status,
        current_balance: account.current_balance,
        available_balance: account.available_balance
      }))
    } catch (error) {
      console.error('Failed to get secure accounts:', error)
      return []
    }
  }
  
  /**
   * 토큰 갱신 (자동 재암호화)
   */
  async refreshSecureToken(
    accountId: string,
    userId: string
  ): Promise<{ success: boolean; error?: string }> {
    try {
      // 1. 현재 토큰 조회
      const tokens = await this.getSecureTokens(accountId, userId)
      if (tokens.error || !tokens.refreshToken) {
        throw new Error('Failed to get current tokens')
      }
      
      // 2. Edge Function을 통해 토큰 갱신
      const { data, error } = await supabase.functions.invoke('kiwoom-token-refresh', {
        body: {
          accountId,
          userId,
          refreshToken: tokens.refreshToken
        }
      })
      
      if (error) throw error
      
      // 3. 갱신된 토큰 저장 (자동 암호화)
      const { error: updateError } = await supabase.rpc('refresh_account_token', {
        p_account_id: accountId,
        p_user_id: userId,
        p_new_access_token: data.access_token,
        p_new_refresh_token: data.refresh_token,
        p_new_expires_at: new Date(Date.now() + data.expires_in * 1000).toISOString()
      })
      
      if (updateError) throw updateError
      
      // 접근 로그 기록
      await this.logTokenAccess(userId, accountId, 'refresh', true)
      
      return { success: true }
    } catch (error) {
      console.error('Failed to refresh secure token:', error)
      
      // 실패 로그 기록
      await this.logTokenAccess(userId, accountId, 'refresh', false, error)
      
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Failed to refresh token' 
      }
    }
  }
  
  /**
   * 계좌 연결 해제 (토큰 안전 삭제)
   */
  async revokeSecureAccount(
    accountId: string,
    userId: string
  ): Promise<{ success: boolean; error?: string }> {
    try {
      // 토큰 무효화
      const { error } = await supabase
        .from('user_trading_accounts_secure')
        .update({
          encrypted_access_token: null,
          encrypted_refresh_token: null,
          is_connected: false,
          is_active: false,
          token_expires_at: null
        })
        .eq('id', accountId)
        .eq('user_id', userId)
      
      if (error) throw error
      
      // 접근 로그 기록
      await this.logTokenAccess(userId, accountId, 'revoke', true)
      
      return { success: true }
    } catch (error) {
      console.error('Failed to revoke secure account:', error)
      
      // 실패 로그 기록
      await this.logTokenAccess(userId, accountId, 'revoke', false, error)
      
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Failed to revoke account' 
      }
    }
  }
  
  /**
   * 토큰 접근 로그 기록
   */
  private async logTokenAccess(
    userId: string,
    accountId: string | null,
    action: 'encrypt' | 'decrypt' | 'refresh' | 'revoke',
    success: boolean,
    error?: any
  ): Promise<void> {
    try {
      await supabase
        .from('token_access_logs')
        .insert({
          user_id: userId,
          account_id: accountId,
          action,
          success,
          error_message: error ? (error instanceof Error ? error.message : String(error)) : null,
          ip_address: await this.getClientIP(),
          user_agent: navigator.userAgent
        })
    } catch (logError) {
      console.error('Failed to log token access:', logError)
    }
  }
  
  /**
   * 클라이언트 IP 조회
   */
  private async getClientIP(): Promise<string> {
    try {
      const response = await fetch('https://api.ipify.org?format=json')
      const data = await response.json()
      return data.ip
    } catch {
      return 'unknown'
    }
  }
  
  /**
   * 토큰 상태 확인
   */
  async checkTokenStatus(
    accountId: string,
    userId: string
  ): Promise<'valid' | 'expired' | 'needs_refresh' | 'invalid'> {
    try {
      const { data, error } = await supabase
        .from('user_trading_accounts_view')
        .select('token_status, token_expires_at')
        .eq('id', accountId)
        .eq('user_id', userId)
        .single()
      
      if (error || !data) return 'invalid'
      
      const expiresAt = new Date(data.token_expires_at)
      const now = new Date()
      const fiveMinutesFromNow = new Date(now.getTime() + 5 * 60 * 1000)
      
      if (expiresAt <= now) return 'expired'
      if (expiresAt <= fiveMinutesFromNow) return 'needs_refresh'
      
      return 'valid'
    } catch {
      return 'invalid'
    }
  }
  
  /**
   * 자동 토큰 관리 (만료 체크 및 갱신)
   */
  async ensureValidToken(
    accountId: string,
    userId: string
  ): Promise<{ accessToken?: string; error?: string }> {
    try {
      const status = await this.checkTokenStatus(accountId, userId)
      
      if (status === 'invalid') {
        return { error: 'Invalid account' }
      }
      
      if (status === 'expired' || status === 'needs_refresh') {
        const refreshResult = await this.refreshSecureToken(accountId, userId)
        if (!refreshResult.success) {
          return { error: refreshResult.error }
        }
      }
      
      const tokens = await this.getSecureTokens(accountId, userId)
      return { accessToken: tokens.accessToken }
    } catch (error) {
      return { 
        error: error instanceof Error ? error.message : 'Failed to ensure valid token' 
      }
    }
  }
}

// 싱글톤 인스턴스
export const kiwoomAuthSecure = new KiwoomAuthSecureService()