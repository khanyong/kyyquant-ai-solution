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
import PerformanceDashboard from './components/PerformanceDashboard'
import AutoTradingPanel from './components/trading/AutoTradingPanelV2'
import OrderPanel from './components/trading/OrderPanel'
import PortfolioPanel from './components/trading/PortfolioPanel'
import MarketOverview from './components/trading/MarketOverview'
import KiwoomTradingPanel from './components/trading/KiwoomTradingPanel'
import MarketMonitor from './components/MarketMonitor'
import Community from './components/community/Community'
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
    if (isAdmin && newValue === 7) {
      // Admin tab - keep as separate route for security
      navigate('/admin')
    } else {
      setCurrentTab(newValue)
    }
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
                  label={t('tabs.community')}
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
                  label={t('tabs.strategy_builder')}
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#4caf50'
                      }
                    }
                  }}
                />
                <Tab
                  icon={<SettingsIcon />}
                  label={
                    <Stack direction="row" spacing={0.5} alignItems="center">
                      <span>{t('tabs.investment_settings')}</span>
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
                <Tab
                  icon={<Assessment />}
                  label={t('tabs.backtesting')}
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
                  label={t('tabs.realtime_signals')}
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#00bcd4'
                      }
                    }
                  }}
                />
                <Tab
                  icon={<TrendingUp />}
                  label={t('tabs.auto_trading')}
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#f44336'
                      }
                    }
                  }}
                />
                <Tab
                  icon={<ShowChart />}
                  label={t('tabs.performance')}
                  sx={{
                    '&.Mui-selected': {
                      '& .MuiSvgIcon-root': {
                        color: '#9c27b0'
                      }
                    }
                  }}
                />
                {isAdmin && (
                  <Tab
                    icon={<AdminPanelSettings />}
                    label={t('tabs.admin')}
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
                  <MarketOverview />
                </Grid>

                <Grid item xs={12}>
                  <KiwoomTradingPanel />
                </Grid>

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
                          • {t('auto_trading.feature_247')}<br/>
                          • {t('auto_trading.feature_monitoring')}<br/>
                          • {t('auto_trading.feature_multi_strategy')}<br/>
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
              <PerformanceDashboard />
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
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/api-test" element={<ApiKeyTest />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App