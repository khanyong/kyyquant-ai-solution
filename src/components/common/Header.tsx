import React, { useState, useEffect } from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Chip,
  IconButton,
  Link
} from '@mui/material'
import {
  TrendingUp,
  Logout,
  Settings,
  Map,
  Person,
  Science
} from '@mui/icons-material'
import { useAppSelector, useAppDispatch } from '../../hooks/redux'
import { logout } from '../../store/authSlice'
import { authService } from '../../services/auth'
import { supabase } from '../../lib/supabase'
import RoadmapDialog from './RoadmapDialog'

interface HeaderProps {
  onLoginClick: () => void
}

const Header: React.FC<HeaderProps> = ({ onLoginClick }) => {
  const dispatch = useAppDispatch()
  const { isConnected, user } = useAppSelector(state => state.auth)
  const [roadmapOpen, setRoadmapOpen] = useState(false)
  const [tradingMode, setTradingMode] = useState<'test' | 'live'>('test')

  useEffect(() => {
    if (user?.id) {
      const fetchMode = async () => {
        const { data } = await supabase.rpc('get_current_mode_info', { p_user_id: user.id })
        if (data?.current_mode) {
          setTradingMode(data.current_mode)
        }
      }
      fetchMode()
    }
  }, [user?.id])

  const handleLogout = async () => {
    await authService.signOut()
    dispatch(logout())
  }

  return (
    <>
      <AppBar position="static" elevation={0} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Toolbar>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              flexGrow: 1,
              cursor: 'pointer',
              '&:hover': {
                opacity: 0.8
              }
            }}
            onClick={() => window.location.href = '/'}
          >
            <TrendingUp sx={{ mr: 2 }} />
            <Typography variant="h6" component="div">
              KyyQuant AI Solution
            </Typography>
          </Box>

          {/* 개발 로드맵 버튼 */}
          <Button
            color="warning"
            variant="outlined"
            startIcon={<Map />}
            onClick={() => setRoadmapOpen(true)}
            sx={{ mr: 2 }}
          >
            개발진행 로드맵
          </Button>

          {isConnected ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              {/* 거래 모드 표시 */}
              <Chip
                icon={tradingMode === 'live' ? <TrendingUp /> : <Science />}
                label={tradingMode === 'live' ? "실전투자" : "모의투자"}
                color={tradingMode === 'live' ? "warning" : "primary"}
                variant="outlined"
                sx={{
                  fontWeight: 'bold',
                  borderWidth: 2
                }}
              />

              <Chip
                label={user?.name || 'User'}
                color="default"
                variant="outlined"
              />

              <IconButton
                color="inherit"
                size="small"
                onClick={() => window.location.href = '/mypage'}
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  mr: 1
                }}
              >
                <Person />
              </IconButton>

              <Button
                color="inherit"
                startIcon={<Logout />}
                onClick={handleLogout}
              >
                로그아웃
              </Button>
            </Box>
          ) : (
            <Button
              color="inherit"
              variant="outlined"
              onClick={onLoginClick}
            >
              로그인
            </Button>
          )}
        </Toolbar>
      </AppBar>

      {/* 로드맵 다이얼로그 */}
      <RoadmapDialog
        open={roadmapOpen}
        onClose={() => setRoadmapOpen(false)}
      />
    </>
  )
}

export default Header