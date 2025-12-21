import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Stack,
  Chip,
  Card,
  CardContent,
  useTheme
} from '@mui/material'
import {
  TrendingUp,
  AccountBalance,
  PieChart as PieChartIcon,
  BarChart as BarChartIcon
} from '@mui/icons-material'
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LabelList
} from 'recharts'

interface PortfolioStats {
  totalCapital: number
  totalAllocated: number
  totalInvested: number
  totalValue: number
  totalProfit: number
  totalProfitRate: number
  activeStrategiesCount: number
  totalPositions: number
  realCash: number
}

interface PortfolioOverviewProps {
  stats: PortfolioStats
  activeStrategies: any[]
  positions: any[]
  lastUpdated: Date | null
}

const COLORS = ['#C5A065', '#212121', '#424242', '#616161', '#9E9E9E', '#E0E0E0'] // Editorial Gold + Grey Palette

export default function PortfolioOverview({ stats, activeStrategies, positions, lastUpdated }: PortfolioOverviewProps) {
  const theme = useTheme()
  const safeStats = stats || {}

  const formatCurrency = (value: number | undefined) => {
    return new Intl.NumberFormat('ko-KR').format(value || 0)
  }

  const formatPercent = (value: number | undefined) => {
    const safeValue = value || 0
    return `${safeValue >= 0 ? '+' : ''}${safeValue.toFixed(2)}%`
  }

  const getProfitColor = (value: number | undefined) => {
    const safeValue = value || 0
    if (safeValue > 0) return 'error.main' // Red for profit
    if (safeValue < 0) return 'primary.main' // Blue for loss
    return 'text.secondary'
  }

  // 데이터 준비: 자산 배분 (현금 vs 투자금)
  const assetAllocationData = [
    { name: '보유 주식', value: safeStats.totalValue || 0 },
    { name: '가용 현금', value: safeStats.realCash || 0 }
  ]

  // 데이터 준비: 전략별 자금 할당
  const strategyAllocationData = activeStrategies?.map((s) => ({
    name: s.strategy_name,
    value: parseFloat(s.allocated_capital) || 0
  })) || []

  // 데이터 준비: 보유 비중 Top 5
  const topHoldingsData = [...(positions || [])]
    .sort((a, b) => (b.value || 0) - (a.value || 0))
    .slice(0, 5)
    .map((p) => {
      const value = p.value || 0
      const percent = safeStats.totalValue > 0 ? (value / safeStats.totalValue) * 100 : 0
      return {
        name: p.stock_name,
        value: value,
        percent: percent,
        label: `₩${formatCurrency(value)} (${percent.toFixed(1)}%)`
      }
    })

  // Custom label for Pie Charts (Inner %)
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }: any) => {
    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    if (percent < 0.05) return null // Hide if too small

    return (
      <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize={12} fontWeight="bold">
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      {/* Header */}
      <Stack direction="row" alignItems="center" spacing={2} mb={3}>
        <AccountBalance fontSize="large" sx={{ color: '#121212' }} />
        <Typography variant="h5" fontWeight="bold" fontFamily="serif">
          내 포트폴리오 현황
          <Chip label="Source: 내부DB" color="info" size="small" variant="outlined" sx={{ ml: 2, verticalAlign: 'middle', fontSize: '0.8rem' }} />
          {lastUpdated && (
            <Typography variant="caption" color="text.secondary" sx={{ ml: 1, verticalAlign: 'middle', fontSize: '0.8rem' }}>
              ({lastUpdated.toLocaleString('ko-KR')})
            </Typography>
          )}
        </Typography>
      </Stack>

      <Grid container spacing={3}>
        {/* ... (Summary Cards Section - No Changes) ... */}
        {/* 총 투자금 */}
        <Grid item xs={12} md={3}>
          <Box p={2} border="1px solid #000000" bgcolor="background.paper" borderRadius={0}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              총 할당 자금
            </Typography>
            <Typography variant="h5" fontWeight="bold" fontFamily="serif">
              {formatCurrency(safeStats.totalAllocated)}원
            </Typography>
            <Typography variant="caption" color="text.secondary">
              활성 전략 {safeStats.activeStrategiesCount || 0}개
            </Typography>
          </Box>
        </Grid>

        {/* 투자 중 */}
        <Grid item xs={12} md={3}>
          <Box p={2} border="1px solid #000000" bgcolor="background.paper" borderRadius={0}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              투자 중
            </Typography>
            <Typography variant="h5" fontWeight="bold" fontFamily="serif">
              {formatCurrency(safeStats.totalInvested)}원
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {safeStats.totalPositions || 0}개 종목 보유
            </Typography>
          </Box>
        </Grid>

        {/* 현재 평가액 */}
        <Grid item xs={12} md={3}>
          <Box p={2} border="1px solid #000000" bgcolor="background.paper" borderRadius={0}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              현재 평가액
            </Typography>
            <Typography variant="h5" fontWeight="bold" fontFamily="serif">
              {formatCurrency(safeStats.totalValue)}원
            </Typography>
            <Typography variant="caption" color="text.secondary">
              대기 자금: {formatCurrency((safeStats.totalAllocated || 0) - (safeStats.totalInvested || 0))}원
            </Typography>
          </Box>
        </Grid>

        {/* 수익률 */}
        <Grid item xs={12} md={3}>
          <Box p={2} border="1px solid #000000" bgcolor="background.paper" borderRadius={0}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              총 수익
            </Typography>
            <Stack direction="row" alignItems="baseline" spacing={1}>
              <Typography
                variant="h5"
                fontWeight="bold"
                fontFamily="serif"
                color={getProfitColor(safeStats.totalProfit)}
              >
                {safeStats.totalProfit > 0 ? '+' : ''}{formatCurrency(safeStats.totalProfit)}원
              </Typography>
              <Chip
                icon={safeStats.totalProfitRate > 0 ? <TrendingUp /> : undefined}
                label={formatPercent(safeStats.totalProfitRate)}
                size="small"
                variant="outlined"
                color={safeStats.totalProfitRate > 0 ? 'error' : safeStats.totalProfitRate < 0 ? 'primary' : 'default'}
                sx={{ fontWeight: 'bold', borderRadius: 0 }}
              />
            </Stack>
          </Box>
        </Grid>


        {/* === 차트 섹션 === */}
        {/* 1. 자산 배분 (Pie) */}
        <Grid item xs={12} md={4}>
          <Card elevation={0} variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold" display="flex" alignItems="center" fontFamily="serif">
                <PieChartIcon sx={{ mr: 1, color: 'text.primary' }} /> 자산 배분
              </Typography>
              <Box height={250}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={assetAllocationData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      fill="#212121"
                      paddingAngle={5}
                      dataKey="value"
                      label={renderCustomizedLabel}
                      labelLine={false}
                    >
                      {assetAllocationData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => `₩${formatCurrency(value)}`} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 2. 전략별 자금 할당 (Pie) */}
        <Grid item xs={12} md={4}>
          <Card elevation={0} variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold" display="flex" alignItems="center" fontFamily="serif">
                <PieChartIcon sx={{ mr: 1, color: 'text.primary' }} /> 전략별 자금 할당
              </Typography>
              {strategyAllocationData.length > 0 ? (
                <Box height={250}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={strategyAllocationData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        fill="#212121"
                        paddingAngle={5}
                        dataKey="value"
                        label={renderCustomizedLabel}
                        labelLine={false}
                      >
                        {strategyAllocationData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value: number) => `₩${formatCurrency(value)}`} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box height={250} display="flex" alignItems="center" justifyContent="center">
                  <Typography color="text.secondary">할당된 전략이 없습니다.</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* 3. 보유 비중 Top 5 (Bar) */}
        <Grid item xs={12} md={4}>
          <Card elevation={0} variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold" display="flex" alignItems="center" fontFamily="serif">
                <BarChartIcon sx={{ mr: 1, color: 'text.primary' }} /> 보유 비중 Top 5
              </Typography>
              {topHoldingsData.length > 0 ? (
                <Box height={250}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      layout="vertical"
                      data={topHoldingsData}
                      margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                      <XAxis type="number" hide />
                      <YAxis type="category" dataKey="name" width={60} fontSize={12} />
                      <Tooltip formatter={(value: number) => `₩${formatCurrency(value)}`} contentStyle={{ backgroundColor: '#fff', border: '1px solid #000' }} />
                      <Bar dataKey="value" fill="#212121" radius={[0, 0, 0, 0]}>
                        <LabelList dataKey="label" position="insideLeft" fill="white" fontSize={11} fontWeight="bold" />
                        {topHoldingsData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box height={250} display="flex" alignItems="center" justifyContent="center">
                  <Typography color="text.secondary">보유 중인 종목이 없습니다.</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Paper>
  )
}
