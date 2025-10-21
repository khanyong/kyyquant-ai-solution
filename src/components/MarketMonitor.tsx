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
  Grid,
  Divider
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  Refresh,
  ShowChart,
  Timeline
} from '@mui/icons-material'
import { supabase } from '../lib/supabase'
import N8nWorkflowMonitor from './N8nWorkflowMonitor'

interface MarketData {
  stock_code: string
  current_price: number
  change_price: number
  change_rate: number
  volume: number
  trading_value: number
  high_52w: number
  low_52w: number
  market_cap: number
  shares_outstanding: number
  foreign_ratio: number
  updated_at: string
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
      .channel('kw_price_current')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'kw_price_current'
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

      // 모든 데이터 조회 (kw_price_current는 종목별 최신 가격만 저장)
      const { data, error } = await supabase
        .from('kw_price_current')
        .select('*')
        .order('updated_at', { ascending: false })

      if (error) {
        // 테이블이 없는 경우 조용히 무시 (kw_price_current 테이블은 선택적)
        if (error.code === 'PGRST205') {
          console.warn('kw_price_current 테이블이 없습니다. 시장 모니터링 기능이 비활성화됩니다.')
          setMarketData([])
          return
        }
        throw error
      }

      setMarketData(data || [])
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
      {/* n8n 워크플로우 모니터링 */}
      <Box mb={3}>
        <N8nWorkflowMonitor />
      </Box>

      <Divider sx={{ my: 3 }} />

      {/* 시장 데이터 모니터링 */}
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
                      <TableCell align="right">현재가</TableCell>
                      <TableCell align="right">등락가</TableCell>
                      <TableCell align="right">등락률</TableCell>
                      <TableCell align="right">거래량</TableCell>
                      <TableCell align="right">52주 고가</TableCell>
                      <TableCell align="right">52주 저가</TableCell>
                      <TableCell align="center">업데이트</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {marketData.map((item) => (
                      <TableRow key={item.stock_code} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {item.stock_code}
                          </Typography>
                        </TableCell>
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
                          <Typography
                            variant="body2"
                            color={getPriceColor(item.change_rate)}
                          >
                            {item.change_price > 0 ? '+' : ''}
                            {formatPrice(Math.abs(item.change_price))}원
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
                          {formatPrice(item.high_52w)}
                        </TableCell>
                        <TableCell align="right" sx={{ color: 'primary.main' }}>
                          {formatPrice(item.low_52w)}
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={new Date(item.updated_at).toLocaleTimeString()}
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
    </Box>
  )
}
