import React from 'react'
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
  FormControl
} from '@mui/material'
import { 
  TrendingUp, 
  AccountBalance, 
  Logout,
  Settings
} from '@mui/icons-material'
import { useAppSelector, useAppDispatch } from '../hooks/redux'
import { logout, selectAccount } from '../store/authSlice'

interface HeaderProps {
  onLoginClick: () => void
}

const Header: React.FC<HeaderProps> = ({ onLoginClick }) => {
  const dispatch = useAppDispatch()
  const { isConnected, user, accounts, selectedAccount } = useAppSelector(state => state.auth)

  const handleLogout = () => {
    dispatch(logout())
  }

  const handleAccountChange = (event: any) => {
    dispatch(selectAccount(event.target.value))
  }

  return (
    <AppBar position="static" elevation={0} sx={{ borderBottom: 1, borderColor: 'divider' }}>
      <Toolbar>
        <TrendingUp sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          KyyQuant AI Solution
        </Typography>

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
  )
}

export default Header