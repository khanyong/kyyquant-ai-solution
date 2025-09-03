import React, { useEffect, useState } from 'react'
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
  Button
} from '@mui/material'
import { 
  Code, 
  ShowChart, 
  Assessment, 
  Monitor,
  Speed,
  Settings,
  TrendingUp,
  Announcement
} from '@mui/icons-material'
import Header from './components/common/Header'
import LoginDialog from './components/common/LoginDialog'
import StrategyBuilder from './components/StrategyBuilder'
import BacktestResults from './components/BacktestResults'
import SignalMonitor from './components/SignalMonitor'
import PerformanceDashboard from './components/PerformanceDashboard'
import TradingSettings from './components/TradingSettings'
import TestSupabase from './components/test/TestSupabase'
import AutoTradingPanel from './components/trading/AutoTradingPanel'
import OrderPanel from './components/trading/OrderPanel'
import PortfolioPanel from './components/trading/PortfolioPanel'
import MarketOverview from './components/trading/MarketOverview'
import Community from './components/community/Community'
import AdminApprovalPanel from './components/admin/AdminApprovalPanel'
import { useAppDispatch, useAppSelector } from './hooks/redux'
// import { connectWebSocket } from './services/websocket' // Removed - using Supabase instead
import { checkServerStatus } from './services/api'
import { authService } from './services/auth'
import { loginSuccess, logout } from './store/authSlice'

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

    // Supabase Auth 상태 모니터링
    const { data: authListener } = authService.onAuthStateChange(async (user) => {
      if (user) {
        try {
          // 프로필 정보 가져오기
          const { profile } = await authService.getProfile(user.id)
          
          dispatch(loginSuccess({
            user: {
              id: user.id,
              name: profile?.name || user.email || 'User',
              accounts: [profile?.kiwoom_account || 'DEMO'],
              role: profile?.role
            },
            accounts: [profile?.kiwoom_account || 'DEMO'],
          }))
        } catch (error) {
          console.warn('Profile fetch error:', error)
          // 프로필이 없어도 기본 정보로 로그인
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
              role: profile?.role
            },
            accounts: [profile?.kiwoom_account || 'DEMO'],
          }))
        } catch (error) {
          console.warn('Initial profile fetch error:', error)
          // 프로필이 없어도 기본 정보로 로그인
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
      }
    })

    return () => {
      authListener?.subscription.unsubscribe()
    }
  }, [isConnected, dispatch])

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
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
              <BacktestResults />
            </TabPanel>

            <TabPanel value={currentTab} index={3}>
              <SignalMonitor signals={[]} strategies={[]} />
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
                  <AutoTradingPanel strategies={activeStrategies} />
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
                <AdminApprovalPanel />
                <TestSupabase />
                <TradingSettings />
              </Stack>
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

export default App