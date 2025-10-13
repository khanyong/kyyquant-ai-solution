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
  IconButton,
  Button,
  LinearProgress,
  Alert,
  Stack,
  Grid
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  Refresh,
  ShowChart,
  Timeline
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'

interface MarketData {
  id: string
  stock_code: string
  stock_name: string
  current_price: number
  change_amount: number
  change_rate: number
  volume: number
  high: number
  low: number
  monitored_at: string
  source: string
}

export default function MarketMonitor() {
  const [marketData, setMarketData] = useState<MarketData[]>([])
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    fetchMarketData()

    // Supabase Realtime 구독 - 새 데이터 실시간 반영
    const channel = supabase
      .channel('market_monitoring')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'market_monitoring'
        },
        (payload) => {
          console.log('📊 New market data:', payload.new)
          setMarketData((prev) => {
            // 같은 종목코드가 있으면 업데이트, 없으면 추가
            const exists = prev.findIndex(
              (item) => item.stock_code === (payload.new as MarketData).stock_code
            )
            if (exists >= 0) {
              const updated = [...prev]
              updated[exists] = payload.new as MarketData
              return updated
            }
            return [payload.new as MarketData, ...prev]
          })
          setLastUpdate(new Date())
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  const fetchMarketData = async () => {
    try {
      setLoading(true)

      // 최근 1시간 이내 데이터만 조회 (종목별 최신 데이터)
      const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString()

      const { data, error } = await supabase
        .from('market_monitoring')
        .select('*')
        .gte('monitored_at', oneHourAgo)
        .order('monitored_at', { ascending: false })

      if (error) throw error

      // 종목별 최신 데이터만 추출
      const latestByStock = new Map<string, MarketData>()
      data?.forEach((item) => {
        if (!latestByStock.has(item.stock_code)) {
          latestByStock.set(item.stock_code, item)
        }
      })

      setMarketData(Array.from(latestByStock.values()))
      setLastUpdate(new Date())
    } catch (error) {
      console.error('시장 데이터 로드 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ko-KR').format(price)
  }

  const formatVolume = (volume: number) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`
    }
    return volume.toString()
  }

  const getPriceColor = (changeRate: number) => {
    if (changeRate > 0) return 'error.main'
    if (changeRate < 0) return 'primary.main'
    return 'text.secondary'
  }

  const getPriceIcon = (changeRate: number) => {
    if (changeRate > 0) return <TrendingUp fontSize="small" />
    if (changeRate < 0) return <TrendingDown fontSize="small" />
    return null
  }

  return (
    <Box>
      <Card>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5" component="h2">
              📊 실시간 시장 모니터링
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center">
              {lastUpdate && (
                <Typography variant="caption" color="text.secondary">
                  마지막 업데이트: {lastUpdate.toLocaleTimeString()}
                </Typography>
              )}
              <Button
                size="small"
                startIcon={<Refresh />}
                onClick={fetchMarketData}
                disabled={loading}
              >
                새로고침
              </Button>
            </Stack>
          </Stack>

          {loading && <LinearProgress sx={{ mb: 2 }} />}

          {marketData.length === 0 && !loading && (
            <Alert severity="info">
              모니터링 중인 종목이 없습니다. n8n 워크플로우가 실행 중인지 확인하세요.
            </Alert>
          )}

          {marketData.length > 0 && (
            <>
              {/* 요약 카드 */}
              <Grid container spacing={2} mb={3}>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'error.lighter' }}>
                    <Typography variant="caption" color="text.secondary">
                      상승 종목
                    </Typography>
                    <Typography variant="h4" color="error.main">
                      {marketData.filter((d) => d.change_rate > 0).length}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'primary.lighter' }}>
                    <Typography variant="caption" color="text.secondary">
                      하락 종목
                    </Typography>
                    <Typography variant="h4" color="primary.main">
                      {marketData.filter((d) => d.change_rate < 0).length}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                    <Typography variant="caption" color="text.secondary">
                      보합 종목
                    </Typography>
                    <Typography variant="h4">
                      {marketData.filter((d) => d.change_rate === 0).length}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* 종목 테이블 */}
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>종목코드</TableCell>
                      <TableCell>종목명</TableCell>
                      <TableCell align="right">현재가</TableCell>
                      <TableCell align="right">등락률</TableCell>
                      <TableCell align="right">거래량</TableCell>
                      <TableCell align="right">고가</TableCell>
                      <TableCell align="right">저가</TableCell>
                      <TableCell align="center">업데이트</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {marketData.map((item) => (
                      <TableRow key={item.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {item.stock_code}
                          </Typography>
                        </TableCell>
                        <TableCell>{item.stock_name}</TableCell>
                        <TableCell align="right">
                          <Typography
                            variant="body2"
                            fontWeight="bold"
                            color={getPriceColor(item.change_rate)}
                          >
                            {formatPrice(item.current_price)}원
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                            {getPriceIcon(item.change_rate)}
                            <Typography
                              variant="body2"
                              fontWeight="medium"
                              color={getPriceColor(item.change_rate)}
                            >
                              {item.change_rate > 0 ? '+' : ''}
                              {item.change_rate.toFixed(2)}%
                            </Typography>
                          </Stack>
                        </TableCell>
                        <TableCell align="right">
                          {formatVolume(item.volume)}
                        </TableCell>
                        <TableCell align="right" sx={{ color: 'error.main' }}>
                          {formatPrice(item.high)}
                        </TableCell>
                        <TableCell align="right" sx={{ color: 'primary.main' }}>
                          {formatPrice(item.low)}
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={new Date(item.monitored_at).toLocaleTimeString()}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </>
          )}
        </CardContent>
      </Card>

      {/* n8n 상태 안내 */}
      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">
          💡 <strong>n8n 워크플로우 상태:</strong>
          {' '}1분마다 자동으로 시장 데이터를 수집하여 실시간 반영됩니다.
          {' '}워크플로우가 실행 중이지 않으면 데이터가 업데이트되지 않습니다.
        </Typography>
      </Alert>
    </Box>
  )
}
