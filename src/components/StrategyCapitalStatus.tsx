import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Stack,
  IconButton,
  Tooltip,
  Alert
} from '@mui/material'
import {
  Refresh,
  TrendingUp,
  TrendingDown,
  AccountBalanceWallet,
  ShowChart
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'

interface StrategyCapitalData {
  strategy_id: string
  strategy_name: string
  allocation_mode: string
  total_allocated: number
  capital_in_use: number
  available_capital: number
  utilization_rate: number
  active_positions: number
  total_pnl: number
}

const StrategyCapitalStatus: React.FC = () => {
  const [capitalData, setCapitalData] = useState<StrategyCapitalData[]>([])
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  useEffect(() => {
    fetchCapitalStatus()

    // 10초마다 자동 새로고침
    const interval = setInterval(fetchCapitalStatus, 10000)

    return () => clearInterval(interval)
  }, [])

  const fetchCapitalStatus = async () => {
    try {
      setLoading(true)

      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return

      const { data, error } = await supabase
        .rpc('get_all_strategies_capital_summary', {
          p_user_id: user.id
        })

      if (error) throw error

      setCapitalData(data || [])
      setLastUpdate(new Date())
    } catch (error: any) {
      console.error('자금 현황 조회 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return amount.toLocaleString('ko-KR') + '원'
  }

  const getUtilizationColor = (rate: number) => {
    if (rate >= 90) return 'error'
    if (rate >= 70) return 'warning'
    if (rate >= 50) return 'info'
    return 'success'
  }

  const totalAllocated = capitalData.reduce((sum, item) => sum + item.total_allocated, 0)
  const totalInUse = capitalData.reduce((sum, item) => sum + item.capital_in_use, 0)
  const totalAvailable = capitalData.reduce((sum, item) => sum + item.available_capital, 0)
  const totalPnL = capitalData.reduce((sum, item) => sum + item.total_pnl, 0)

  if (loading && capitalData.length === 0) {
    return (
      <Card>
        <CardContent>
          <LinearProgress />
        </CardContent>
      </Card>
    )
  }

  if (capitalData.length === 0) {
    return (
      <Alert severity="info">
        활성화된 전략이 없습니다. 전략을 생성하고 자금을 할당하세요.
      </Alert>
    )
  }

  return (
    <Box>
      {/* 헤더 */}
      <Card sx={{ mb: 2, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="h5" color="white" gutterBottom>
                💰 전략별 자금 현황
              </Typography>
              <Typography variant="body2" color="rgba(255, 255, 255, 0.8)">
                실시간 자금 사용량 및 가용 자금 모니터링
              </Typography>
            </Box>
            <Stack direction="row" spacing={1} alignItems="center">
              {lastUpdate && (
                <Chip
                  label={lastUpdate.toLocaleTimeString()}
                  size="small"
                  sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', color: 'white' }}
                />
              )}
              <IconButton onClick={fetchCapitalStatus} sx={{ color: 'white' }}>
                <Refresh />
              </IconButton>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      {/* 전체 요약 */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            📊 전체 요약
          </Typography>
          <Stack direction="row" spacing={3} sx={{ mt: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary">
                총 할당 자금
              </Typography>
              <Typography variant="h6" color="primary.main">
                {formatCurrency(totalAllocated)}
              </Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary">
                사용 중
              </Typography>
              <Typography variant="h6" color="warning.main">
                {formatCurrency(totalInUse)}
              </Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary">
                가용 자금
              </Typography>
              <Typography variant="h6" color="success.main">
                {formatCurrency(totalAvailable)}
              </Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary">
                총 손익
              </Typography>
              <Typography
                variant="h6"
                color={totalPnL >= 0 ? 'success.main' : 'error.main'}
                sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
              >
                {totalPnL >= 0 ? <TrendingUp /> : <TrendingDown />}
                {totalPnL >= 0 ? '+' : ''}
                {formatCurrency(totalPnL)}
              </Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      {/* 전략별 상세 */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>전략명</TableCell>
              <TableCell>할당 방식</TableCell>
              <TableCell align="right">총 할당</TableCell>
              <TableCell align="right">사용 중</TableCell>
              <TableCell align="right">가용 자금</TableCell>
              <TableCell align="center">사용률</TableCell>
              <TableCell align="center">활성 포지션</TableCell>
              <TableCell align="right">손익</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {capitalData.map((item) => (
              <TableRow key={item.strategy_id} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold">
                    {item.strategy_name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={item.allocation_mode}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2" fontWeight="medium">
                    {formatCurrency(item.total_allocated)}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Stack alignItems="flex-end">
                    <Typography variant="body2" color="warning.main" fontWeight="bold">
                      {formatCurrency(item.capital_in_use)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {item.total_allocated > 0
                        ? `${((item.capital_in_use / item.total_allocated) * 100).toFixed(1)}%`
                        : '0%'}
                    </Typography>
                  </Stack>
                </TableCell>
                <TableCell align="right">
                  <Stack alignItems="flex-end">
                    <Typography
                      variant="body2"
                      color={item.available_capital > 0 ? 'success.main' : 'error.main'}
                      fontWeight="bold"
                    >
                      {formatCurrency(item.available_capital)}
                    </Typography>
                    {item.available_capital < item.total_allocated * 0.1 && item.total_allocated > 0 && (
                      <Chip
                        label="잔여 부족"
                        size="small"
                        color="error"
                        sx={{ height: 18, fontSize: '0.65rem', mt: 0.5 }}
                      />
                    )}
                  </Stack>
                </TableCell>
                <TableCell align="center">
                  <Box sx={{ width: '100%', maxWidth: 120, mx: 'auto' }}>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min(item.utilization_rate, 100)}
                      color={getUtilizationColor(item.utilization_rate)}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                      {item.utilization_rate.toFixed(1)}%
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell align="center">
                  <Chip
                    icon={<AccountBalanceWallet />}
                    label={`${item.active_positions}개`}
                    size="small"
                    color={item.active_positions > 0 ? 'primary' : 'default'}
                  />
                </TableCell>
                <TableCell align="right">
                  <Stack direction="row" spacing={0.5} alignItems="center" justifyContent="flex-end">
                    {item.total_pnl !== 0 && (
                      item.total_pnl > 0 ? <TrendingUp fontSize="small" color="success" /> : <TrendingDown fontSize="small" color="error" />
                    )}
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color={item.total_pnl >= 0 ? 'success.main' : 'error.main'}
                    >
                      {item.total_pnl >= 0 ? '+' : ''}
                      {formatCurrency(item.total_pnl)}
                    </Typography>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 경고 메시지 */}
      {capitalData.some(item => item.available_capital < item.total_allocated * 0.1 && item.total_allocated > 0) && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          ⚠️ 일부 전략의 가용 자금이 10% 미만입니다. 추가 매수가 제한될 수 있습니다.
        </Alert>
      )}
    </Box>
  )
}

export default StrategyCapitalStatus
