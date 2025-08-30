import React, { useState } from 'react'
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Box, 
  Chip,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  Link
} from '@mui/material'
import { 
  TrendingUp, 
  AccountBalance, 
  Logout,
  Settings,
  Map
} from '@mui/icons-material'
import { useAppSelector, useAppDispatch } from '../../hooks/redux'
import { logout, selectAccount } from '../../store/authSlice'
import { authService } from '../../services/auth'
import RoadmapDialog from './RoadmapDialog'

interface HeaderProps {
  onLoginClick: () => void
}

const Header: React.FC<HeaderProps> = ({ onLoginClick }) => {
  const dispatch = useAppDispatch()
  const { isConnected, user, accounts, selectedAccount } = useAppSelector(state => state.auth)
  const [roadmapOpen, setRoadmapOpen] = useState(false)

  const handleLogout = async () => {
    await authService.signOut()
    dispatch(logout())
  }

  const handleAccountChange = (event: any) => {
    dispatch(selectAccount(event.target.value))
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
            <FormControl size="small">
              <Select
                value={selectedAccount || ''}
                onChange={handleAccountChange}
                displayEmpty
                sx={{ minWidth: 150 }}
              >
                {accounts.map(account => (
                  <MenuItem key={account} value={account}>
                    <AccountBalance sx={{ mr: 1, fontSize: 16 }} />
                    {account}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Chip 
              label={user?.name || 'User'} 
              color="primary" 
              variant="outlined"
            />

            <IconButton color="inherit" size="small">
              <Settings />
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