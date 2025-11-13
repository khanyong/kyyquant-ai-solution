import React, { useEffect, useState, lazy, Suspense } from 'react'
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
  Stack,
  Button,
  CircularProgress
} from '@mui/material'
import {
  Code,
  ShowChart,
  Assessment,
  Monitor,
  Speed,
  Settings,
  TrendingUp,
  Announcement,
  CompareArrows
} from '@mui/icons-material'
import Header from './components/common/Header'
import LoginDialog from './components/common/LoginDialog'
import LandingPage from './components/landing/LandingPage'
import { useAppDispatch, useAppSelector } from './hooks/redux'
// import { connectWebSocket } from './services/websocket' // Removed - using Supabase instead
import { checkServerStatus } from './services/api'
import { authService } from './services/auth'
import { loginSuccess, logout } from './store/authSlice'

// Lazy load components for code splitting
const StrategyBuilder = lazy(() => import('./components/StrategyBuilder'))
const BacktestRunner = lazy(() => import('./components/BacktestRunner'))
const SignalMonitor = lazy(() => import('./components/SignalMonitor'))
const PerformanceDashboard = lazy(() => import('./components/PerformanceDashboard'))
const AutoTradingPanel = lazy(() => import('./components/trading/AutoTradingPanelV2'))
const OrderPanel = lazy(() => import('./components/trading/OrderPanel'))
const PortfolioPanel = lazy(() => import('./components/trading/PortfolioPanel'))
const MarketOverview = lazy(() => import('./components/trading/MarketOverview'))
const Community = lazy(() => import('./components/community/Community'))
const TradingSettings = lazy(() => import('./components/TradingSettings'))
const TestSupabase = lazy(() => import('./components/test/TestSupabase'))
const TestBacktestTable = lazy(() => import('./components/test/TestBacktestTable'))
const InvestmentUniverse = lazy(() => import('./components/InvestmentUniverse'))
const AdminApprovalPanel = lazy(() => import('./components/admin/AdminApprovalPanel'))
const TestInvestmentUniverse = lazy(() => import('./components/TestInvestmentUniverse'))
const DebugPortfolio = lazy(() => import('./pages/DebugPortfolio'))

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
          <Suspense fallback={
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
              <CircularProgress />
            </Box>
          }>
            {children}
          </Suspense>
        </Box>
      )}
    </div>
  )
}

function App() {
  const dispatch = useAppDispatch()
  const { isConnected, user } = useAppSelector(state => state.auth)
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [loginOpen, setLoginOpen] = useState(false)
  const [currentTab, setCurrentTab] = useState(0)
  const [demoMode, setDemoMode] = useState(false)
  const [activeStrategies, setActiveStrategies] = useState<any[]>([])
  
  // 전략 실행 함수
  const executeStrategy = (strategy: any) => {
    setActiveStrategies([...activeStrategies, strategy])
    // 자동매매 탭으로 이동 (인덱스 조정)
    setCurrentTab(5)
  }

  useEffect(() => {
    checkServerStatus().then(status => {
      setServerStatus(status ? 'online' : 'offline')
    })

    if (isConnected) {
      // connectWebSocket() // Removed - using Supabase instead
    }

    // Tab change event listener
    const handleTabChange = (event: CustomEvent) => {
      if (event.detail && typeof event.detail.tab === 'number') {
        setCurrentTab(event.detail.tab)
      }
    }

    window.addEventListener('changeTab', handleTabChange as any)

    // Supabase Auth 상태 모니터링
    const { data: authListener } = authService.onAuthStateChange(async (user) => {
      console.log('🎯 App: Auth state changed, user:', user?.email)

      if (user) {
        console.log('✅ App: User authenticated, fetching profile immediately')

        // 프로필을 먼저 가져온 후 로그인 처리 (role 정보 포함)
        authService.getProfile(user.id)
          .then(({ profile }) => {
            if (profile) {
              console.log('📝 App: Profile loaded with role:', profile.role)
              dispatch(loginSuccess({
                user: {
                  id: user.id,
                  name: profile.name || user.email || 'User',
                  accounts: [profile.kiwoom_account || 'DEMO'],
                  role: profile.role || 'user'
                },
                accounts: [profile.kiwoom_account || 'DEMO'],
              }))
            } else {
              // 프로필이 없으면 기본값으로
              console.log('⚠️ App: No profile, using defaults')
              dispatch(loginSuccess({
                user: {
                  id: user.id,
                  name: user.email || 'User',
                  accounts: ['DEMO'],
                  role: 'user'
                },
                accounts: ['DEMO'],
              }))
            }
          })
          .catch(error => {
            console.warn('⚠️ App: Profile fetch error, using defaults:', error)
            // 에러 시에도 로그인은 허용 (기본 role)
            dispatch(loginSuccess({
              user: {
                id: user.id,
                name: user.email || 'User',
                accounts: ['DEMO'],
                role: 'user'
              },
              accounts: ['DEMO'],
            }))
          })
      } else {
        console.log('🚪 App: User signed out')
        dispatch(logout())
      }
    })

    // 초기 세션 체크
    authService.getCurrentUser().then(async (user) => {
      console.log('🔍 App: Checking initial session, user:', user?.email)

      if (user) {
        // 프로필을 먼저 가져온 후 Redux 업데이트
        authService.getProfile(user.id)
          .then(({ profile }) => {
            if (profile) {
              console.log('✅ App: Initial session restored with role:', profile.role)
              dispatch(loginSuccess({
                user: {
                  id: user.id,
                  name: profile.name || user.email || 'User',
                  accounts: [profile.kiwoom_account || 'DEMO'],
                  role: profile.role || 'user'
                },
                accounts: [profile.kiwoom_account || 'DEMO'],
              }))
            } else {
              console.log('⚠️ App: No profile for initial session')
              dispatch(loginSuccess({
                user: {
                  id: user.id,
                  name: user.email || 'User',
                  accounts: ['DEMO'],
                  role: 'user'
                },
                accounts: ['DEMO'],
              }))
            }
          })
          .catch(error => {
            console.warn('⚠️ App: Initial profile fetch error:', error)
            dispatch(loginSuccess({
              user: {
                id: user.id,
                name: user.email || 'User',
                accounts: ['DEMO'],
                role: 'user'
              },
              accounts: ['DEMO'],
            }))
          })
      }
    })

    return () => {
      authListener?.subscription.unsubscribe()
      window.removeEventListener('changeTab', handleTabChange as any)
    }
  }, [isConnected, dispatch])

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
  }

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      width: '100%',
      maxWidth: '100vw',
      overflowX: 'hidden',
      bgcolor: 'background.default'
    }}>
      {!isConnected ? (
        // Landing Page - Full Screen
        <LandingPage onLoginClick={() => setLoginOpen(true)} />
      ) : (
        <>
          <Header onLoginClick={() => setLoginOpen(true)} />

          <Container maxWidth="xl" sx={{ mt: 3, mb: 3, flexGrow: 1 }}>
            {serverStatus === 'offline' && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                데모 모드: 백엔드 서버를 사용할 수 없어 모의 데이터를 사용합니다.
              </Alert>
            )}

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
                    height: 3,
                    borderRadius: '3px 3px 0 0'
                  },
                  '& .MuiTab-root': {
                    textTransform: 'none',
                    fontSize: '0.95rem',
                    fontWeight: 500,
                    color: 'rgba(255, 255, 255, 0.6)',
                    minHeight: 72,
                    padding: '12px 16px',
                    transition: 'all 0.3s ease',
                    borderRight: '1px solid rgba(255, 255, 255, 0.05)',
                    '&:last-child': {
                      borderRight: 'none'
                    },
                    '&:hover': {
                      backgroundColor: 'rgba(144, 202, 249, 0.08)',
                      color: 'rgba(255, 255, 255, 0.9)'
                    },
                    '&.Mui-selected': {
                      color: '#90caf9',
                      backgroundColor: 'rgba(144, 202, 249, 0.15)',
                      boxShadow: 'inset 0 -3px 0 0 #90caf9'
                    },
                    '& .MuiSvgIcon-root': {
                      fontSize: '1.5rem',
                      marginBottom: '4px'
                    }
                  },
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
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
                  icon={<Settings />} 
                  label="설정" 
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#607d8b'
                      }
                    }
                  }}
                />
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
              <BacktestRunner />
            </TabPanel>

            <TabPanel value={currentTab} index={3}>
              <SignalMonitor />
            </TabPanel>

            <TabPanel value={currentTab} index={4}>
              <PerformanceDashboard />
            </TabPanel>

            <TabPanel value={currentTab} index={5}>
              <Grid container spacing={3}>
                {/* 시장 개요 */}
                <Grid item xs={12}>
                  <MarketOverview />
                </Grid>
                
                {/* 자동매매 전략 */}
                <Grid item xs={12}>
                  <AutoTradingPanel />
                </Grid>
                
                {/* 주문 패널과 포트폴리오 */}
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
              <Stack spacing={3}>
                <DebugPortfolio />
                <TestBacktestTable />
                <TestInvestmentUniverse />
                <InvestmentUniverse />
                <AdminApprovalPanel />
                <TestSupabase />
                <TradingSettings />
              </Stack>
            </TabPanel>
          </Container>
        </>
      )}

      <LoginDialog
        open={loginOpen}
        onClose={() => setLoginOpen(false)}
      />
    </Box>
  )
}

export default App