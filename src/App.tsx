import React, { useEffect, useState } from 'react'
import { Container, Grid, Paper, Box, Typography, Alert } from '@mui/material'
import Header from './components/Header'
import LoginDialog from './components/LoginDialog'
import StockChart from './components/StockChart'
import OrderPanel from './components/OrderPanel'
import PortfolioPanel from './components/PortfolioPanel'
import MarketOverview from './components/MarketOverview'
import { useAppDispatch, useAppSelector } from './hooks/redux'
import { connectWebSocket } from './services/websocket'
import { checkServerStatus } from './services/api'

function App() {
  const dispatch = useAppDispatch()
  const { isConnected, user } = useAppSelector(state => state.auth)
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [loginOpen, setLoginOpen] = useState(false)

  useEffect(() => {
    // 서버 상태 확인
    checkServerStatus().then(status => {
      setServerStatus(status ? 'online' : 'offline')
    })

    // WebSocket 연결
    if (isConnected) {
      connectWebSocket()
    }
  }, [isConnected])

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header onLoginClick={() => setLoginOpen(true)} />
      
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        {serverStatus === 'offline' && (
          <Alert severity="error" sx={{ mb: 2 }}>
            백엔드 서버에 연결할 수 없습니다. 서버를 실행해주세요.
          </Alert>
        )}

        {!isConnected ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom>
              키움 자동매매 시스템
            </Typography>
            <Typography variant="body1" color="text.secondary">
              로그인하여 시작하세요
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {/* 시장 개요 */}
            <Grid item xs={12}>
              <MarketOverview />
            </Grid>

            {/* 차트 */}
            <Grid item xs={12} lg={8}>
              <Paper sx={{ p: 2, height: 500 }}>
                <StockChart />
              </Paper>
            </Grid>

            {/* 주문 패널 */}
            <Grid item xs={12} lg={4}>
              <Paper sx={{ p: 2, height: 500 }}>
                <OrderPanel />
              </Paper>
            </Grid>

            {/* 포트폴리오 */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <PortfolioPanel />
              </Paper>
            </Grid>
          </Grid>
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