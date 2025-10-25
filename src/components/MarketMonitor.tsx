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
  stock_name: string // kw_price_current 테이블에서 직접 가져온 종목명
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
  const [showAllStocks, setShowAllStocks] = useState(false)

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
        async (payload) => {
          console.log('📊 New market data:', payload.new)

          // payload에서 직접 데이터 사용 (stock_name 포함)
          const newData = payload.new as MarketData
          const updatedData = {
            ...newData,
            stock_name: newData.stock_name || newData.stock_code
          }

          setMarketData((prev) => {
            // 같은 종목코드가 있으면 업데이트, 없으면 추가
            const exists = prev.findIndex(
              (item) => item.stock_code === updatedData.stock_code
            )
            if (exists >= 0) {
              const updated = [...prev]
              updated[exists] = updatedData
              return updated
            }
            return [updatedData, ...prev]
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
      console.log('🔄 MarketMonitor: Fetching market data...')

      // kw_price_current 데이터 조회 (stock_name 포함)
      const { data: priceData, error: priceError } = await supabase
        .from('kw_price_current')
        .select('*')
        .order('updated_at', { ascending: false })

      if (priceError) {
        // 테이블이 없는 경우 조용히 무시
        if (priceError.code === 'PGRST205') {
          console.warn('kw_price_current 테이블이 없습니다. 시장 모니터링 기능이 비활성화됩니다.')
          setMarketData([])
          return
        }
        throw priceError
      }

      if (!priceData || priceData.length === 0) {
        setMarketData([])
        setLastUpdate(new Date())
        return
      }

      // stock_name이 없는 경우 stock_code로 대체
      const formattedData = priceData.map((item: any) => ({
        ...item,
        stock_name: item.stock_name || item.stock_code
      }))

      console.log(`✅ MarketMonitor: Loaded ${formattedData.length} stocks`)
      console.log('📊 Sample data:', formattedData.slice(0, 3))
      console.log('🔍 Stock names:', formattedData.slice(0, 10).map(d => ({ code: d.stock_code, name: d.stock_name })))

      setMarketData(formattedData)
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

  // 표시할 종목 데이터 (최근 10개 또는 전체)
  const displayedStocks = showAllStocks ? marketData : marketData.slice(0, 10)

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
                  <Paper sx={{ p: 2, bgcolor: 'rgba(244, 67, 54, 0.1)', border: '1px solid rgba(244, 67, 54, 0.3)' }}>
                    <Typography variant="caption" color="text.secondary">
                      상승 종목
                    </Typography>
                    <Typography variant="h4" color="error.main" fontWeight="bold">
                      {marketData.filter((d) => d.change_rate > 0).length}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(33, 150, 243, 0.1)', border: '1px solid rgba(33, 150, 243, 0.3)' }}>
                    <Typography variant="caption" color="text.secondary">
                      하락 종목
                    </Typography>
                    <Typography variant="h4" color="primary.main" fontWeight="bold">
                      {marketData.filter((d) => d.change_rate < 0).length}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(158, 158, 158, 0.1)', border: '1px solid rgba(158, 158, 158, 0.3)' }}>
                    <Typography variant="caption" color="text.secondary">
                      보합 종목
                    </Typography>
                    <Typography variant="h4" color="text.primary" fontWeight="bold">
                      {marketData.filter((d) => d.change_rate === 0).length}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* 종목 테이블 - 최근 업데이트 종목 */}
              <Box>
                <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="subtitle1" fontWeight="medium">
                    최근 업데이트 종목 ({displayedStocks.length}개)
                  </Typography>
                  {marketData.length > 10 && (
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => setShowAllStocks(!showAllStocks)}
                    >
                      {showAllStocks ? '접기 ▲' : `전체 보기 (${marketData.length}개) ▼`}
                    </Button>
                  )}
                </Stack>

                <TableContainer
                  component={Paper}
                  sx={{
                    maxHeight: showAllStocks ? 600 : 400,
                    overflow: 'auto'
                  }}
                >
                  <Table stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell>종목코드</TableCell>
                        <TableCell>종목명</TableCell>
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
                      {displayedStocks.map((item) => (
                        <TableRow key={item.stock_code} hover>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium" fontFamily="monospace">
                              {item.stock_code}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {item.stock_name || '-'}
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
              </Box>
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  )
}
