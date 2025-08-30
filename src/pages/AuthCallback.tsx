import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, CircularProgress, Typography } from '@mui/material'
import { supabase } from '../lib/supabase'

const AuthCallback: React.FC = () => {
  const navigate = useNavigate()

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // URL의 해시 파라미터에서 인증 정보 처리
        const { data, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('Auth callback error:', error)
          navigate('/?error=auth_failed')
          return
        }

        if (data?.session?.user) {
          // 이메일 인증 완료 - 메인 페이지로 리다이렉트
          navigate('/?success=email_verified')
        } else {
          // 세션이 없으면 메인 페이지로
          navigate('/')
        }
      } catch (error) {
        console.error('Callback processing error:', error)
        navigate('/?error=callback_failed')
      }
    }

    handleAuthCallback()
  }, [navigate])

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        gap: 2
      }}
    >
      <CircularProgress size={60} />
      <Typography variant="h6">
        이메일 인증 처리 중...
      </Typography>
      <Typography variant="body2" color="text.secondary">
        잠시만 기다려주세요.
      </Typography>
    </Box>
  )
}

export default AuthCallback