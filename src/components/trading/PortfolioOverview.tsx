import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Stack,
  Chip
} from '@mui/material'
import {
  TrendingUp,
  AccountBalance,
  ShowChart
} from '@mui/icons-material'

interface PortfolioStats {
  totalCapital: number
  totalAllocated: number
  totalInvested: number
  totalValue: number
  totalProfit: number
  totalProfitRate: number
  activeStrategiesCount: number
  totalPositions: number
}

interface PortfolioOverviewProps {
  stats: PortfolioStats
}

export default function PortfolioOverview({ stats }: PortfolioOverviewProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ko-KR').format(value)
  }

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  const getProfitColor = (value: number) => {
    if (value > 0) return 'error.main'
    if (value < 0) return 'primary.main'
    return 'text.secondary'
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={3}>
        <AccountBalance fontSize="large" color="primary" />
        <Typography variant="h5" fontWeight="bold">
          📊 내 포트폴리오 현황
        </Typography>
      </Stack>

      <Grid container spacing={3}>
        {/* 총 투자금 */}
        <Grid item xs={12} md={3}>
          <Box>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              총 할당 자금
            </Typography>
            <Typography variant="h5" fontWeight="bold">
              {formatCurrency(stats.totalAllocated)}원
            </Typography>
            <Typography variant="caption" color="text.secondary">
              활성 전략 {stats.activeStrategiesCount}개
            </Typography>
          </Box>
        </Grid>

        {/* 투자 중 */}
        <Grid item xs={12} md={3}>
          <Box>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              투자 중
            </Typography>
            <Typography variant="h5" fontWeight="bold">
              {formatCurrency(stats.totalInvested)}원
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {stats.totalPositions}개 종목 보유
            </Typography>
          </Box>
        </Grid>

        {/* 현재 평가액 */}
        <Grid item xs={12} md={3}>
          <Box>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              현재 평가액
            </Typography>
            <Typography variant="h5" fontWeight="bold">
              {formatCurrency(stats.totalValue)}원
            </Typography>
            <Typography variant="caption" color="text.secondary">
              대기 자금: {formatCurrency(stats.totalAllocated - stats.totalInvested)}원
            </Typography>
          </Box>
        </Grid>

        {/* 수익률 */}
        <Grid item xs={12} md={3}>
          <Box>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              총 수익
            </Typography>
            <Stack direction="row" alignItems="baseline" spacing={1}>
              <Typography
                variant="h5"
                fontWeight="bold"
                color={getProfitColor(stats.totalProfit)}
              >
                {formatCurrency(Math.abs(stats.totalProfit))}원
              </Typography>
              <Chip
                icon={stats.totalProfitRate > 0 ? <TrendingUp /> : undefined}
                label={formatPercent(stats.totalProfitRate)}
                size="small"
                color={stats.totalProfitRate > 0 ? 'error' : stats.totalProfitRate < 0 ? 'primary' : 'default'}
                sx={{ fontWeight: 'bold' }}
              />
            </Stack>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  )
}
