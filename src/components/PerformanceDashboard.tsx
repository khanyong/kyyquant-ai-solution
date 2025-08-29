import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Stack,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableRow,
  LinearProgress,
  Rating
} from '@mui/material'
import {
  TrendingUp,
  AccountBalance,
  Speed,
  Assessment,
  EmojiEvents,
  Warning
} from '@mui/icons-material'
import { Doughnut, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
)

const PerformanceDashboard: React.FC = () => {
  // Portfolio 분포 차트 데이터
  const portfolioData = {
    labels: ['삼성전자', 'SK하이닉스', 'NAVER', '카카오', '현금'],
    datasets: [{
      data: [35, 25, 20, 15, 5],
      backgroundColor: [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)'
      ]
    }]
  }

  // 월별 수익률 차트 데이터
  const monthlyReturnsData = {
    labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
    datasets: [{
      label: '월 수익률 (%)',
      data: [2.5, -1.2, 3.8, 2.1, -0.5, 4.2],
      backgroundColor: (context: any) => {
        const value = context.raw
        return value >= 0 ? 'rgba(75, 192, 192, 0.8)' : 'rgba(255, 99, 132, 0.8)'
      }
    }]
  }

  // 전략별 성과
  const strategyPerformance = [
    { name: 'RSI + MACD', return: 15.2, trades: 45, winRate: 68, rating: 4.5 },
    { name: '모멘텀 전략', return: 12.8, trades: 38, winRate: 62, rating: 4 },
    { name: '평균회귀', return: 8.5, trades: 52, winRate: 58, rating: 3.5 },
    { name: '볼린저밴드', return: -2.3, trades: 28, winRate: 43, rating: 2 }
  ]

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>
        <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
        성과 분석 대시보드
      </Typography>

      {/* 주요 지표 카드 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent>
              <Stack spacing={1}>
                <AccountBalance sx={{ color: 'white' }} />
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                  총 자산
                </Typography>
                <Typography variant="h4" sx={{ color: 'white' }}>
                  12.5M
                </Typography>
                <Chip 
                  label="+23.5%" 
                  size="small" 
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <CardContent>
              <Stack spacing={1}>
                <TrendingUp sx={{ color: 'white' }} />
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                  일일 수익
                </Typography>
                <Typography variant="h4" sx={{ color: 'white' }}>
                  +152K
                </Typography>
                <Chip 
                  label="+1.2%" 
                  size="small" 
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <CardContent>
              <Stack spacing={1}>
                <Speed sx={{ color: 'white' }} />
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                  승률
                </Typography>
                <Typography variant="h4" sx={{ color: 'white' }}>
                  62.5%
                </Typography>
                <Chip 
                  label="156/250" 
                  size="small" 
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
            <CardContent>
              <Stack spacing={1}>
                <EmojiEvents sx={{ color: 'white' }} />
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                  Sharpe Ratio
                </Typography>
                <Typography variant="h4" sx={{ color: 'white' }}>
                  1.85
                </Typography>
                <Chip 
                  label="우수" 
                  size="small" 
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 차트 섹션 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>포트폴리오 구성</Typography>
            <Doughnut 
              data={portfolioData}
              options={{
                plugins: {
                  legend: { position: 'bottom' }
                }
              }}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>월별 수익률</Typography>
            <Bar 
              data={monthlyReturnsData}
              options={{
                responsive: true,
                plugins: {
                  legend: { display: false }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: { display: true, text: '수익률 (%)' }
                  }
                }
              }}
            />
          </Paper>
        </Grid>
      </Grid>

      {/* 전략별 성과 */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>전략별 성과</Typography>
            <Table size="small">
              <TableBody>
                {strategyPerformance.map((strategy) => (
                  <TableRow key={strategy.name}>
                    <TableCell>
                      <Stack>
                        <Typography variant="body2">{strategy.name}</Typography>
                        <Rating value={strategy.rating} readOnly size="small" />
                      </Stack>
                    </TableCell>
                    <TableCell align="right">
                      <Typography 
                        variant="body2" 
                        color={strategy.return >= 0 ? 'success.main' : 'error.main'}
                      >
                        {strategy.return >= 0 ? '+' : ''}{strategy.return}%
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Stack alignItems="flex-end">
                        <Typography variant="caption" color="text.secondary">
                          승률 {strategy.winRate}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={strategy.winRate} 
                          sx={{ width: 60, height: 4, borderRadius: 2 }}
                          color={strategy.winRate > 60 ? 'success' : 'warning'}
                        />
                      </Stack>
                    </TableCell>
                    <TableCell align="right">
                      <Chip label={`${strategy.trades}회`} size="small" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>리스크 지표</Typography>
            <Stack spacing={2}>
              <Box>
                <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
                  <Typography variant="body2">최대 낙폭 (MDD)</Typography>
                  <Typography variant="body2" color="error.main">-8.3%</Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={8.3} 
                  color="error"
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
              
              <Box>
                <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
                  <Typography variant="body2">일일 VaR (95%)</Typography>
                  <Typography variant="body2" color="warning.main">2.1%</Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={21} 
                  color="warning"
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Box>
                <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
                  <Typography variant="body2">포지션 집중도</Typography>
                  <Typography variant="body2" color="info.main">35%</Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={35} 
                  color="info"
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Box>
                <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
                  <Typography variant="body2">레버리지 사용률</Typography>
                  <Typography variant="body2" color="success.main">0%</Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={0} 
                  color="success"
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default PerformanceDashboard