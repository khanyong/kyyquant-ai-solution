import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { 
  Container, 
  Grid, 
  Paper, 
  Box, 
  Typography, 
  Alert,
  Tab,
  Tabs,
  Chip,
  Stack
} from '@mui/material'
import { 
  Code, 
  ShowChart, 
  Assessment, 
  Monitor,
  Speed,
  Settings as SettingsIcon,
  TrendingUp,
  Announcement,
  AdminPanelSettings
} from '@mui/icons-material'
import Header from './components/common/Header'
import LoginDialog from './components/common/LoginDialog'
import StrategyBuilder from './components/StrategyBuilder'
import BacktestResults from './components/BacktestResults'
import SignalMonitor from './components/SignalMonitor'
import PerformanceDashboard from './components/PerformanceDashboard'
import AutoTradingPanel from './components/trading/AutoTradingPanel'
import OrderPanel from './components/trading/OrderPanel'
import PortfolioPanel from './components/trading/PortfolioPanel'
import MarketOverview from './components/trading/MarketOverview'
import Community from './components/community/Community'
import Settings from './pages/Settings'
import TradingSettings from './pages/TradingSettings'
import AdminDashboard from './pages/AdminDashboard'
import { useAppDispatch, useAppSelector } from './hooks/redux'
import { connectWebSocket } from './services/websocket'
import { checkServerStatus } from './services/api'
import { authService } from './services/auth'
import { loginSuccess, logout } from './store/authSlice'
import { supabase } from './lib/supabase'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  )
}

function MainApp() {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { isConnected, user } = useAppSelector(state => state.auth)
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [loginOpen, setLoginOpen] = useState(false)
  const [currentTab, setCurrentTab] = useState(0)
  const [activeStrategies, setActiveStrategies] = useState<any[]>([])
  const [isAdmin, setIsAdmin] = useState(false)
  
  // 전략 실행 함수
  const executeStrategy = (strategy: any) => {
    setActiveStrategies([...activeStrategies, strategy])
    // 자동매매 탭으로 이동
    setCurrentTab(5)
  }

  // Check admin status
  useEffect(() => {
    const checkAdminStatus = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (user) {
        const { data: profile } = await supabase
          .from('profiles')
          .select('is_admin')
          .eq('id', user.id)
          .single()
        
        setIsAdmin(profile?.is_admin || false)
      }
    }
    checkAdminStatus()
  }, [user])

  useEffect(() => {
    checkServerStatus().then(status => {
      setServerStatus(status ? 'online' : 'offline')
    })

    if (isConnected) {
      connectWebSocket()
    }

    // Supabase Auth 상태 모니터링
    const { data: authListener } = authService.onAuthStateChange(async (user) => {
      if (user) {
        try {
          const { profile } = await authService.getProfile(user.id)
          
          dispatch(loginSuccess({
            user: {
              id: user.id,
              name: profile?.name || user.email || 'User',
              accounts: [profile?.kiwoom_account || 'DEMO'],
            },
            accounts: [profile?.kiwoom_account || 'DEMO'],
          }))
        } catch (error) {
          console.warn('Profile fetch error:', error)
          dispatch(loginSuccess({
            user: {
              id: user.id,
              name: user.email || 'User',
              accounts: ['DEMO'],
            },
            accounts: ['DEMO'],
          }))
        }
      } else {
        dispatch(logout())
      }
    })

    // 초기 세션 체크
    authService.getCurrentUser().then(async (user) => {
      if (user) {
        try {
          const { profile } = await authService.getProfile(user.id)
          
          dispatch(loginSuccess({
            user: {
              id: user.id,
              name: profile?.name || user.email || 'User',
              accounts: [profile?.kiwoom_account || 'DEMO'],
            },
            accounts: [profile?.kiwoom_account || 'DEMO'],
          }))
        } catch (error) {
          console.warn('Initial profile fetch error:', error)
          dispatch(loginSuccess({
            user: {
              id: user.id,
              name: user.email || 'User',
              accounts: ['DEMO'],
            },
            accounts: ['DEMO'],
          }))
        }
      }
    })

    return () => {
      authListener?.subscription.unsubscribe()
    }
  }, [isConnected, dispatch])

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    if (isAdmin && newValue === 7) {
      // Admin tab - keep as separate route for security
      navigate('/admin')
    } else {
      setCurrentTab(newValue)
    }
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      <Header onLoginClick={() => setLoginOpen(true)} />
      
      <Container maxWidth="xl" sx={{ mt: 3, mb: 3, flexGrow: 1 }}>
        {serverStatus === 'offline' && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            데모 모드: 백엔드 서버를 사용할 수 없어 모의 데이터를 사용합니다.
          </Alert>
        )}

        {!isConnected ? (
          <Paper sx={{ p: 6, textAlign: 'center' }}>
            <Stack spacing={3} alignItems="center">
              <ShowChart sx={{ fontSize: 80, color: 'primary.main' }} />
              <Typography variant="h3" fontWeight="bold">
                KyyQuant AI Solution
              </Typography>
              <Typography variant="h6" color="text.secondary">
                AI 기반 알고리즘 트레이딩 플랫폼
              </Typography>
              <Stack direction="row" spacing={2}>
                <Chip icon={<Code />} label="보조지표 기반 자동매매" />
                <Chip icon={<Assessment />} label="백테스팅 & 최적화" />
                <Chip icon={<Speed />} label="실시간 신호 모니터링" />
              </Stack>
              <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
                로그인하여 프로그램 매매를 시작하세요
              </Typography>
            </Stack>
          </Paper>
        ) : (
          <>
            {/* 탭 메뉴 */}
            <Paper 
              elevation={3}
              sx={{ 
                mb: 3,
                background: 'linear-gradient(135deg, rgba(25, 28, 51, 0.9) 0%, rgba(30, 30, 46, 0.95) 100%)',
                borderRadius: 2,
                overflow: 'hidden'
              }}
            >
              <Tabs 
                value={currentTab} 
                onChange={handleTabChange}
                variant="fullWidth"
                sx={{ 
                  '& .MuiTabs-indicator': {
                    backgroundColor: '#90caf9',
                    height: 4,
                    borderRadius: '2px 2px 0 0'
                  },
                  '& .MuiTab-root': {
                    textTransform: 'none',
                    fontSize: '0.9rem',
                    fontWeight: 600,
                    color: 'rgba(255, 255, 255, 0.6)',
                    minHeight: 64,
                    padding: '8px 12px',
                    transition: 'all 0.3s ease',
                    borderRight: '1px solid rgba(255, 255, 255, 0.1)',
                    flex: 1,
                    minWidth: 0,
                    '&:last-child': {
                      borderRight: 'none'
                    },
                    '&:hover': {
                      backgroundColor: 'rgba(144, 202, 249, 0.08)',
                      color: 'rgba(255, 255, 255, 0.9)'
                    },
                    '&.Mui-selected': {
                      color: '#fff',
                      backgroundColor: 'rgba(144, 202, 249, 0.2)',
                      borderBottom: 'none'
                    },
                    '& .MuiSvgIcon-root': {
                      fontSize: '1.3rem',
                      marginBottom: '2px'
                    }
                  },
                  borderBottom: '2px solid rgba(255, 255, 255, 0.1)',
                  '& .MuiTabs-flexContainer': {
                    justifyContent: 'space-between'
                  }
                }}
              >
                <Tab 
                  icon={<Announcement />} 
                  label="커뮤니티" 
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#ffc107'
                      }
                    }
                  }}
                />
                <Tab 
                  icon={<Code />} 
                  label="전략 빌더" 
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#4caf50'
                      }
                    }
                  }}
                />
                <Tab 
                  icon={<Assessment />} 
                  label="백테스팅" 
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#ff9800'
                      }
                    }
                  }}
                />
                <Tab 
                  icon={<Monitor />} 
                  label="실시간 신호" 
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#00bcd4'
                      }
                    }
                  }}
                />
                <Tab 
                  icon={<ShowChart />} 
                  label="성과 분석" 
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#9c27b0'
                      }
                    }
                  }}
                />
                <Tab 
                  icon={<TrendingUp />} 
                  label="자동매매" 
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#f44336'
                      }
                    }
                  }}
                />
                <Tab 
                  icon={<SettingsIcon />} 
                  label={
                    <Stack direction="row" spacing={0.5} alignItems="center">
                      <span>투자설정</span>
                      <Chip 
                        label="상세" 
                        size="small" 
                        sx={{ 
                          height: 16, 
                          fontSize: '0.65rem',
                          '& .MuiChip-label': { px: 0.5 }
                        }} 
                      />
                    </Stack>
                  }
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#607d8b'
                      }
                    }
                  }}
                />
                {isAdmin && (
                  <Tab 
                    icon={<AdminPanelSettings />} 
                    label="관리자" 
                    sx={{
                      '&.Mui-selected': {
                        '& .MuiSvgIcon-root': {
                          color: '#ff5722'
                        }
                      }
                    }}
                  />
                )}
              </Tabs>
            </Paper>

            {/* 탭 컨텐츠 */}
            <TabPanel value={currentTab} index={0}>
              <Community />
            </TabPanel>
            
            <TabPanel value={currentTab} index={1}>
              <StrategyBuilder onExecute={executeStrategy} />
            </TabPanel>

            <TabPanel value={currentTab} index={2}>
              <BacktestResults />
            </TabPanel>

            <TabPanel value={currentTab} index={3}>
              <SignalMonitor />
            </TabPanel>

            <TabPanel value={currentTab} index={4}>
              <PerformanceDashboard />
            </TabPanel>

            <TabPanel value={currentTab} index={5}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <MarketOverview />
                </Grid>
                
                <Grid item xs={12}>
                  <AutoTradingPanel strategies={activeStrategies} />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <OrderPanel />
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <PortfolioPanel />
                  </Paper>
                </Grid>
              </Grid>
            </TabPanel>

            <TabPanel value={currentTab} index={6}>
              <TradingSettings />
            </TabPanel>
          </>
        )}
      </Container>

      <LoginDialog 
        open={loginOpen} 
        onClose={() => setLoginOpen(false)} 
      />
    </Box>
  )
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainApp />} />
        <Route path="/investment-settings" element={<TradingSettings />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App