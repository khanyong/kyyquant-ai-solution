import { supabase } from '../lib/supabase'
import type { User } from '@supabase/supabase-js'

export interface AuthResponse {
  user: User | null
  error: Error | null
}

export const authService = {
  // 이메일로 회원가입
  async signUpWithEmail(email: string, password: string, name?: string, kiwoomId?: string) {
    console.log('🔄 Starting signup process for:', email)
    console.log('📝 Signup data:', { email, name, kiwoomId })
    
    try {
      console.log('📡 Calling Supabase auth.signUp...')
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

      console.log('📥 Supabase signup response:', { data, error })

      if (error) {
        console.error('❌ Supabase signup error:', error)
        throw error
      }

      // 프로필 생성 보장 (트리거가 실행되지 않을 경우 대비)
      if (data.user) {
        console.log('🔍 Checking if profile exists for user:', data.user.id)
        
        // 잠시 대기 후 프로필 확인 (트리거 실행 시간 고려)
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        const { data: existingProfile, error: checkError } = await supabase
          .from('profiles')
          .select('id')
          .eq('id', data.user.id)
          .single()

        if (checkError && checkError.code === 'PGRST116') {
          // 프로필이 없으면 생성
          console.log('📝 Profile not found, creating manually for user:', data.user.id)
          const { data: profileData, error: profileError } = await supabase
            .from('profiles')
            .insert({
              id: data.user.id,
              email: data.user.email,
              name: name || email.split('@')[0],
              kiwoom_account: kiwoomId,
              email_verified: false,
              email_verified_at: null,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            })
            .select()

          if (profileError) {
            console.error('❌ Manual profile creation error:', profileError)
            console.log('📋 Profile error details:', {
              code: profileError.code,
              message: profileError.message,
              details: profileError.details,
              hint: profileError.hint
            })
          } else {
            console.log('✅ Profile created manually:', profileData)
          }
        } else if (existingProfile) {
          console.log('✅ Profile already exists (created by trigger):', existingProfile)
        } else {
          console.error('❌ Unexpected error checking profile:', checkError)
        }
      }

      console.log('✅ Signup completed successfully for user:', data.user?.id)
      return { user: data.user, error: null }
    } catch (error) {
      console.error('💥 Signup process failed with exception:', error)
      console.error('📋 Error details:', {
        name: (error as Error).name,
        message: (error as Error).message,
        stack: (error as Error).stack
      })
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