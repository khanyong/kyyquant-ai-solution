import React, { createContext, useContext, useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { User } from '@supabase/supabase-js'

export type UserRole = 'user' | 'trial' | 'standard' | 'premium' | 'admin'

interface AuthContextType {
  user: User | null
  role: UserRole | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  hasRole: (requiredRole: UserRole | UserRole[]) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [role, setRole] = useState<UserRole | null>(null)
  const [loading, setLoading] = useState(true)
  const [roleCache, setRoleCache] = useState<Record<string, { role: UserRole; timestamp: number }>>({})

  const fetchUserRole = async (userId: string, useCache = true): Promise<UserRole> => {
    try {
      // 캐시 확인 (5분 유효)
      if (useCache && roleCache[userId]) {
        const cached = roleCache[userId]
        const age = Date.now() - cached.timestamp
        if (age < 5 * 60 * 1000) { // 5분
          console.log('✅ AuthContext: Using cached role:', cached.role)
          return cached.role
        }
      }

      console.log('🔍 AuthContext: Fetching role from database...')

      // 10초 타임아웃 (5초에서 증가)
      const rolePromise = supabase
        .from('profiles')
        .select('role')
        .eq('id', userId)
        .single()

      const timeoutPromise = new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('Role fetch timeout')), 10000)
      )

      const { data, error } = await Promise.race([
        rolePromise,
        timeoutPromise
      ]) as any

      if (error) {
        console.error('⚠️ AuthContext: Error fetching user role:', error)
        // 에러 시 캐시된 값 사용 (있으면)
        if (roleCache[userId]) {
          console.log('🔄 AuthContext: Using stale cache due to error')
          return roleCache[userId].role
        }
        return 'user'
      }

      const fetchedRole = (data?.role as UserRole) || 'user'
      console.log('✅ AuthContext: Fetched role:', fetchedRole)

      // 캐시 업데이트
      setRoleCache(prev => ({
        ...prev,
        [userId]: { role: fetchedRole, timestamp: Date.now() }
      }))

      return fetchedRole
    } catch (error) {
      console.error('⚠️ AuthContext: Role fetch failed:', error)
      // 타임아웃 시 캐시된 값 사용
      if (roleCache[userId]) {
        console.log('🔄 AuthContext: Using stale cache due to timeout')
        return roleCache[userId].role
      }
      return 'user'
    }
  }

  const hasRole = (requiredRole: UserRole | UserRole[]): boolean => {
    if (!role) return false

    // admin은 모든 권한 보유
    if (role === 'admin') return true

    // 배열인 경우 하나라도 일치하면 true
    if (Array.isArray(requiredRole)) {
      return requiredRole.includes(role)
    }

    // 역할 계층 구조: admin > premium > standard > trial > user
    const roleHierarchy: Record<UserRole, number> = {
      'user': 1,
      'trial': 2,
      'standard': 3,
      'premium': 4,
      'admin': 5
    }

    const currentLevel = roleHierarchy[role] || 0
    const requiredLevel = roleHierarchy[requiredRole as UserRole] || 0

    // 현재 역할이 요구되는 역할보다 높거나 같으면 접근 가능
    return currentLevel >= requiredLevel
  }

  useEffect(() => {
    let mounted = true
    let isInitializing = false

    // 현재 세션 확인
    const initializeAuth = async () => {
      if (isInitializing) {
        console.log('⚠️ AuthContext: Already initializing, skipping...')
        return
      }

      isInitializing = true

      try {
        console.log('🔐 AuthContext: Initializing auth...')

        const { data: { session }, error } = await supabase.auth.getSession()

        if (error) {
          console.error('❌ AuthContext: Session error:', error)
          // 세션 오류 시 localStorage 정리
          if (error.message?.includes('session') || error.message?.includes('token') || error.message?.includes('expired')) {
            console.log('🧹 AuthContext: Clearing expired session...')
            localStorage.removeItem('kyyquant-auth-token')
            localStorage.removeItem('supabase.auth.token')
            // 세션 정리 후 재시도
            await supabase.auth.signOut({ scope: 'local' })
          }
        }

        if (mounted) {
          setUser(session?.user ?? null)
          if (session?.user) {
            console.log('✅ AuthContext: Session found for', session.user.email)
            const userRole = await fetchUserRole(session.user.id)
            setRole(userRole)
          } else {
            console.log('ℹ️ AuthContext: No session found')
            setRole(null)
          }
          setLoading(false)
        }
      } catch (error: any) {
        console.error('❌ AuthContext: Auth initialization error:', error)
        // 초기화 실패 시 세션 클리어
        try {
          console.log('🧹 AuthContext: Clearing corrupted auth data...')
          localStorage.removeItem('kyyquant-auth-token')
          localStorage.removeItem('supabase.auth.token')
          await supabase.auth.signOut({ scope: 'local' })
        } catch (clearError) {
          console.error('❌ AuthContext: Failed to clear auth data:', clearError)
        }

        if (mounted) {
          setUser(null)
          setRole(null)
          setLoading(false)
        }
      } finally {
        isInitializing = false
      }
    }

    initializeAuth()

    // 인증 상태 변경 구독
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('🔄 AuthContext: Auth state changed:', event, session?.user?.email)

      // INITIAL_SESSION은 무시 (initializeAuth에서 처리)
      if (event === 'INITIAL_SESSION') {
        console.log('ℹ️ AuthContext: Skipping INITIAL_SESSION event')
        return
      }

      if (mounted) {
        setUser(session?.user ?? null)
        if (session?.user) {
          const userRole = await fetchUserRole(session.user.id)
          setRole(userRole)
        } else {
          setRole(null)
        }
      }
    })

    return () => {
      mounted = false
      subscription.unsubscribe()
    }
  }, [])

  const signIn = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
  }

  const signUp = async (email: string, password: string) => {
    const { error } = await supabase.auth.signUp({ email, password })
    if (error) throw error
  }

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  }

  return (
    <AuthContext.Provider value={{ user, role, loading, signIn, signUp, signOut, hasRole }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
