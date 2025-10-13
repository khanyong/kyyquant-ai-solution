import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Stack,
  Alert,
  CircularProgress,
  Chip,
  Grid,
  TextField,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton
} from '@mui/material'
import {
  PlayArrow,
  Stop,
  Refresh,
  TrendingUp,
  TrendingDown,
  AttachMoney,
  ShowChart,
  AccountBalance
} from '@mui/icons-material'
import { kiwoomApi } from '../../services/kiwoomApiService'
import { supabase } from '../../lib/supabase'
import { useAppSelector } from '../../hooks/redux'

interface StockPosition {
  code: string
  name: string
  quantity: number
  avgPrice: number
  currentPrice: number
  profitLoss: number
  profitLossPercent: number
}

const KiwoomTradingPanel: React.FC = () => {
  const user = useAppSelector(state => state.auth.user)
  const [loading, setLoading] = useState(false)
  const [initialized, setInitialized] = useState(false)
  const [testMode, setTestMode] = useState(true)
  const [accountBalance, setAccountBalance] = useState<any>(null)
  const [positions, setPositions] = useState<StockPosition[]>([])
  const [error, setError] = useState<string | null>(null)
  const [stockCode, setStockCode] = useState('')
  const [orderQuantity, setOrderQuantity] = useState('1')
  const [orderPrice, setOrderPrice] = useState('')
  const [currentPrice, setCurrentPrice] = useState<any>(null)

  // 초기화
  useEffect(() => {
    initializeApi()
  }, [])

  const initializeApi = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Get current user
      const { data: { user: authUser } } = await supabase.auth.getUser()
      const userId = authUser?.id || user?.id
      
      if (!userId) {
        throw new Error('사용자 ID를 찾을 수 없습니다')
      }

      // Get current trading mode
      const { data: modeData } = await supabase.rpc('get_current_mode_info', {
        p_user_id: userId
      })
      
      const isTestMode = modeData?.current_mode === 'test'
      setTestMode(isTestMode)
      
      // Initialize Kiwoom API
      await kiwoomApi.initialize(userId, isTestMode)
      setInitialized(true)

      // Load initial data
      // Note: Commented out to avoid CORS error - use backend API instead
      // await loadAccountData()
    } catch (err: any) {
      console.error('Failed to initialize:', err)
      setError(err.message || '초기화 실패')
    } finally {
      setLoading(false)
    }
  }

  const loadAccountData = async () => {
    try {
      const balance = await kiwoomApi.getAccountBalance()
      setAccountBalance(balance)
      
      // Parse positions from balance data
      if (balance?.output2) {
        const positions: StockPosition[] = balance.output2.map((item: any) => ({
          code: item.pdno,
          name: item.prdt_name,
          quantity: parseInt(item.hldg_qty),
          avgPrice: parseFloat(item.pchs_avg_pric),
          currentPrice: parseFloat(item.prpr),
          profitLoss: parseFloat(item.evlu_pfls_amt),
          profitLossPercent: parseFloat(item.evlu_pfls_rt)
        }))
        setPositions(positions)
      }
    } catch (err: any) {
      console.error('Failed to load account data:', err)
      setError(err.message || '계좌 정보 로드 실패')
    }
  }

  const getCurrentPrice = async () => {
    if (!stockCode) {
      setError('종목 코드를 입력하세요')
      return
    }

    setLoading(true)
    try {
      const price = await kiwoomApi.getCurrentPrice(stockCode)
      setCurrentPrice(price)
      
      // Set order price to current price
      if (price?.output?.stck_prpr) {
        setOrderPrice(price.output.stck_prpr)
      }
    } catch (err: any) {
      setError(err.message || '현재가 조회 실패')
    } finally {
      setLoading(false)
    }
  }

  const handleBuy = async () => {
    if (!stockCode || !orderQuantity || !orderPrice) {
      setError('주문 정보를 모두 입력하세요')
      return
    }

    setLoading(true)
    try {
      const result = await kiwoomApi.buyStock(
        stockCode,
        parseInt(orderQuantity),
        parseInt(orderPrice)
      )
      
      if (result?.rt_cd === '0') {
        alert('매수 주문이 성공적으로 접수되었습니다')
        await loadAccountData()
      } else {
        throw new Error(result?.msg1 || '매수 주문 실패')
      }
    } catch (err: any) {
      setError(err.message || '매수 주문 실패')
    } finally {
      setLoading(false)
    }
  }

  const handleSell = async () => {
    if (!stockCode || !orderQuantity || !orderPrice) {
      setError('주문 정보를 모두 입력하세요')
      return
    }

    setLoading(true)
    try {
      const result = await kiwoomApi.sellStock(
        stockCode,
        parseInt(orderQuantity),
        parseInt(orderPrice)
      )
      
      if (result?.rt_cd === '0') {
        alert('매도 주문이 성공적으로 접수되었습니다')
        await loadAccountData()
      } else {
        throw new Error(result?.msg1 || '매도 주문 실패')
      }
    } catch (err: any) {
      setError(err.message || '매도 주문 실패')
    } finally {
      setLoading(false)
    }
  }

  if (!initialized) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CircularProgress size={24} />
            <Typography>키움 API 초기화 중...</Typography>
          </Box>
        </CardContent>
      </Card>
    )
  }

  return (
    <Box>
      <Stack spacing={3}>
        {/* 상태 표시 */}
        <Card>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="h6">
                키움증권 {testMode ? '모의투자' : '실전투자'}
              </Typography>
              <Stack direction="row" spacing={2}>
                <Chip 
                  label={testMode ? '모의투자' : '실전투자'} 
                  color={testMode ? 'info' : 'warning'}
                />
                <Button
                  startIcon={<Refresh />}
                  onClick={loadAccountData}
                  disabled={loading}
                >
                  새로고침
                </Button>
              </Stack>
            </Stack>
          </CardContent>
        </Card>

        {error && (
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* 계좌 정보 */}
        {accountBalance && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AccountBalance sx={{ mr: 1, verticalAlign: 'middle' }} />
                계좌 정보
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    예수금
                  </Typography>
                  <Typography variant="h6">
                    {parseInt(accountBalance.output1?.dnca_tot_amt || 0).toLocaleString()}원
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    총 평가금액
                  </Typography>
                  <Typography variant="h6">
                    {parseInt(accountBalance.output1?.tot_evlu_amt || 0).toLocaleString()}원
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    총 손익
                  </Typography>
                  <Typography 
                    variant="h6"
                    color={parseFloat(accountBalance.output1?.evlu_pfls_smtl_amt || 0) >= 0 ? 'success.main' : 'error.main'}
                  >
                    {parseInt(accountBalance.output1?.evlu_pfls_smtl_amt || 0).toLocaleString()}원
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    수익률
                  </Typography>
                  <Typography 
                    variant="h6"
                    color={parseFloat(accountBalance.output1?.evlu_pfls_rt || 0) >= 0 ? 'success.main' : 'error.main'}
                  >
                    {parseFloat(accountBalance.output1?.evlu_pfls_rt || 0).toFixed(2)}%
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* 주문 패널 */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <ShowChart sx={{ mr: 1, verticalAlign: 'middle' }} />
              주문
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="종목 코드"
                  value={stockCode}
                  onChange={(e) => setStockCode(e.target.value)}
                  placeholder="예: 005930"
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={getCurrentPrice}
                  disabled={loading || !stockCode}
                  sx={{ height: '56px' }}
                >
                  현재가 조회
                </Button>
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="주문 수량"
                  type="number"
                  value={orderQuantity}
                  onChange={(e) => setOrderQuantity(e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="주문 가격"
                  type="number"
                  value={orderPrice}
                  onChange={(e) => setOrderPrice(e.target.value)}
                />
              </Grid>
            </Grid>

            {currentPrice && (
              <Paper sx={{ p: 2, mt: 2, bgcolor: 'background.default' }}>
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">현재가</Typography>
                    <Typography variant="h6">
                      {parseInt(currentPrice.output?.stck_prpr || 0).toLocaleString()}원
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">전일 대비</Typography>
                    <Typography 
                      variant="h6"
                      color={parseInt(currentPrice.output?.prdy_vrss || 0) >= 0 ? 'error.main' : 'primary.main'}
                    >
                      {parseInt(currentPrice.output?.prdy_vrss || 0).toLocaleString()}원
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">등락률</Typography>
                    <Typography 
                      variant="h6"
                      color={parseFloat(currentPrice.output?.prdy_ctrt || 0) >= 0 ? 'error.main' : 'primary.main'}
                    >
                      {parseFloat(currentPrice.output?.prdy_ctrt || 0).toFixed(2)}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">거래량</Typography>
                    <Typography variant="h6">
                      {parseInt(currentPrice.output?.acml_vol || 0).toLocaleString()}주
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            )}

            <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
              <Button
                variant="contained"
                color="error"
                startIcon={<TrendingUp />}
                onClick={handleBuy}
                disabled={loading || !stockCode || !orderQuantity || !orderPrice}
                sx={{ flex: 1 }}
              >
                매수
              </Button>
              <Button
                variant="contained"
                color="primary"
                startIcon={<TrendingDown />}
                onClick={handleSell}
                disabled={loading || !stockCode || !orderQuantity || !orderPrice}
                sx={{ flex: 1 }}
              >
                매도
              </Button>
            </Stack>
          </CardContent>
        </Card>

        {/* 보유 종목 */}
        {positions.length > 0 && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AttachMoney sx={{ mr: 1, verticalAlign: 'middle' }} />
                보유 종목
              </Typography>
              
              <List>
                {positions.map((position, index) => (
                  <React.Fragment key={position.code}>
                    <ListItem>
                      <ListItemText
                        primary={position.name}
                        secondary={`${position.code} | ${position.quantity}주`}
                      />
                      <ListItemSecondaryAction>
                        <Stack alignItems="flex-end">
                          <Typography variant="body2">
                            현재가: {position.currentPrice.toLocaleString()}원
                          </Typography>
                          <Typography 
                            variant="body2"
                            color={position.profitLoss >= 0 ? 'error.main' : 'primary.main'}
                          >
                            {position.profitLoss >= 0 ? '+' : ''}{position.profitLoss.toLocaleString()}원
                            ({position.profitLossPercent >= 0 ? '+' : ''}{position.profitLossPercent.toFixed(2)}%)
                          </Typography>
                        </Stack>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < positions.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        )}
      </Stack>
    </Box>
  )
}

export default KiwoomTradingPanel