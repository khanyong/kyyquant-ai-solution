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
import axios from 'axios'

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

  /* Debug State */
  const [debugError, setDebugError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<string>("");

  // 시장 지수 데이터 로드 (Backend API 사용)
  const loadMarketIndices = async () => {
    try {
      setMarketData(prev => ({ ...prev, loading: true }))
      setDebugError(null)

      // API 호출 (VITE_API_URL 사용, 없으면 로컬호스트 기본값)
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001'
      const response = await axios.get(`${apiUrl}/api/market/global-indices`)

      const data = response.data
      setDebugInfo(`Items: ${Array.isArray(data) ? data.length : 'Not Array'} | First: ${JSON.stringify(data[0] || {})}`)

      if (!data || !Array.isArray(data)) throw new Error("Invalid API response")

      const kospiData = data.find((d: any) => d.index_code === 'KOSPI')
      const kosdaqData = data.find((d: any) => d.index_code === 'KOSDAQ')
      const usdData = data.find((d: any) => d.index_code === 'USD_KRW')
      const spxData = data.find((d: any) => d.index_code === 'SPX')
      const compData = data.find((d: any) => d.index_code === 'COMP')
      const iefData = data.find((d: any) => d.index_code === 'IEF')
      const tltData = data.find((d: any) => d.index_code === 'TLT')
      const lqdData = data.find((d: any) => d.index_code === 'LQD')

      setMarketData({
        kospi: {
          value: kospiData?.current_value || 0,
          change: kospiData?.change_value || 0,
          changeRate: kospiData?.change_rate || 0
        },
        kosdaq: {
          value: kosdaqData?.current_value || 0,
          change: kosdaqData?.change_value || 0,
          changeRate: kosdaqData?.change_rate || 0
        },
        usd: {
          value: usdData?.current_value || 0,
          change: usdData?.change_value || 0
        },
        sp500: {
          value: spxData?.current_value || 0,
          change: spxData?.change_value || 0,
          changeRate: spxData?.change_rate || 0
        },
        nasdaq: {
          value: compData?.current_value || 0,
          change: compData?.change_value || 0,
          changeRate: compData?.change_rate || 0
        },
        ief: {
          value: iefData?.current_value || 0,
          change: iefData?.change_value || 0,
          changeRate: iefData?.change_rate || 0
        },
        tlt: {
          value: tltData?.current_value || 0,
          change: tltData?.change_value || 0,
          changeRate: tltData?.change_rate || 0
        },
        lqd: {
          value: lqdData?.current_value || 0,
          change: lqdData?.change_value || 0,
          changeRate: lqdData?.change_rate || 0
        },
        loading: false
      })
    } catch (error: any) {
      console.error('시장 지수 로드 실패:', error)
      setDebugError(error.message || "Unknown Error")
      setMarketData(prev => ({ ...prev, loading: false }))
    }
  }

  useEffect(() => {
    loadMarketIndices()
    // 1분마다 갱신
    const interval = setInterval(loadMarketIndices, 60000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    // Update Redux store
    dispatch(updateMarketIndices([
      { name: 'KOSPI', value: marketData.kospi.value, change: marketData.kospi.change, changeRate: marketData.kospi.changeRate },
      { name: 'KOSDAQ', value: marketData.kosdaq.value, change: marketData.kosdaq.change, changeRate: marketData.kosdaq.changeRate },
    ]))
  }, [marketData, dispatch])

  return (
    <Box>
      {/* Debug Info Overlay */}
      {(debugError || debugInfo) && (
        <Paper sx={{ p: 1, mb: 2, bgcolor: '#fff3e0', color: '#e65100', fontSize: '0.75rem' }}>
          <b>Debug:</b> {debugError ? `Error: ${debugError}` : debugInfo}
        </Paper>
      )}

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
    </Box>
  )
}

export default MarketOverview