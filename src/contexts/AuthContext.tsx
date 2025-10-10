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

  const fetchUserRole = async (userId: string): Promise<UserRole> => {
    const { data, error } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', userId)
      .single()

    if (error) {
      console.error('Error fetching user role:', error)
      return 'user'
    }

    return (data?.role as UserRole) || 'user'
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

    // 현재 세션 확인
    const initializeAuth = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession()

        if (error) {
          console.error('Session error:', error)
        }

        if (mounted) {
          setUser(session?.user ?? null)
          if (session?.user) {
            const userRole = await fetchUserRole(session.user.id)
            setRole(userRole)
          } else {
            setRole(null)
          }
          setLoading(false)
        }
      } catch (error) {
        console.error('Auth initialization error:', error)
        if (mounted) {
          setUser(null)
          setRole(null)
          setLoading(false)
        }
      }
    }

    initializeAuth()

    // 인증 상태 변경 구독
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('Auth state changed:', event, session?.user?.email)

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
