import { supabase } from '../lib/supabase'
import type { User } from '@supabase/supabase-js'

export interface AuthResponse {
  user: User | null
  error: Error | null
}

export const authService = {
  // 이메일로 회원가입
  async signUpWithEmail(email: string, password: string, name?: string, kiwoomId?: string) {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            name: name || email.split('@')[0],
            kiwoom_id: kiwoomId
          },
          emailRedirectTo: 'https://kyyquant-ai-solution.vercel.app/auth/callback'
        }
      })

      if (error) throw error

      // 프로필 생성 (트리거가 없는 경우 백업용)
      if (data.user) {
        console.log('Creating profile for user:', data.user.id)
        const { data: profileData, error: profileError } = await supabase
          .from('profiles')
          .insert({
            id: data.user.id,
            email: data.user.email,
            name: name || email.split('@')[0],
            kiwoom_account: kiwoomId,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          })
          .select()

        if (profileError) {
          console.error('Profile creation error:', profileError)
          console.log('Profile error details:', {
            code: profileError.code,
            message: profileError.message,
            details: profileError.details,
            hint: profileError.hint
          })
        } else {
          console.log('Profile created successfully:', profileData)
        }
      }

      return { user: data.user, error: null }
    } catch (error) {
      return { user: null, error: error as Error }
    }
  },

  // 이메일로 로그인
  async signInWithEmail(email: string, password: string) {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) throw error

      // 사용자 승인 상태 확인 (옵션 - 프로필이 없으면 스킵)
      if (data.user) {
        const { data: profile, error: profileError } = await supabase
          .from('profiles')
          .select('is_approved, approval_status, email_verified')
          .eq('id', data.user.id)
          .single()

        if (profileError) {
          console.warn('Profile not found or fetch error:', profileError)
          // 프로필이 없어도 로그인은 허용 (데모 모드나 초기 설정용)
        } else if (profile) {
          // 이메일 미인증 (프로필이 있는 경우만 체크)
          if (profile.email_verified === false && !data.user.email_confirmed_at) {
            throw new Error('이메일 인증이 필요합니다. 이메일을 확인해주세요.')
          }

          // 관리자 승인 대기 (프로필이 있는 경우만 체크)
          if (profile.approval_status === 'pending') {
            console.warn('User is pending approval')
            // 일단 로그인은 허용하되, 기능 제한은 프론트엔드에서 처리
          }

          // 승인 거부됨
          if (profile.approval_status === 'rejected') {
            throw new Error('가입이 거부되었습니다. 관리자에게 문의하세요.')
          }
        }
      }

      return { user: data.user, error: null }
    } catch (error) {
      return { user: null, error: error as Error }
    }
  },

  // Google OAuth 로그인
  async signInWithGoogle() {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: 'https://kyyquant-ai-solution.vercel.app/auth/callback'
        }
      })

      if (error) throw error
      return { data, error: null }
    } catch (error) {
      return { data: null, error: error as Error }
    }
  },

  // GitHub OAuth 로그인
  async signInWithGitHub() {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'github',
        options: {
          redirectTo: 'https://kyyquant-ai-solution.vercel.app/auth/callback'
        }
      })

      if (error) throw error
      return { data, error: null }
    } catch (error) {
      return { data: null, error: error as Error }
    }
  },

  // 로그아웃
  async signOut() {
    try {
      const { error } = await supabase.auth.signOut()
      if (error) throw error
      return { error: null }
    } catch (error) {
      return { error: error as Error }
    }
  },

  // 현재 사용자 가져오기
  async getCurrentUser() {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      return user
    } catch (error) {
      console.error('Get current user error:', error)
      return null
    }
  },

  // 세션 가져오기
  async getSession() {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      return session
    } catch (error) {
      console.error('Get session error:', error)
      return null
    }
  },

  // 비밀번호 재설정 이메일 보내기
  async resetPassword(email: string) {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`
      })

      if (error) throw error
      return { error: null }
    } catch (error) {
      return { error: error as Error }
    }
  },

  // 비밀번호 업데이트
  async updatePassword(newPassword: string) {
    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword
      })

      if (error) throw error
      return { error: null }
    } catch (error) {
      return { error: error as Error }
    }
  },

  // 프로필 정보 가져오기
  async getProfile(userId: string) {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (error) throw error
      return { profile: data, error: null }
    } catch (error) {
      return { profile: null, error: error as Error }
    }
  },

  // 프로필 업데이트
  async updateProfile(userId: string, updates: { name?: string; kiwoom_account?: string }) {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .update(updates)
        .eq('id', userId)
        .select()
        .single()

      if (error) throw error
      return { profile: data, error: null }
    } catch (error) {
      return { profile: null, error: error as Error }
    }
  },

  // Auth 상태 변경 리스너
  onAuthStateChange(callback: (user: User | null) => void) {
    return supabase.auth.onAuthStateChange((event, session) => {
      callback(session?.user ?? null)
    })
  }
}