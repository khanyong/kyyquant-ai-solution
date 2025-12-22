import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
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
import LandingPage from './components/landing/LandingPage'
import StrategyBuilder from './components/StrategyBuilder'
import BacktestResults from './components/BacktestResults'
import BacktestResultsList from './components/BacktestResultsList'
import BacktestRunner from './components/BacktestRunner'
import SignalMonitor from './components/SignalMonitor'
import StrategyMarket from './components/StrategyMarket'
import AutoTradingPanel from './components/trading/AutoTradingPanelV2'
import MarketOverview from './components/trading/MarketOverview'
import MarketMonitor from './components/MarketMonitor'
import Community from './components/community/Community'
import VisualRetirementPlanner from './components/simulation/VisualRetirementPlanner'
import Settings from './pages/Settings'
import TradingSettings from './pages/TradingSettings'
import MyPage from './pages/MyPage'
import TradingSettingsWithUniverse from './components/TradingSettingsWithUniverse'
import AdminDashboard from './pages/AdminDashboard'
import AuthCallback from './pages/AuthCallback'
import ApiKeyTest from './pages/ApiKeyTest'
import AboutPage from './pages/AboutPage'
import ServicesPage from './pages/ServicesPage'
import ContactPage from './pages/ContactPage'
import { useAppDispatch, useAppSelector } from './hooks/redux'
// import { connectWebSocket } from './services/websocket' // Removed - using Supabase
// import { checkServerStatus } from './services/api' // Removed - using Supabase
import { authService } from './services/auth'
import { loginSuccess, logout } from './store/authSlice'
import { supabase } from './lib/supabase'
import { useAuth } from './contexts/AuthContext'

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
  const { t } = useTranslation()
  const { user: authUser, role } = useAuth()
  const { isConnected, user } = useAppSelector(state => state.auth)
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [loginOpen, setLoginOpen] = useState(false)
  const [currentTab, setCurrentTab] = useState(0)
  const [activeStrategies, setActiveStrategies] = useState<any[]>([])
  const [isAdmin, setIsAdmin] = useState(false)

  // Debug log
  console.log('🎯 MainApp: isConnected =', isConnected, ', currentTab =', currentTab)

  // 전략 실행 함수
  const executeStrategy = (strategy: any) => {
    setActiveStrategies([...activeStrategies, strategy])
    // 자동매매 탭으로 이동
    setCurrentTab(5)
  }

  // 탭 네비게이션 이벤트 리스너
  useEffect(() => {
    const handleNavigateToStrategyBuilder = (event: CustomEvent) => {
      setCurrentTab(1) // 전략 빌더 탭으로 이동
      // 필터링된 유니버스 정보를 전달할 수 있음
      if (event.detail?.universe) {
        localStorage.setItem('filteredUniverse', JSON.stringify(event.detail.universe))
      }
    }

    const handleNavigateToInvestmentSettings = () => {
      setCurrentTab(2) // 투자설정 탭으로 이동
    }

    window.addEventListener('navigateToStrategyBuilder', handleNavigateToStrategyBuilder as EventListener)
    window.addEventListener('navigateToInvestmentSettings', handleNavigateToInvestmentSettings as EventListener)

    return () => {
      window.removeEventListener('navigateToStrategyBuilder', handleNavigateToStrategyBuilder as EventListener)
      window.removeEventListener('navigateToInvestmentSettings', handleNavigateToInvestmentSettings as EventListener)
    }
  }, [])

  // Check admin status from AuthContext role
  useEffect(() => {
    setIsAdmin(role === 'admin')
  }, [role])

  useEffect(() => {
    setServerStatus('online') // Supabase is always online
  }, [])

  // Sync AuthContext user state with Redux
  useEffect(() => {
    if (authUser) {
      // User is logged in via AuthContext
      authService.getProfile(authUser.id).then(({ profile }) => {
        dispatch(loginSuccess({
          user: {
            id: authUser.id,
            name: profile?.name || authUser.email || 'User',
            accounts: [profile?.kiwoom_account || 'DEMO'],
          },
          accounts: [profile?.kiwoom_account || 'DEMO'],
        }))
      }).catch(error => {
        console.warn('Profile fetch error:', error)
        dispatch(loginSuccess({
          user: {
            id: authUser.id,
            name: authUser.email || 'User',
            accounts: ['DEMO'],
          },
          accounts: ['DEMO'],
        }))
      })
    } else {
      // User is logged out
      dispatch(logout())
    }
  }, [authUser, dispatch])

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      {!isConnected ? (
        // Landing Page - Full Screen
        <LandingPage onLoginClick={() => setLoginOpen(true)} />
      ) : (
        <>
          <Header onLoginClick={() => setLoginOpen(true)} />

          <Container maxWidth="xl" sx={{ mt: 3, mb: 3, flexGrow: 1 }}>
            {serverStatus === 'offline' && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                {t('common.demo_mode')}
              </Alert>
            )}

            {/* 탭 메뉴 */}
            <Paper
              elevation={3}
              sx={{
                mb: 3,
                bgcolor: 'background.paper',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                overflow: 'hidden'
              }}
            >
              <Tabs
                value={currentTab}
                onChange={handleTabChange}
                variant="fullWidth"
                textColor="primary"
                indicatorColor="primary"
                sx={{
                  '& .MuiTab-root': {
                    textTransform: 'none',
                    minHeight: 72,
                    padding: '12px 16px',
                    transition: 'all 0.3s ease',
                    opacity: 0.7,
                    '&:hover': {
                      opacity: 1,
                      bgcolor: 'rgba(0, 0, 0, 0.04)',
                    },
                    '&.Mui-selected': {
                      opacity: 1,
                      fontWeight: 700,
                    },
                    '& .MuiSvgIcon-root': {
                      fontSize: '1.5rem',
                      marginBottom: '4px'
                    }
                  },
                  '& .MuiTabs-indicator': {
                    height: 3,
                    borderRadius: '3px 3px 0 0'
                  }
                }}
              >
                <Tab
                  icon={<Announcement />}
                  label={
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', lineHeight: 1 }}>
                      <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>Community</Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', mt: 0.5, opacity: 0.8 }}>커뮤니티</Typography>
                    </Box>
                  }
                />
                <Tab
                  icon={<Code />}
                  label={
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', lineHeight: 1 }}>
                      <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>Strategy Builder</Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', mt: 0.5, opacity: 0.8 }}>전략 빌더</Typography>
                    </Box>
                  }
                />
                <Tab
                  icon={<SettingsIcon />}
                  label={
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', lineHeight: 1 }}>
                      <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>Universe Builder</Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', mt: 0.5, opacity: 0.8 }}>투자 유니버스</Typography>
                    </Box>
                  }
                />
                <Tab
                  icon={<Assessment />}
                  label={
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', lineHeight: 1 }}>
                      <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>Backtest</Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', mt: 0.5, opacity: 0.8 }}>백테스트</Typography>
                    </Box>
                  }
                />
                <Tab
                  icon={<Monitor />}
                  label={
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', lineHeight: 1 }}>
                      <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>Live Signals</Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', mt: 0.5, opacity: 0.8 }}>실시간 시그널</Typography>
                    </Box>
                  }
                />
                <Tab
                  icon={<TrendingUp />}
                  label={
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', lineHeight: 1 }}>
                      <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>Auto Trading</Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', mt: 0.5, opacity: 0.8 }}>자동매매</Typography>
                    </Box>
                  }
                />
                <Tab
                  icon={<ShowChart />}
                  label={
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', lineHeight: 1 }}>
                      <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>Market</Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', mt: 0.5, opacity: 0.8 }}>전략 마켓</Typography>
                    </Box>
                  }
                />
                {isAdmin && (
                  <Tab
                    icon={<AdminPanelSettings />}
                    label={
                      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', lineHeight: 1 }}>
                        <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>Admin</Typography>
                        <Typography variant="caption" sx={{ fontSize: '0.7rem', mt: 0.5, opacity: 0.8 }}>관리자</Typography>
                      </Box>
                    }
                  />
                )}
                <Tab
                  icon={<Speed />}
                  label={
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', lineHeight: 1 }}>
                      <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>IPC</Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', mt: 0.5, opacity: 0.8 }}>자산운용</Typography>
                    </Box>
                  }
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
              <TradingSettingsWithUniverse />
            </TabPanel>

            <TabPanel value={currentTab} index={3}>
              <BacktestRunner />
            </TabPanel>

            <TabPanel value={currentTab} index={4}>
              <SignalMonitor />
            </TabPanel>

            <TabPanel value={currentTab} index={5}>
              <Grid container spacing={3}>


                <Grid item xs={12}>
                  {role && (role === 'premium' || role === 'admin') ? (
                    <AutoTradingPanel />
                  ) : (
                    <Paper sx={{ p: 3 }}>
                      <Alert severity="warning" sx={{ mb: 2 }}>
                        <Typography variant="h6" gutterBottom>
                          {t('auto_trading.premium_only')}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 2 }}>
                          {t('auto_trading.premium_description')}
                        </Typography>
                        <Typography variant="body2">
                          • {t('auto_trading.feature_247')}<br />
                          • {t('auto_trading.feature_monitoring')}<br />
                          • {t('auto_trading.feature_multi_strategy')}<br />
                          • {t('auto_trading.feature_universe')}
                        </Typography>
                      </Alert>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {t('auto_trading.upgrade_message')}
                        </Typography>
                        <Chip
                          label={t('auto_trading.view_premium')}
                          color="primary"
                          onClick={() => navigate('/pricing')}
                          sx={{ mt: 2, cursor: 'pointer' }}
                        />
                      </Box>
                    </Paper>
                  )}
                </Grid>
              </Grid>
            </TabPanel>

            <TabPanel value={currentTab} index={6}>
              <StrategyMarket />
            </TabPanel>

            {isAdmin && (
              <TabPanel value={currentTab} index={7}>
                <AdminDashboard />
              </TabPanel>
            )}

            <TabPanel value={currentTab} index={isAdmin ? 8 : 7}>
              <VisualRetirementPlanner />
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

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/" element={<MainApp />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/services" element={<ServicesPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/backtest/results" element={<BacktestResultsList />} />
        <Route path="/backtest/results/:backtestId" element={<BacktestResults />} />
        <Route path="/investment-settings" element={<TradingSettings />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/mypage" element={<MyPage />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/api-test" element={<ApiKeyTest />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App