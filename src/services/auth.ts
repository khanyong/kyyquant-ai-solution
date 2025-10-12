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
      console.log('🔑 authService: Attempting sign in...')

      // 15초 타임아웃으로 signInWithPassword 호출
      const signInPromise = supabase.auth.signInWithPassword({
        email,
        password
      })

      const timeoutPromise = new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('Sign in timeout - 서버 응답이 없습니다. 다시 시도해주세요.')), 15000)
      )

      const { data, error } = await Promise.race([
        signInPromise,
        timeoutPromise
      ])

      console.log('🔑 authService: Sign in response:', { user: !!data.user, error: !!error })

      if (error) {
        console.error('🔑 authService: Sign in error:', error)
        throw error
      }

      // 프로필 확인은 타임아웃 설정하여 blocking 방지
      if (data.user) {
        console.log('🔑 authService: User authenticated, checking profile...')

        // 5초 타임아웃으로 프로필 조회
        const profilePromise = supabase
          .from('profiles')
          .select('is_approved, approval_status, email_verified')
          .eq('id', data.user.id)
          .single()

        const timeoutPromise = new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Profile fetch timeout')), 5000)
        )

        try {
          const { data: profile, error: profileError } = await Promise.race([
            profilePromise,
            timeoutPromise
          ]) as any

          if (profileError) {
            console.warn('🔑 authService: Profile not found or fetch error:', profileError)
            // 프로필이 없어도 로그인은 허용
          } else if (profile) {
            console.log('🔑 authService: Profile loaded:', profile)

            // 이메일 미인증 체크
            if (profile.email_verified === false && !data.user.email_confirmed_at) {
              throw new Error('이메일 인증이 필요합니다. 이메일을 확인해주세요.')
            }

            // 승인 거부 체크
            if (profile.approval_status === 'rejected') {
              throw new Error('가입이 거부되었습니다. 관리자에게 문의하세요.')
            }

            // 승인 대기는 경고만 (로그인 허용)
            if (profile.approval_status === 'pending') {
              console.warn('🔑 authService: User is pending approval')
            }
          }
        } catch (profileError: any) {
          console.warn('🔑 authService: Profile check failed (non-blocking):', profileError.message)
          // 프로필 체크 실패해도 로그인은 계속
        }
      }

      console.log('🔑 authService: Sign in successful')
      return { user: data.user, error: null }
    } catch (error) {
      console.error('🔑 authService: Sign in failed:', error)
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

  // 프로필 정보 가져오기 (통합 프로필 정보 포함)
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

  // 전체 프로필 정보 가져오기 (확장 프로필, API 키, 거래 계좌 포함)
  async getFullProfile(userId: string) {
    try {
      const { data, error } = await supabase
        .rpc('get_user_full_profile', { p_user_id: userId })

      if (error) throw error
      return { fullProfile: data, error: null }
    } catch (error) {
      return { fullProfile: null, error: error as Error }
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

  // 확장 프로필 업데이트
  async updateExtendedProfile(userId: string, updates: any) {
    try {
      const { data, error } = await supabase
        .from('user_profiles_extended')
        .upsert({
          user_id: userId,
          ...updates,
          updated_at: new Date().toISOString()
        })
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