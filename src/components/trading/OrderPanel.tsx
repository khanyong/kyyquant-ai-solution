import React, { useState } from 'react'
import {
  Box,
  Typography,
  TextField,
  Button,
  ToggleButton,
  ToggleButtonGroup,
  Stack,
  Divider,
  Alert,
  InputAdornment,
  Chip
} from '@mui/material'
import { ShoppingCart, Sell } from '@mui/icons-material'
import { useAppSelector, useAppDispatch } from '../../hooks/redux'
import { placeOrder } from '../../services/api'
import { addToHistory, setError } from '../../store/orderSlice'

const OrderPanel: React.FC = () => {
  const dispatch = useAppDispatch()
  const { selectedAccount } = useAppSelector(state => state.auth)
  const { selectedStock } = useAppSelector(state => state.market)
  const { error } = useAppSelector(state => state.order)

  const [orderType, setOrderType] = useState<'buy' | 'sell'>('buy')
  const [orderMethod, setOrderMethod] = useState<'limit' | 'market'>('limit')
  const [quantity, setQuantity] = useState('')
  const [price, setPrice] = useState('')
  const [loading, setLoading] = useState(false)

  const handleOrderTypeChange = (event: React.MouseEvent<HTMLElement>, newType: 'buy' | 'sell') => {
    if (newType !== null) {
      setOrderType(newType)
    }
  }

  const handleOrderMethodChange = (event: React.MouseEvent<HTMLElement>, newMethod: 'limit' | 'market') => {
    if (newMethod !== null) {
      setOrderMethod(newMethod)
    }
  }

  const calculateTotal = () => {
    const qty = parseInt(quantity) || 0
    const prc = parseInt(price) || selectedStock?.price || 0
    return qty * prc
  }

  const handleSubmit = async () => {
    if (!selectedAccount || !selectedStock) {
      dispatch(setError('계좌와 종목을 선택해주세요'))
      return
    }

    if (!quantity || (orderMethod === 'limit' && !price)) {
      dispatch(setError('수량과 가격을 입력해주세요'))
      return
    }

    setLoading(true)
    dispatch(setError(null))

    try {
      const order = {
        accountNo: selectedAccount,
        stockCode: selectedStock.code,
        orderType,
        quantity: parseInt(quantity),
        price: orderMethod === 'limit' ? parseInt(price) : 0,
        orderMethod,
      }

      const response = await placeOrder(order)
      
      if (response.success) {
        dispatch(addToHistory(order))
        // Reset form
        setQuantity('')
        setPrice('')
        alert('주문이 전송되었습니다')
      } else {
        dispatch(setError(response.message || '주문 실패'))
      }
    } catch (err: any) {
      dispatch(setError(err.response?.data?.detail || '주문 처리 중 오류가 발생했습니다'))
    } finally {
      setLoading(false)
    }
  }

  const setPercentage = (percent: number) => {
    // This would calculate based on available balance
    // For now, just set example values
    setQuantity(String(Math.floor(100 * percent / 100)))
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        주문
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => dispatch(setError(null))}>
          {error}
        </Alert>
      )}

      {!selectedStock ? (
        <Alert severity="info">
          <Typography variant="body2" gutterBottom fontWeight="bold">
            📌 수동 주문 패널
          </Typography>
          <Typography variant="body2">
            시장 상황에 따라 직접 매수/매도 주문을 입력할 수 있습니다.
            <br />
            종목을 선택하면 주문을 시작할 수 있습니다.
          </Typography>
        </Alert>
      ) : (
        <Stack spacing={2}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              선택 종목
            </Typography>
            <Typography variant="body1">
              {selectedStock.name} ({selectedStock.code})
            </Typography>
            <Chip 
              label={`₩${selectedStock.price.toLocaleString()}`}
              size="small"
              color="primary"
            />
          </Box>

          <Divider />

          <ToggleButtonGroup
            value={orderType}
            exclusive
            onChange={handleOrderTypeChange}
            fullWidth
          >
            <ToggleButton value="buy" color="error">
              <ShoppingCart sx={{ mr: 1 }} />
              매수
            </ToggleButton>
            <ToggleButton value="sell" color="primary">
              <Sell sx={{ mr: 1 }} />
              매도
            </ToggleButton>
          </ToggleButtonGroup>

          <ToggleButtonGroup
            value={orderMethod}
            exclusive
            onChange={handleOrderMethodChange}
            fullWidth
            size="small"
          >
            <ToggleButton value="limit">
              지정가
            </ToggleButton>
            <ToggleButton value="market">
              시장가
            </ToggleButton>
          </ToggleButtonGroup>

          <TextField
            label="수량"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            type="number"
            fullWidth
            InputProps={{
              endAdornment: <InputAdornment position="end">주</InputAdornment>,
            }}
          />

          <Stack direction="row" spacing={1}>
            <Button size="small" onClick={() => setPercentage(25)}>25%</Button>
            <Button size="small" onClick={() => setPercentage(50)}>50%</Button>
            <Button size="small" onClick={() => setPercentage(75)}>75%</Button>
            <Button size="small" onClick={() => setPercentage(100)}>100%</Button>
          </Stack>

          {orderMethod === 'limit' && (
            <TextField
              label="가격"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              type="number"
              fullWidth
              InputProps={{
                endAdornment: <InputAdornment position="end">원</InputAdornment>,
              }}
            />
          )}

          <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
            <Stack direction="row" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                주문 총액
              </Typography>
              <Typography variant="h6">
                ₩{calculateTotal().toLocaleString()}
              </Typography>
            </Stack>
          </Box>

          <Button
            variant="contained"
            color={orderType === 'buy' ? 'error' : 'primary'}
            size="large"
            fullWidth
            onClick={handleSubmit}
            disabled={loading || !selectedStock || !selectedAccount}
          >
            {loading ? '처리 중...' : orderType === 'buy' ? '매수 주문' : '매도 주문'}
          </Button>
        </Stack>
      )}
    </Box>
  )
}

export default OrderPanel