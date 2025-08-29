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
        setError('로그인에 실패했습니다.')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '서버 연결에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>키움증권 로그인</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            키움 OpenAPI+가 설치되어 있어야 합니다.
            계정 정보는 선택사항입니다 (미입력시 키움 로그인창 표시).
          </Typography>

          <TextField
            fullWidth
            label="계좌번호 (선택)"
            value={accountNo}
            onChange={(e) => setAccountNo(e.target.value)}
            margin="normal"
            disabled={loading}
          />

          <TextField
            fullWidth
            label="비밀번호 (선택)"
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
            label="모의투자 모드"
            sx={{ mt: 2 }}
          />

          {!demoMode && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              실거래 모드입니다. 실제 주문이 실행됩니다!
            </Alert>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          취소
        </Button>
        <Button
          onClick={handleLogin}
          variant="contained"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? '연결 중...' : '로그인'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default LoginDialog