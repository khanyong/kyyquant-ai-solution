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
  loading: boolean
}

const MarketOverview: React.FC = () => {
  const dispatch = useAppDispatch()
  const [marketData, setMarketData] = useState<MarketData>({
    kospi: { value: 0, change: 0, changeRate: 0 },
    kosdaq: { value: 0, change: 0, changeRate: 0 },
    usd: { value: 0, change: 0 },
    loading: true
  })

  // 시장 지수 데이터 로드
  const loadMarketIndices = async () => {
    try {
      setMarketData(prev => ({ ...prev, loading: true }))

      const { data, error } = await supabase
        .from('market_index')
        .select('index_code, current_value, change_value, change_rate')
        .in('index_code', ['KOSPI', 'KOSDAQ', 'USD_KRW'])
        .order('timestamp', { ascending: false })
        .limit(3)

      if (error) throw error

      const kospiData = data?.find(d => d.index_code === 'KOSPI')
      const kosdaqData = data?.find(d => d.index_code === 'KOSDAQ')
      const usdData = data?.find(d => d.index_code === 'USD_KRW')

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
        loading: false
      })
    } catch (error) {
      console.error('시장 지수 로드 실패:', error)
      setMarketData(prev => ({ ...prev, loading: false }))
    }
  }

  useEffect(() => {
    loadMarketIndices()

    // 1분마다 자동 갱신
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
    <Grid container spacing={2}>
      <Grid item xs={12} md={4}>
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

      <Grid item xs={12} md={4}>
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

      <Grid item xs={12} md={4}>
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
    </Grid>
  )
}

export default MarketOverview