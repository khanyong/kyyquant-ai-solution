import React from 'react'
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Typography,
  Stack,
  Paper,
  Divider
} from '@mui/material'

interface OrderPriceStrategy {
  buy: {
    type: 'best_ask' | 'best_bid' | 'mid_price' | 'market'
    offset: number
  }
  sell: {
    type: 'best_bid' | 'best_ask' | 'mid_price' | 'market'
    offset: number
  }
}

interface OrderPriceStrategySelectorProps {
  value: OrderPriceStrategy
  onChange: (value: OrderPriceStrategy) => void
}

const ORDER_TYPES = [
  { value: 'best_ask', label: '매도 1호가 (즉시 체결)', description: '팔려는 사람의 가격으로 매수' },
  { value: 'best_bid', label: '매수 1호가 (대기)', description: '사려는 사람의 가격으로 대기' },
  { value: 'mid_price', label: '중간가', description: '(매도1호가 + 매수1호가) / 2' },
  { value: 'market', label: '시장가', description: '즉시 체결 (가격 무관)' }
]

export default function OrderPriceStrategySelector({ value, onChange }: OrderPriceStrategySelectorProps) {
  const handleBuyTypeChange = (type: string) => {
    onChange({
      ...value,
      buy: { ...value.buy, type: type as any }
    })
  }

  const handleBuyOffsetChange = (offset: number) => {
    onChange({
      ...value,
      buy: { ...value.buy, offset }
    })
  }

  const handleSellTypeChange = (type: string) => {
    onChange({
      ...value,
      sell: { ...value.sell, type: type as any }
    })
  }

  const handleSellOffsetChange = (offset: number) => {
    onChange({
      ...value,
      sell: { ...value.sell, offset }
    })
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        💰 주문 가격 전략
      </Typography>
      <Typography variant="caption" color="text.secondary" gutterBottom display="block">
        매수/매도 시 어떤 가격으로 주문할지 선택하세요
      </Typography>

      <Stack spacing={3} sx={{ mt: 2 }}>
        {/* 매수 가격 전략 */}
        <Box>
          <Typography variant="subtitle2" gutterBottom fontWeight="bold" color="error">
            📈 매수 주문 가격
          </Typography>

          <Stack direction="row" spacing={2} alignItems="center">
            <FormControl fullWidth>
              <InputLabel>매수 가격 기준</InputLabel>
              <Select
                value={value.buy.type}
                onChange={(e) => handleBuyTypeChange(e.target.value)}
                label="매수 가격 기준"
              >
                {ORDER_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    <Box>
                      <Typography variant="body2">{type.label}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {type.description}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {value.buy.type !== 'market' && (
              <TextField
                label="가격 조정"
                type="number"
                value={value.buy.offset}
                onChange={(e) => handleBuyOffsetChange(parseInt(e.target.value) || 0)}
                InputProps={{
                  endAdornment: '원'
                }}
                sx={{ width: 200 }}
                helperText="양수: 더 비싸게, 음수: 더 싸게"
              />
            )}
          </Stack>

          <Box sx={{ mt: 1, p: 2, bgcolor: 'error.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              예시: 매도 1호가가 72,000원일 때
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {value.buy.type === 'best_ask' && `→ 72,000원 ${value.buy.offset > 0 ? `+ ${value.buy.offset}원` : value.buy.offset < 0 ? `- ${Math.abs(value.buy.offset)}원` : ''}에 매수 주문`}
              {value.buy.type === 'best_bid' && `→ 71,950원 ${value.buy.offset > 0 ? `+ ${value.buy.offset}원` : value.buy.offset < 0 ? `- ${Math.abs(value.buy.offset)}원` : ''}에 매수 주문 (대기)`}
              {value.buy.type === 'mid_price' && `→ 71,975원 ${value.buy.offset > 0 ? `+ ${value.buy.offset}원` : value.buy.offset < 0 ? `- ${Math.abs(value.buy.offset)}원` : ''}에 매수 주문`}
              {value.buy.type === 'market' && `→ 시장가로 즉시 매수`}
            </Typography>
          </Box>
        </Box>

        <Divider />

        {/* 매도 가격 전략 */}
        <Box>
          <Typography variant="subtitle2" gutterBottom fontWeight="bold" color="primary">
            📉 매도 주문 가격
          </Typography>

          <Stack direction="row" spacing={2} alignItems="center">
            <FormControl fullWidth>
              <InputLabel>매도 가격 기준</InputLabel>
              <Select
                value={value.sell.type}
                onChange={(e) => handleSellTypeChange(e.target.value)}
                label="매도 가격 기준"
              >
                {ORDER_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    <Box>
                      <Typography variant="body2">{type.label}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {type.description}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {value.sell.type !== 'market' && (
              <TextField
                label="가격 조정"
                type="number"
                value={value.sell.offset}
                onChange={(e) => handleSellOffsetChange(parseInt(e.target.value) || 0)}
                InputProps={{
                  endAdornment: '원'
                }}
                sx={{ width: 200 }}
                helperText="양수: 더 비싸게, 음수: 더 싸게"
              />
            )}
          </Stack>

          <Box sx={{ mt: 1, p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              예시: 매수 1호가가 75,000원일 때
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {value.sell.type === 'best_bid' && `→ 75,000원 ${value.sell.offset > 0 ? `+ ${value.sell.offset}원` : value.sell.offset < 0 ? `- ${Math.abs(value.sell.offset)}원` : ''}에 매도 주문`}
              {value.sell.type === 'best_ask' && `→ 75,050원 ${value.sell.offset > 0 ? `+ ${value.sell.offset}원` : value.sell.offset < 0 ? `- ${Math.abs(value.sell.offset)}원` : ''}에 매도 주문 (대기)`}
              {value.sell.type === 'mid_price' && `→ 75,025원 ${value.sell.offset > 0 ? `+ ${value.sell.offset}원` : value.sell.offset < 0 ? `- ${Math.abs(value.sell.offset)}원` : ''}에 매도 주문`}
              {value.sell.type === 'market' && `→ 시장가로 즉시 매도`}
            </Typography>
          </Box>
        </Box>
      </Stack>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'warning.50', borderRadius: 1 }}>
        <Typography variant="caption" fontWeight="bold" display="block" gutterBottom>
          💡 추천 설정
        </Typography>
        <Typography variant="caption" display="block">
          • <strong>빠른 체결 우선</strong>: 매수=매도1호가+10원, 매도=매수1호가-10원
        </Typography>
        <Typography variant="caption" display="block">
          • <strong>유리한 가격 우선</strong>: 매수=매수1호가, 매도=매도1호가 (체결 안 될 수 있음)
        </Typography>
        <Typography variant="caption" display="block">
          • <strong>확실한 체결</strong>: 시장가 주문 (슬리피지 있음)
        </Typography>
      </Box>
    </Paper>
  )
}
