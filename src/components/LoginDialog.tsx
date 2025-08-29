import React, { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  Alert,
  FormControlLabel,
  Checkbox,
  CircularProgress
} from '@mui/material'
import { useAppDispatch } from '../hooks/redux'
import { loginSuccess } from '../store/authSlice'
import { login } from '../services/api'

interface LoginDialogProps {
  open: boolean
  onClose: () => void
}

const LoginDialog: React.FC<LoginDialogProps> = ({ open, onClose }) => {
  const dispatch = useAppDispatch()
  const [accountNo, setAccountNo] = useState('')
  const [password, setPassword] = useState('')
  const [demoMode, setDemoMode] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await login(accountNo, password, demoMode)
      
      if (response.success) {
        dispatch(loginSuccess({
          user: {
            id: response.user_id,
            name: response.user_name,
            accounts: response.accounts,
          },
          accounts: response.accounts,
        }))
        onClose()
      } else {
        setError('Login failed. Please try again.')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Server connection failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>KyyQuant AI Solution Login</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Welcome to KyyQuant AI Algorithmic Trading Platform.
            Enter your credentials to access the trading system.
          </Typography>

          <TextField
            fullWidth
            label="Account Number (Optional)"
            value={accountNo}
            onChange={(e) => setAccountNo(e.target.value)}
            margin="normal"
            disabled={loading}
          />

          <TextField
            fullWidth
            label="Password (Optional)"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            disabled={loading}
          />

          <FormControlLabel
            control={
              <Checkbox
                checked={demoMode}
                onChange={(e) => setDemoMode(e.target.checked)}
                disabled={loading}
              />
            }
            label="Demo Mode"
            sx={{ mt: 2 }}
          />

          {!demoMode && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              Live Trading Mode. Real orders will be executed!
            </Alert>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleLogin}
          variant="contained"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Connecting...' : 'Login'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default LoginDialog