import React, { useEffect, useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  Add,
  Remove,
  Refresh,
  ShowChart,
  AccountBalance
} from '@mui/icons-material'
import kiwoomService from '../services/kiwoomService'

interface StockData {
  stock_code: string
  stock_name: string
  current_price: number
  change: number
  change_rate: number
  volume: number
}

interface PortfolioItem {
  stock_code: string
  stock_name: string
  quantity: number
  avg_price: number
  current_price: number
  profit_loss: number
  profit_rate: number
}

interface OrderDialogProps {
  open: boolean
  onClose: () => void
  stockCode?: string
  stockName?: string
  currentPrice?: number
}

const OrderDialog: React.FC<OrderDialogProps> = ({
  open,
  onClose,
  stockCode = '',
  stockName = '',
  currentPrice = 0
}) => {
  const [orderType, setOrderType] = useState<'BUY' | 'SELL'>('BUY')
  const [quantity, setQuantity] = useState(1)
  const [price, setPrice] = useState(currentPrice)
  const [orderMethod, setOrderMethod] = useState<'LIMIT' | 'MARKET'>('LIMIT')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setPrice(currentPrice)
  }, [currentPrice])

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const success = await kiwoomService.sendOrder({
        stock_code: stockCode,
        stock_name: stockName,
        order_type: orderType,
        order_method: orderMethod,
        quantity,
        price: orderMethod === 'MARKET' ? 0 : price,
        status: 'PENDING'
      })

      if (success) {
        alert('주문이 성공적으로 접수되었습니다.')
        onClose()
      } else {
        alert('주문 접수에 실패했습니다.')
      }
    } catch (error) {
      console.error('Order error:', error)
      alert('주문 처리 중 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        주문하기 - {stockName} ({stockCode})
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Button
                fullWidth
                variant={orderType === 'BUY' ? 'contained' : 'outlined'}
                color="error"
                onClick={() => setOrderType('BUY')}
              >
                매수
              </Button>
            </Grid>
            <Grid item xs={6}>
              <Button
                fullWidth
                variant={orderType === 'SELL' ? 'contained' : 'outlined'}
                color="primary"
                onClick={() => setOrderType('SELL')}
              >
                매도
              </Button>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="수량"
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
                InputProps={{ inputProps: { min: 1 } }}
              />
            </Grid>
            <Grid item xs={6}>
              <Button
                fullWidth
                variant={orderMethod === 'LIMIT' ? 'contained' : 'outlined'}
                onClick={() => setOrderMethod('LIMIT')}
              >
                지정가
              </Button>
            </Grid>
            <Grid item xs={6}>
              <Button
                fullWidth
                variant={orderMethod === 'MARKET' ? 'contained' : 'outlined'}
                onClick={() => setOrderMethod('MARKET')}
              >
                시장가
              </Button>
            </Grid>
            {orderMethod === 'LIMIT' && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="가격"
                  type="number"
                  value={price}
                  onChange={(e) => setPrice(Number(e.target.value))}
                  InputProps={{ inputProps: { min: 0 } }}
                />
              </Grid>
            )}
            <Grid item xs={12}>
              <Typography variant="body2" color="textSecondary">
                예상 금액: {(quantity * (orderMethod === 'MARKET' ? currentPrice : price)).toLocaleString()}원
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          취소
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          color={orderType === 'BUY' ? 'error' : 'primary'}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : '주문'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

const KiwoomDashboard: React.FC = () => {
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([])
  const [watchlist, setWatchlist] = useState<StockData[]>([])
  const [loading, setLoading] = useState(true)
  const [connected, setConnected] = useState(false)
  const [orderDialog, setOrderDialog] = useState({
    open: false,
    stockCode: '',
    stockName: '',
    currentPrice: 0
  })

  useEffect(() => {
    // 초기 데이터 로드
    loadInitialData()

    // WebSocket 연결 상태 확인
    const checkConnection = setInterval(() => {
      setConnected(kiwoomService.isConnected())
    }, 1000)

    // 실시간 데이터 이벤트 리스너
    const handleStockUpdate = (event: CustomEvent) => {
      updateWatchlistItem(event.detail)
    }

    const handleBalanceUpdate = (event: CustomEvent) => {
      setPortfolio(event.detail)
    }

    window.addEventListener('stockUpdate', handleStockUpdate as any)
    window.addEventListener('balanceUpdate', handleBalanceUpdate as any)

    return () => {
      clearInterval(checkConnection)
      window.removeEventListener('stockUpdate', handleStockUpdate as any)
      window.removeEventListener('balanceUpdate', handleBalanceUpdate as any)
    }
  }, [])

  const loadInitialData = async () => {
    setLoading(true)
    try {
      const [portfolioData, watchlistData] = await Promise.all([
        kiwoomService.getPortfolio(),
        kiwoomService.getWatchlist()
      ])

      setPortfolio(portfolioData)
      
      // 관심종목 실시간 구독
      const watchlistItems: StockData[] = []
      for (const item of watchlistData) {
        kiwoomService.subscribeStock(item.stock_code)
        
        // 최신 가격 데이터 가져오기
        const prices = await kiwoomService.getStockPrices(item.stock_code, 1)
        if (prices.length > 0) {
          watchlistItems.push({
            stock_code: item.stock_code,
            stock_name: item.stock_name,
            current_price: prices[0].current_price,
            change: prices[0].change,
            change_rate: prices[0].change_rate,
            volume: prices[0].volume
          })
        }
      }
      setWatchlist(watchlistItems)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateWatchlistItem = (data: StockData) => {
    setWatchlist(prev => {
      const index = prev.findIndex(item => item.stock_code === data.stock_code)
      if (index >= 0) {
        const newList = [...prev]
        newList[index] = data
        return newList
      }
      return prev
    })
  }

  const handleRefresh = () => {
    kiwoomService.requestBalance()
    loadInitialData()
  }

  const handleOrder = (stock: StockData | PortfolioItem) => {
    setOrderDialog({
      open: true,
      stockCode: stock.stock_code,
      stockName: stock.stock_name,
      currentPrice: stock.current_price
    })
  }

  const formatNumber = (num: number) => {
    return num.toLocaleString('ko-KR')
  }

  const formatPercent = (num: number) => {
    const formatted = num.toFixed(2)
    return num > 0 ? `+${formatted}%` : `${formatted}%`
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* 연결 상태 */}
        <Grid item xs={12}>
          <Alert severity={connected ? 'success' : 'error'}>
            키움증권 API {connected ? '연결됨' : '연결 끊김'}
            <IconButton size="small" onClick={handleRefresh} sx={{ ml: 2 }}>
              <Refresh />
            </IconButton>
          </Alert>
        </Grid>

        {/* 포트폴리오 */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AccountBalance sx={{ mr: 1, verticalAlign: 'middle' }} />
                포트폴리오
              </Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>종목명</TableCell>
                      <TableCell align="right">보유수량</TableCell>
                      <TableCell align="right">평균단가</TableCell>
                      <TableCell align="right">현재가</TableCell>
                      <TableCell align="right">평가손익</TableCell>
                      <TableCell align="right">수익률</TableCell>
                      <TableCell align="center">주문</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {portfolio.map((item) => (
                      <TableRow key={item.stock_code}>
                        <TableCell>
                          {item.stock_name}
                          <Typography variant="caption" display="block" color="textSecondary">
                            {item.stock_code}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">{formatNumber(item.quantity)}</TableCell>
                        <TableCell align="right">{formatNumber(item.avg_price)}</TableCell>
                        <TableCell align="right">{formatNumber(item.current_price)}</TableCell>
                        <TableCell align="right">
                          <Typography color={item.profit_loss > 0 ? 'error' : 'primary'}>
                            {formatNumber(item.profit_loss)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={formatPercent(item.profit_rate)}
                            color={item.profit_rate > 0 ? 'error' : 'primary'}
                            size="small"
                            icon={item.profit_rate > 0 ? <TrendingUp /> : <TrendingDown />}
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleOrder(item)}
                          >
                            주문
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* 관심종목 */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <ShowChart sx={{ mr: 1, verticalAlign: 'middle' }} />
                관심종목
              </Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>종목</TableCell>
                      <TableCell align="right">현재가</TableCell>
                      <TableCell align="right">등락률</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {watchlist.map((item) => (
                      <TableRow 
                        key={item.stock_code}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => handleOrder(item)}
                      >
                        <TableCell>
                          <Typography variant="body2">{item.stock_name}</Typography>
                          <Typography variant="caption" color="textSecondary">
                            {item.stock_code}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          {formatNumber(item.current_price)}
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={formatPercent(item.change_rate)}
                            color={item.change_rate > 0 ? 'error' : 'primary'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 주문 다이얼로그 */}
      <OrderDialog
        open={orderDialog.open}
        onClose={() => setOrderDialog({ ...orderDialog, open: false })}
        stockCode={orderDialog.stockCode}
        stockName={orderDialog.stockName}
        currentPrice={orderDialog.currentPrice}
      />
    </Box>
  )
}

export default KiwoomDashboard