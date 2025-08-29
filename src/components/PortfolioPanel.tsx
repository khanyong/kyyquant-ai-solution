import React, { useEffect } from 'react'
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Stack,
  Button,
  CircularProgress
} from '@mui/material'
import { Refresh } from '@mui/icons-material'
import { useAppSelector, useAppDispatch } from '../hooks/redux'
import { setPortfolio, setLoading } from '../store/portfolioSlice'
import { getBalance } from '../services/api'

const PortfolioPanel: React.FC = () => {
  const dispatch = useAppDispatch()
  const { selectedAccount } = useAppSelector(state => state.auth)
  const { holdings, totalValue, totalProfitLoss, loading } = useAppSelector(state => state.portfolio)

  const fetchPortfolio = async () => {
    if (!selectedAccount) return

    dispatch(setLoading(true))
    try {
      const data = await getBalance(selectedAccount)
      dispatch(setPortfolio(data))
    } catch (error) {
      console.error('Failed to fetch portfolio:', error)
    }
  }

  useEffect(() => {
    if (selectedAccount) {
      fetchPortfolio()
    }
  }, [selectedAccount])

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ko-KR').format(num)
  }

  const formatPercent = (num: number) => {
    const formatted = num.toFixed(2)
    return num >= 0 ? `+${formatted}%` : `${formatted}%`
  }

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h6">
          보유 종목
        </Typography>
        <Button
          startIcon={loading ? <CircularProgress size={16} /> : <Refresh />}
          onClick={fetchPortfolio}
          disabled={loading || !selectedAccount}
        >
          새로고침
        </Button>
      </Stack>

      {!selectedAccount ? (
        <Typography color="text.secondary">
          계좌를 선택해주세요
        </Typography>
      ) : loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : holdings.length === 0 ? (
        <Typography color="text.secondary" align="center" sx={{ p: 4 }}>
          보유 종목이 없습니다
        </Typography>
      ) : (
        <>
          <Stack direction="row" spacing={3} sx={{ mb: 3 }}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                총 평가금액
              </Typography>
              <Typography variant="h5">
                ₩{formatNumber(totalValue)}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                총 평가손익
              </Typography>
              <Typography 
                variant="h5" 
                color={totalProfitLoss >= 0 ? 'success.main' : 'error.main'}
              >
                {totalProfitLoss >= 0 ? '+' : ''}{formatNumber(totalProfitLoss)}
              </Typography>
            </Box>
          </Stack>

          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>종목명</TableCell>
                  <TableCell align="right">보유수량</TableCell>
                  <TableCell align="right">평균단가</TableCell>
                  <TableCell align="right">현재가</TableCell>
                  <TableCell align="right">평가금액</TableCell>
                  <TableCell align="right">평가손익</TableCell>
                  <TableCell align="right">수익률</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {holdings.map((holding) => (
                  <TableRow key={holding.stockCode}>
                    <TableCell>
                      <Stack>
                        <Typography variant="body2">
                          {holding.stockName}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {holding.stockCode}
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell align="right">
                      {formatNumber(holding.quantity)}
                    </TableCell>
                    <TableCell align="right">
                      ₩{formatNumber(holding.avgPrice)}
                    </TableCell>
                    <TableCell align="right">
                      ₩{formatNumber(holding.currentPrice)}
                    </TableCell>
                    <TableCell align="right">
                      ₩{formatNumber(holding.currentPrice * holding.quantity)}
                    </TableCell>
                    <TableCell align="right">
                      <Typography 
                        color={holding.profitLoss >= 0 ? 'success.main' : 'error.main'}
                      >
                        {holding.profitLoss >= 0 ? '+' : ''}{formatNumber(holding.profitLoss)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={formatPercent(holding.profitLossRate)}
                        color={holding.profitLossRate >= 0 ? 'success' : 'error'}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}
    </Box>
  )
}

export default PortfolioPanel