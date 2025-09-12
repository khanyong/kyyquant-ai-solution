import React, { useState, useEffect } from 'react'
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  RadioGroup,
  FormControlLabel,
  Radio,
  Alert,
  Box,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  CircularProgress,
  Chip,
  Stack,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material'
import {
  AccountBalance,
  Security,
  CheckCircle,
  Warning,
  Info,
  Close,
  Refresh,
  Delete,
  Settings,
  TrendingUp,
  AccountBalanceWallet
} from '@mui/icons-material'
import { kiwoomAuth } from '../../services/kiwoomAuth'
import { useAppSelector } from '../../hooks/redux'

interface AccountConnectProps {
  onConnect?: (account: any) => void
}

const AccountConnect: React.FC<AccountConnectProps> = ({ onConnect }) => {
  const user = useAppSelector(state => state.auth.user)
  const [accountType, setAccountType] = useState<'mock' | 'real'>('mock')
  const [isConnecting, setIsConnecting] = useState(false)
  const [connectedAccounts, setConnectedAccounts] = useState<any[]>([])
  const [activeStep, setActiveStep] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [showSettings, setShowSettings] = useState(false)
  const [selectedAccount, setSelectedAccount] = useState<any>(null)
  
  // 계좌 설정 상태
  const [accountSettings, setAccountSettings] = useState({
    maxTradeAmount: 1000000,
    maxPositionSize: 10,
    allowAutoTrading: false
  })
  
  useEffect(() => {
    loadConnectedAccounts()
  }, [user])
  
  const loadConnectedAccounts = async () => {
    if (!user?.id) return
    
    try {
      const accounts = await kiwoomAuth.getSavedAccounts(user.id)
      setConnectedAccounts(accounts)
    } catch (error) {
      console.error('Failed to load accounts:', error)
    }
  }
  
  const handleConnect = async () => {
    if (!user?.id) {
      setError('로그인이 필요합니다')
      return
    }
    
    setIsConnecting(true)
    setError(null)
    setActiveStep(1)
    
    try {
      // OAuth 인증 URL 생성
      const authUrl = kiwoomAuth.getAuthorizationUrl(accountType)
      
      // 팝업 창 열기
      const authWindow = window.open(
        authUrl,
        'kiwoom-auth',
        'width=500,height=700,left=100,top=100'
      )
      
      // 콜백 처리
      const handleCallback = async (event: MessageEvent) => {
        if (event.data.type === 'kiwoom-auth-callback') {
          const { code, state, error: authError } = event.data
          
          if (authError) {
            setError(`인증 실패: ${authError}`)
            setIsConnecting(false)
            setActiveStep(0)
            return
          }
          
          if (code) {
            setActiveStep(2)
            
            try {
              // Access Token 획득
              const tokenData = await kiwoomAuth.getAccessToken(code, state as 'mock' | 'real')
              
              setActiveStep(3)
              
              // 계좌 목록 조회
              const accounts = await kiwoomAuth.getAccounts(tokenData.access_token, state as 'mock' | 'real')
              
              // 각 계좌 저장
              for (const account of accounts) {
                await kiwoomAuth.saveAccountToSupabase(user.id, account, tokenData)
              }
              
              setActiveStep(4)
              
              // 연결된 계좌 목록 새로고침
              await loadConnectedAccounts()
              
              // 성공 콜백
              if (onConnect && accounts.length > 0) {
                onConnect(accounts[0])
              }
              
              // 3초 후 초기화
              setTimeout(() => {
                setActiveStep(0)
                setIsConnecting(false)
              }, 3000)
              
            } catch (error) {
              setError(`계좌 연동 실패: ${error}`)
              setIsConnecting(false)
              setActiveStep(0)
            }
          }
          
          // 이벤트 리스너 제거
          window.removeEventListener('message', handleCallback)
          
          // 팝업 창 닫기
          if (authWindow && !authWindow.closed) {
            authWindow.close()
          }
        }
      }
      
      window.addEventListener('message', handleCallback)
      
      // 팝업이 닫혔는지 체크
      const checkInterval = setInterval(() => {
        if (authWindow && authWindow.closed) {
          clearInterval(checkInterval)
          window.removeEventListener('message', handleCallback)
          
          if (activeStep === 1) {
            setError('인증이 취소되었습니다')
            setIsConnecting(false)
            setActiveStep(0)
          }
        }
      }, 1000)
      
    } catch (error) {
      setError(`연동 실패: ${error}`)
      setIsConnecting(false)
      setActiveStep(0)
    }
  }
  
  const handleDisconnect = async (accountId: string) => {
    try {
      await kiwoomAuth.disconnectAccount(accountId)
      await loadConnectedAccounts()
    } catch (error) {
      setError(`연결 해제 실패: ${error}`)
    }
  }
  
  const handleRefreshToken = async (accountId: string) => {
    try {
      await kiwoomAuth.checkAndRefreshToken(accountId)
      await loadConnectedAccounts()
    } catch (error) {
      setError(`토큰 갱신 실패: ${error}`)
    }
  }
  
  const steps = [
    '계좌 유형 선택',
    '키움증권 로그인',
    'Access Token 획득',
    '계좌 정보 조회',
    '연동 완료'
  ]
  
  return (
    <>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" alignItems="center" spacing={2} mb={3}>
            <AccountBalance color="primary" sx={{ fontSize: 32 }} />
            <Box>
              <Typography variant="h5" fontWeight="bold">
                키움증권 계좌 연동
              </Typography>
              <Typography variant="body2" color="text.secondary">
                모의투자 또는 실전투자 계좌를 연동하여 자동매매를 시작하세요
              </Typography>
            </Box>
          </Stack>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
          
          {!isConnecting ? (
            <>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  계좌 유형 선택
                </Typography>
                <RadioGroup
                  value={accountType}
                  onChange={(e) => setAccountType(e.target.value as 'mock' | 'real')}
                  row
                >
                  <FormControlLabel
                    value="mock"
                    control={<Radio />}
                    label={
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Typography>모의투자</Typography>
                        <Chip label="추천" size="small" color="success" />
                      </Stack>
                    }
                  />
                  <FormControlLabel
                    value="real"
                    control={<Radio />}
                    label={
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Typography>실전투자</Typography>
                        <Warning fontSize="small" color="warning" />
                      </Stack>
                    }
                  />
                </RadioGroup>
              </Box>
              
              {accountType === 'real' && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  실전투자는 실제 자금이 거래됩니다. 신중하게 사용하세요.
                </Alert>
              )}
              
              <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1, mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom color="primary">
                  연동 전 준비사항
                </Typography>
                <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
                  <li>키움증권 계좌 개설 완료</li>
                  <li>키움 OpenAPI 신청 및 승인</li>
                  <li>{accountType === 'mock' ? '모의투자 신청 완료' : 'API 실전투자 신청 완료'}</li>
                  <li>공인인증서 또는 간편인증 준비</li>
                </Typography>
              </Box>
            </>
          ) : (
            <Box sx={{ mt: 3 }}>
              <Stepper activeStep={activeStep} orientation="vertical">
                {steps.map((label, index) => (
                  <Step key={label}>
                    <StepLabel
                      optional={
                        index === activeStep && isConnecting ? (
                          <CircularProgress size={20} />
                        ) : null
                      }
                    >
                      {label}
                    </StepLabel>
                    <StepContent>
                      <Typography variant="body2" color="text.secondary">
                        {index === 0 && `${accountType === 'mock' ? '모의투자' : '실전투자'} 계좌를 선택했습니다`}
                        {index === 1 && '키움증권 로그인 페이지로 이동합니다...'}
                        {index === 2 && 'Access Token을 받아오는 중...'}
                        {index === 3 && '계좌 정보를 조회하는 중...'}
                        {index === 4 && '계좌 연동이 완료되었습니다!'}
                      </Typography>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </Box>
          )}
        </CardContent>
        
        {!isConnecting && (
          <CardActions>
            <Button
              variant="contained"
              size="large"
              onClick={handleConnect}
              disabled={isConnecting || !user}
              startIcon={<Security />}
              fullWidth
            >
              계좌 연동 시작
            </Button>
          </CardActions>
        )}
      </Card>
      
      {/* 연결된 계좌 목록 */}
      {connectedAccounts.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              연결된 계좌
            </Typography>
            
            <Stack spacing={2}>
              {connectedAccounts.map((account) => (
                <Card key={account.id} variant="outlined">
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <AccountBalanceWallet color={account.is_connected ? 'success' : 'disabled'} />
                          <Box>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {account.account_name || account.account_number}
                            </Typography>
                            <Stack direction="row" spacing={1} alignItems="center">
                              <Chip
                                label={account.account_type === 'mock' ? '모의투자' : '실전투자'}
                                size="small"
                                color={account.account_type === 'mock' ? 'info' : 'warning'}
                              />
                              {account.is_connected ? (
                                <Chip
                                  label="연결됨"
                                  size="small"
                                  color="success"
                                  icon={<CheckCircle />}
                                />
                              ) : (
                                <Chip
                                  label="연결 끊김"
                                  size="small"
                                  color="error"
                                />
                              )}
                              {account.allow_auto_trading && (
                                <Chip
                                  label="자동매매"
                                  size="small"
                                  color="primary"
                                  icon={<TrendingUp />}
                                />
                              )}
                            </Stack>
                          </Box>
                        </Stack>
                      </Box>
                      
                      <Stack direction="row" spacing={1}>
                        <Tooltip title="토큰 갱신">
                          <IconButton
                            size="small"
                            onClick={() => handleRefreshToken(account.id)}
                          >
                            <Refresh />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="설정">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedAccount(account)
                              setShowSettings(true)
                            }}
                          >
                            <Settings />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="연결 해제">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDisconnect(account.id)}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </Stack>
                    
                    {account.current_balance && (
                      <Box sx={{ mt: 2, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                        <Stack direction="row" justifyContent="space-between">
                          <Typography variant="body2" color="text.secondary">
                            예수금
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {account.current_balance.toLocaleString()}원
                          </Typography>
                        </Stack>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </CardContent>
        </Card>
      )}
      
      {/* 계좌 설정 다이얼로그 */}
      <Dialog open={showSettings} onClose={() => setShowSettings(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          계좌 설정
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <TextField
              label="최대 거래 금액"
              type="number"
              value={accountSettings.maxTradeAmount}
              onChange={(e) => setAccountSettings({
                ...accountSettings,
                maxTradeAmount: Number(e.target.value)
              })}
              fullWidth
              helperText="1회 최대 주문 금액을 설정합니다"
            />
            
            <TextField
              label="최대 보유 종목 수"
              type="number"
              value={accountSettings.maxPositionSize}
              onChange={(e) => setAccountSettings({
                ...accountSettings,
                maxPositionSize: Number(e.target.value)
              })}
              fullWidth
              helperText="동시에 보유할 수 있는 최대 종목 수"
            />
            
            <FormControlLabel
              control={
                <Radio
                  checked={accountSettings.allowAutoTrading}
                  onChange={(e) => setAccountSettings({
                    ...accountSettings,
                    allowAutoTrading: e.target.checked
                  })}
                />
              }
              label="자동매매 허용"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>취소</Button>
          <Button variant="contained" onClick={() => {
            // TODO: 설정 저장
            setShowSettings(false)
          }}>
            저장
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

export default AccountConnect