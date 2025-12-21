import React, { useEffect, useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Stack,
  CircularProgress
} from '@mui/material'
import { TrendingUp, TrendingDown } from '@mui/icons-material'
import { useAppDispatch } from '../../hooks/redux'
import { updateMarketIndices } from '../../store/marketSlice'
import { supabase } from '../../lib/supabase'

interface MarketData {
  kospi: { value: number; change: number; changeRate: number }
  kosdaq: { value: number; change: number; changeRate: number }
  usd: { value: number; change: number }
  sp500: { value: number; change: number; changeRate: number }
  nasdaq: { value: number; change: number; changeRate: number }
  ief: { value: number; change: number; changeRate: number }
  tlt: { value: number; change: number; changeRate: number }
  lqd: { value: number; change: number; changeRate: number }
  loading: boolean
}

const MarketOverview: React.FC = () => {
  const dispatch = useAppDispatch()
  const [marketData, setMarketData] = useState<MarketData>({
    kospi: { value: 0, change: 0, changeRate: 0 },
    kosdaq: { value: 0, change: 0, changeRate: 0 },
    usd: { value: 0, change: 0 },
    sp500: { value: 0, change: 0, changeRate: 0 },
    nasdaq: { value: 0, change: 0, changeRate: 0 },
    ief: { value: 0, change: 0, changeRate: 0 },
    tlt: { value: 0, change: 0, changeRate: 0 },
    lqd: { value: 0, change: 0, changeRate: 0 },
    loading: true
  })

  // 시장 지수 데이터 로드
  const loadMarketIndices = async () => {
    try {
      setMarketData(prev => ({ ...prev, loading: true }))

      const { data, error } = await supabase
        .from('market_index')
        .select('index_code, current_value, change_value, change_rate')
        .in('index_code', ['KOSPI', 'KOSDAQ', 'USD_KRW', 'SPX', 'COMP', 'IEF', 'TLT', 'LQD'])
        .order('timestamp', { ascending: false })
        .limit(8)

      if (error) throw error

      const kospiData = data?.find(d => d.index_code === 'KOSPI')
      const kosdaqData = data?.find(d => d.index_code === 'KOSDAQ')
      const usdData = data?.find(d => d.index_code === 'USD_KRW')
      const spxData = data?.find(d => d.index_code === 'SPX')
      const compData = data?.find(d => d.index_code === 'COMP')
      const iefData = data?.find(d => d.index_code === 'IEF')
      const tltData = data?.find(d => d.index_code === 'TLT')
      const lqdData = data?.find(d => d.index_code === 'LQD')

      setMarketData({
        kospi: {
          value: parseFloat(kospiData?.current_value || '0'),
          change: parseFloat(kospiData?.change_value || '0'),
          changeRate: parseFloat(kospiData?.change_rate || '0')
        },
        kosdaq: {
          value: parseFloat(kosdaqData?.current_value || '0'),
          change: parseFloat(kosdaqData?.change_value || '0'),
          changeRate: parseFloat(kosdaqData?.change_rate || '0')
        },
        usd: {
          value: parseFloat(usdData?.current_value || '0'),
          change: parseFloat(usdData?.change_value || '0')
        },
        sp500: {
          value: parseFloat(spxData?.current_value || '0'),
          change: parseFloat(spxData?.change_value || '0'),
          changeRate: parseFloat(spxData?.change_rate || '0')
        },
        nasdaq: {
          value: parseFloat(compData?.current_value || '0'),
          change: parseFloat(compData?.change_value || '0'),
          changeRate: parseFloat(compData?.change_rate || '0')
        },
        ief: {
          value: parseFloat(iefData?.current_value || '0'),
          change: parseFloat(iefData?.change_value || '0'),
          changeRate: parseFloat(iefData?.change_rate || '0')
        },
        tlt: {
          value: parseFloat(tltData?.current_value || '0'),
          change: parseFloat(tltData?.change_value || '0'),
          changeRate: parseFloat(tltData?.change_rate || '0')
        },
        lqd: {
          value: parseFloat(lqdData?.current_value || '0'),
          change: parseFloat(lqdData?.change_value || '0'),
          changeRate: parseFloat(lqdData?.change_rate || '0')
        },
        loading: false
      })
    } catch (error) {
      console.error('시장 지수 로드 실패:', error)
      setMarketData(prev => ({ ...prev, loading: false }))
    }
  }

  useEffect(() => {
    loadMarketIndices()

    // Real-time Subscription (Supabase)
    const channel = supabase
      .channel('market-overview-changes')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'market_index'
        },
        (payload) => {
          const newIndex = payload.new as {
            index_code: string
            current_value: number
            change_value: number
            change_rate: number
          }

          setMarketData((prev) => {
            const updates: Partial<MarketData> = {}

            // Update specific index based on index_code
            switch (newIndex.index_code) {
              case 'KOSPI':
                updates.kospi = { value: newIndex.current_value, change: newIndex.change_value, changeRate: newIndex.change_rate }
                break
              case 'KOSDAQ':
                updates.kosdaq = { value: newIndex.current_value, change: newIndex.change_value, changeRate: newIndex.change_rate }
                break
              case 'USD_KRW':
                updates.usd = { value: newIndex.current_value, change: newIndex.change_value }
                break
              case 'SPX':
                updates.sp500 = { value: newIndex.current_value, change: newIndex.change_value, changeRate: newIndex.change_rate }
                break
              case 'COMP':
                updates.nasdaq = { value: newIndex.current_value, change: newIndex.change_value, changeRate: newIndex.change_rate }
                break
              case 'IEF':
                updates.ief = { value: newIndex.current_value, change: newIndex.change_value, changeRate: newIndex.change_rate }
                break
              case 'TLT':
                updates.tlt = { value: newIndex.current_value, change: newIndex.change_value, changeRate: newIndex.change_rate }
                break
              case 'LQD':
                updates.lqd = { value: newIndex.current_value, change: newIndex.change_value, changeRate: newIndex.change_rate }
                break
            }
            return { ...prev, ...updates }
          })
        }
      )
      .subscribe()

    // Fallback polling (every 5 minutes)
    const interval = setInterval(loadMarketIndices, 300000)

    return () => {
      supabase.removeChannel(channel)
      clearInterval(interval)
    }
  }, [])

  useEffect(() => {
    // Update Redux store
    dispatch(updateMarketIndices([
      { name: 'KOSPI', value: marketData.kospi.value, change: marketData.kospi.change, changeRate: marketData.kospi.changeRate },
      { name: 'KOSDAQ', value: marketData.kosdaq.value, change: marketData.kosdaq.change, changeRate: marketData.kosdaq.changeRate },
    ]))
  }, [marketData, dispatch])

  return (
    <Grid container spacing={2}>
      {/* 1. KOSPI */}
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                KOSPI
              </Typography>
              <Typography variant="h5">
                {marketData.kospi.value.toFixed(2)}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                {marketData.kospi.change >= 0 ? (
                  <TrendingUp color="error" fontSize="small" />
                ) : (
                  <TrendingDown color="primary" fontSize="small" />
                )}
                <Typography
                  variant="body2"
                  color={marketData.kospi.change >= 0 ? 'error.main' : 'primary.main'}
                >
                  {marketData.kospi.change >= 0 ? '+' : ''}{marketData.kospi.change.toFixed(2)}
                </Typography>
                <Chip
                  label={`${marketData.kospi.changeRate >= 0 ? '+' : ''}${marketData.kospi.changeRate.toFixed(2)}%`}
                  color={marketData.kospi.changeRate >= 0 ? 'error' : 'primary'}
                  size="small"
                />
              </Stack>
            </Box>
          </Stack>
        </Paper>
      </Grid>

      {/* 2. KOSDAQ */}
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                KOSDAQ
              </Typography>
              <Typography variant="h5">
                {marketData.kosdaq.value.toFixed(2)}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                {marketData.kosdaq.change >= 0 ? (
                  <TrendingUp color="error" fontSize="small" />
                ) : (
                  <TrendingDown color="primary" fontSize="small" />
                )}
                <Typography
                  variant="body2"
                  color={marketData.kosdaq.change >= 0 ? 'error.main' : 'primary.main'}
                >
                  {marketData.kosdaq.change >= 0 ? '+' : ''}{marketData.kosdaq.change.toFixed(2)}
                </Typography>
                <Chip
                  label={`${marketData.kosdaq.changeRate >= 0 ? '+' : ''}${marketData.kosdaq.changeRate.toFixed(2)}%`}
                  color={marketData.kosdaq.changeRate >= 0 ? 'error' : 'primary'}
                  size="small"
                />
              </Stack>
            </Box>
          </Stack>
        </Paper>
      </Grid>

      {/* 3. S&P 500 */}
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                S&P 500
              </Typography>
              <Typography variant="h5">
                {marketData.sp500.value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                {marketData.sp500.change >= 0 ? (
                  <TrendingUp color="error" fontSize="small" />
                ) : (
                  <TrendingDown color="primary" fontSize="small" />
                )}
                <Typography
                  variant="body2"
                  color={marketData.sp500.change >= 0 ? 'error.main' : 'primary.main'}
                >
                  {marketData.sp500.change >= 0 ? '+' : ''}{marketData.sp500.change.toFixed(2)}
                </Typography>
                <Chip
                  label={`${marketData.sp500.changeRate >= 0 ? '+' : ''}${marketData.sp500.changeRate.toFixed(2)}%`}
                  color={marketData.sp500.changeRate >= 0 ? 'error' : 'primary'}
                  size="small"
                />
              </Stack>
            </Box>
          </Stack>
        </Paper>
      </Grid>

      {/* 4. NASDAQ */}
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                NASDAQ
              </Typography>
              <Typography variant="h5">
                {marketData.nasdaq.value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                {marketData.nasdaq.change >= 0 ? (
                  <TrendingUp color="error" fontSize="small" />
                ) : (
                  <TrendingDown color="primary" fontSize="small" />
                )}
                <Typography
                  variant="body2"
                  color={marketData.nasdaq.change >= 0 ? 'error.main' : 'primary.main'}
                >
                  {marketData.nasdaq.change >= 0 ? '+' : ''}{marketData.nasdaq.change.toFixed(2)}
                </Typography>
                <Chip
                  label={`${marketData.nasdaq.changeRate >= 0 ? '+' : ''}${marketData.nasdaq.changeRate.toFixed(2)}%`}
                  color={marketData.nasdaq.changeRate >= 0 ? 'error' : 'primary'}
                  size="small"
                />
              </Stack>
            </Box>
          </Stack>
        </Paper>
      </Grid>

      {/* 5. USD/KRW */}
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                USD/KRW
              </Typography>
              <Typography variant="h5">
                {marketData.usd.value.toFixed(2)}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                {marketData.usd.change >= 0 ? (
                  <TrendingUp color="error" fontSize="small" />
                ) : (
                  <TrendingDown color="primary" fontSize="small" />
                )}
                <Typography
                  variant="body2"
                  color={marketData.usd.change >= 0 ? 'error.main' : 'primary.main'}
                >
                  {marketData.usd.change >= 0 ? '+' : ''}{marketData.usd.change.toFixed(2)}
                </Typography>
              </Stack>
            </Box>
          </Stack>
        </Paper>
      </Grid>

      {/* 6. IEF */}
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2, bgcolor: 'rgba(0, 0, 0, 0.02)' }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                US Treasury 10Y (IEF)
              </Typography>
              <Typography variant="h6">
                ${marketData.ief.value.toFixed(2)}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography
                  variant="caption"
                  color={marketData.ief.change >= 0 ? 'success.main' : 'error.main'}
                  fontWeight="bold"
                >
                  {marketData.ief.changeRate >= 0 ? '+' : ''}{marketData.ief.changeRate.toFixed(2)}%
                </Typography>
              </Stack>
            </Box>
            <Chip label="금리/중기채" size="small" variant="outlined" />
          </Stack>
        </Paper>
      </Grid>

      {/* 7. TLT */}
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2, bgcolor: 'rgba(0, 0, 0, 0.02)' }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                US Treasury 20Y+ (TLT)
              </Typography>
              <Typography variant="h6">
                ${marketData.tlt.value.toFixed(2)}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography
                  variant="caption"
                  color={marketData.tlt.change >= 0 ? 'success.main' : 'error.main'}
                  fontWeight="bold"
                >
                  {marketData.tlt.changeRate >= 0 ? '+' : ''}{marketData.tlt.changeRate.toFixed(2)}%
                </Typography>
              </Stack>
            </Box>
            <Chip label="장기채/금리민감" size="small" variant="outlined" />
          </Stack>
        </Paper>
      </Grid>

      {/* 8. LQD */}
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2, bgcolor: 'rgba(0, 0, 0, 0.02)' }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                Corp Bond Inv.Gr (LQD)
              </Typography>
              <Typography variant="h6">
                ${marketData.lqd.value.toFixed(2)}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography
                  variant="caption"
                  color={marketData.lqd.change >= 0 ? 'success.main' : 'error.main'}
                  fontWeight="bold"
                >
                  {marketData.lqd.changeRate >= 0 ? '+' : ''}{marketData.lqd.changeRate.toFixed(2)}%
                </Typography>
              </Stack>
            </Box>
            <Chip label="회사채/신용" size="small" variant="outlined" />
          </Stack>
        </Paper>
      </Grid>
    </Grid>
  )
}

export default MarketOverview