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
  Stack
} from '@mui/material'
import { 
  Code, 
  ShowChart, 
  Assessment, 
  Monitor,
  Speed,
  Settings
} from '@mui/icons-material'
import Header from './components/Header'
import LoginDialog from './components/LoginDialog'
import StrategyBuilder from './components/StrategyBuilder'
import BacktestResults from './components/BacktestResults'
import SignalMonitor from './components/SignalMonitor'
import PerformanceDashboard from './components/PerformanceDashboard'
import { useAppDispatch, useAppSelector } from './hooks/redux'
import { connectWebSocket } from './services/websocket'
import { checkServerStatus } from './services/api'

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

function AppQuant() {
  const dispatch = useAppDispatch()
  const { isConnected, user } = useAppSelector(state => state.auth)
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [loginOpen, setLoginOpen] = useState(false)
  const [currentTab, setCurrentTab] = useState(0)
  // Enable demo mode if no backend server is available
  const [demoMode] = useState(() => {
    // In production (Vercel), always use demo mode if no backend
    return !import.meta.env.VITE_API_URL || import.meta.env.VITE_API_URL === 'https://api.example.com'
  })

  useEffect(() => {
    checkServerStatus().then(status => {
      setServerStatus(status ? 'online' : 'offline')
    })

    if (isConnected) {
      connectWebSocket()
    }
  }, [isConnected])

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

        {!isConnected && !demoMode ? (
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
                데모 모드 - 로그인 없이 플랫폼을 체험해보세요
              </Typography>
            </Stack>
          </Paper>
        ) : (
          <>
            {/* 탭 메뉴 */}
            <Paper sx={{ mb: 3 }}>
              <Tabs 
                value={currentTab} 
                onChange={handleTabChange}
                variant="fullWidth"
                sx={{ borderBottom: 1, borderColor: 'divider' }}
              >
                <Tab 
                  icon={<Code />} 
                  label="전략 빌더" 
                  iconPosition="start"
                />
                <Tab 
                  icon={<Assessment />} 
                  label="백테스팅" 
                  iconPosition="start"
                />
                <Tab 
                  icon={<Monitor />} 
                  label="실시간 신호" 
                  iconPosition="start"
                />
                <Tab 
                  icon={<ShowChart />} 
                  label="성과 분석" 
                  iconPosition="start"
                />
                <Tab 
                  icon={<Settings />} 
                  label="설정" 
                  iconPosition="start"
                />
              </Tabs>
            </Paper>

            {/* 탭 컨텐츠 */}
            <TabPanel value={currentTab} index={0}>
              <StrategyBuilder />
            </TabPanel>

            <TabPanel value={currentTab} index={1}>
              <BacktestResults />
            </TabPanel>

            <TabPanel value={currentTab} index={2}>
              <SignalMonitor />
            </TabPanel>

            <TabPanel value={currentTab} index={3}>
              <PerformanceDashboard />
            </TabPanel>

            <TabPanel value={currentTab} index={4}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom>설정</Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>API 설정</Typography>
                      <Typography variant="body2" color="text.secondary">
                        키움 OpenAPI+ 연결 상태 및 설정
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>리스크 관리</Typography>
                      <Typography variant="body2" color="text.secondary">
                        전역 리스크 파라미터 설정
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>알림 설정</Typography>
                      <Typography variant="body2" color="text.secondary">
                        신호 발생 시 알림 방법 설정
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>데이터 관리</Typography>
                      <Typography variant="body2" color="text.secondary">
                        히스토리컬 데이터 다운로드 및 관리
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Paper>
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

export default AppQuant