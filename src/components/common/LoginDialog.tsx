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
  CircularProgress,
  Divider,
  Stack,
  Tab,
  Tabs,
  IconButton,
  InputAdornment
} from '@mui/material'
import {
  Email,
  Visibility,
  VisibilityOff,
  Login,
  PersonAdd,
  LinkedIn,
  ChatBubble
} from '@mui/icons-material'
import { useAppDispatch } from '../../hooks/redux'
import { loginSuccess } from '../../store/authSlice'
import { authService } from '../../services/auth'

interface LoginDialogProps {
  open: boolean
  onClose: () => void
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  )
}

const LoginDialog: React.FC<LoginDialogProps> = ({ open, onClose }) => {
  const dispatch = useAppDispatch()
  const [tabValue, setTabValue] = useState(0) // 0: 로그인, 1: 회원가입
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [kiwoomId, setKiwoomId] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
    setError('')
    setSuccessMessage('')
  }

  // 이메일 로그인
  const handleEmailLogin = async () => {
    setLoading(true)
    setError('')

    try {
      const { user, error } = await authService.signInWithEmail(email, password)
      
      if (error) {
        setError(error.message)
        setLoading(false)
        return
      }

      if (user) {
        // 프로필 정보 가져오기
        const { profile } = await authService.getProfile(user.id)
        
        dispatch(loginSuccess({
          user: {
            id: user.id,
            name: profile?.name || user.email || 'User',
            accounts: [profile?.kiwoom_account || 'DEMO'],
          },
          accounts: [profile?.kiwoom_account || 'DEMO'],
        }))
        
        // 로그인 성공 시 다이얼로그 닫기
        setLoading(false)
        onClose()
      }
    } catch (err: any) {
      setError('로그인 실패: ' + err.message)
      setLoading(false)
    }
  }

  // 이메일 회원가입
  const handleEmailSignUp = async () => {
    if (password !== confirmPassword) {
      setError('비밀번호가 일치하지 않습니다')
      return
    }

    if (password.length < 6) {
      setError('비밀번호는 최소 6자 이상이어야 합니다')
      return
    }

    setLoading(true)
    setError('')

    try {
      const { user, error } = await authService.signUpWithEmail(email, password, name, kiwoomId)
      
      if (error) {
        if (error.message.includes('already registered')) {
          setError('이미 등록된 이메일입니다')
        } else {
          setError(error.message)
        }
        return
      }

      if (user) {
        setSuccessMessage('회원가입이 완료되었습니다! 이메일을 확인하여 인증을 완료하고, 관리자 승인을 기다려주세요.')
        // 자동으로 로그인 탭으로 전환
        setTimeout(() => {
          setTabValue(0)
          setSuccessMessage('')
        }, 3000)
      }
    } catch (err: any) {
      setError('회원가입 실패: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  // 카카오 로그인 (추후 구현)
  const handleKakaoLogin = async () => {
    setError('카카오 로그인은 준비 중입니다.')
    // TODO: 카카오 OAuth 구현
  }

  // LinkedIn 로그인 (추후 구현)
  const handleLinkedInLogin = async () => {
    setError('LinkedIn 로그인은 준비 중입니다.')
    // TODO: LinkedIn OAuth 구현
  }

  // 데모 모드
  const handleDemoStart = () => {
    dispatch(loginSuccess({
      user: {
        id: 'demo_user',
        name: 'Demo User',
        accounts: ['DEMO12345'],
      },
      accounts: ['DEMO12345'],
    }))
    onClose()
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Typography variant="h5" fontWeight="bold">
          KyyQuant AI Solution
        </Typography>
        <Typography variant="body2" color="text.secondary">
          AI 기반 알고리즘 트레이딩 플랫폼
        </Typography>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} variant="fullWidth">
            <Tab label="로그인" icon={<Login />} iconPosition="start" />
            <Tab label="회원가입" icon={<PersonAdd />} iconPosition="start" />
          </Tabs>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        
        {successMessage && (
          <Alert severity="success" sx={{ mt: 2 }}>
            {successMessage}
          </Alert>
        )}

        {/* 로그인 탭 */}
        <TabPanel value={tabValue} index={0}>
          <Stack spacing={2}>
            <TextField
              fullWidth
              label="이메일"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              autoComplete="email"
            />

            <TextField
              fullWidth
              label="비밀번호"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoComplete="current-password"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              fullWidth
              variant="contained"
              onClick={handleEmailLogin}
              disabled={loading || !email || !password}
              startIcon={loading ? <CircularProgress size={20} /> : <Email />}
            >
              이메일로 로그인
            </Button>

            <Divider>또는</Divider>

            <Stack direction="row" spacing={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={handleKakaoLogin}
                disabled={loading}
                startIcon={<ChatBubble />}
                sx={{ 
                  backgroundColor: '#FEE500',
                  color: '#000000',
                  '&:hover': {
                    backgroundColor: '#FFEB3B'
                  }
                }}
              >
                카카오
              </Button>
              
              <Button
                fullWidth
                variant="outlined"
                onClick={handleLinkedInLogin}
                disabled={loading}
                startIcon={<LinkedIn />}
                sx={{ 
                  backgroundColor: '#0077B5',
                  color: '#FFFFFF',
                  borderColor: '#0077B5',
                  '&:hover': {
                    backgroundColor: '#006097',
                    borderColor: '#006097'
                  }
                }}
              >
                LinkedIn
              </Button>
            </Stack>

            <Button
              fullWidth
              variant="outlined"
              color="success"
              onClick={handleDemoStart}
              disabled={loading}
            >
              데모 모드로 시작
            </Button>
          </Stack>
        </TabPanel>

        {/* 회원가입 탭 */}
        <TabPanel value={tabValue} index={1}>
          <Stack spacing={2}>
            <TextField
              fullWidth
              label="이름"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={loading}
              autoComplete="name"
            />

            <TextField
              fullWidth
              label="이메일"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              autoComplete="email"
            />

            <TextField
              fullWidth
              label="키움증권 ID"
              value={kiwoomId}
              onChange={(e) => setKiwoomId(e.target.value)}
              disabled={loading}
              helperText="키움증권 계좌 ID를 입력하세요"
              required
            />

            <TextField
              fullWidth
              label="비밀번호"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoComplete="new-password"
              helperText="최소 6자 이상"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="비밀번호 확인"
              type={showPassword ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading}
              autoComplete="new-password"
              error={confirmPassword !== '' && password !== confirmPassword}
              helperText={confirmPassword !== '' && password !== confirmPassword ? '비밀번호가 일치하지 않습니다' : ''}
            />

            <Button
              fullWidth
              variant="contained"
              onClick={handleEmailSignUp}
              disabled={loading || !email || !password || !confirmPassword}
              startIcon={loading ? <CircularProgress size={20} /> : <PersonAdd />}
            >
              회원가입
            </Button>

            <Typography variant="body2" color="text.secondary" align="center">
              이미 계정이 있으신가요?{' '}
              <Button size="small" onClick={() => setTabValue(0)}>
                로그인
              </Button>
            </Typography>
          </Stack>
        </TabPanel>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          닫기
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default LoginDialog