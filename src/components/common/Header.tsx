import React, { useState } from 'react'
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
  Science,
  Timeline
} from '@mui/icons-material'
import { useAppSelector, useAppDispatch } from '../../hooks/redux'
import { logout } from '../../store/authSlice'
import { authService } from '../../services/auth'
import RoadmapDialog from './RoadmapDialog'
import RoadmapDialogV2 from './RoadmapDialogV2'

interface HeaderProps {
  onLoginClick: () => void
}

const Header: React.FC<HeaderProps> = ({ onLoginClick }) => {
  const dispatch = useAppDispatch()
  const { isConnected, user, tradingMode } = useAppSelector(state => state.auth)
  const [roadmapOpen, setRoadmapOpen] = useState(false)
  const [roadmapV2Open, setRoadmapV2Open] = useState(false)

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

          {/* 개발 로드맵 버튼 (Phase 1 - 완료) */}
          <Button
            color="inherit"
            variant="outlined"
            size="small"
            startIcon={<Map />}
            onClick={() => setRoadmapOpen(true)}
            sx={{ mr: 1, borderColor: 'divider', color: 'text.secondary' }}
          >
            로드맵 (완료)
          </Button>

          {/* 개발 로드맵 버튼 (Phase 2 - 진행중) */}
          <Button
            color="secondary"
            variant="contained"
            size="small"
            startIcon={<Timeline />}
            onClick={() => setRoadmapV2Open(true)}
            sx={{ mr: 2 }}
          >
            로드맵 Phase 2
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

      {/* 로드맵 다이얼로그 (Phase 1) */}
      <RoadmapDialog
        open={roadmapOpen}
        onClose={() => setRoadmapOpen(false)}
      />

      {/* 로드맵 다이얼로그 (Phase 2) */}
      <RoadmapDialogV2
        open={roadmapV2Open}
        onClose={() => setRoadmapV2Open(false)}
      />
    </>
  )
}

export default Header