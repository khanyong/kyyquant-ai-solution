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

interface MarketData {
  kospi: { value: number; change: number; changeRate: number }
  kosdaq: { value: number; change: number; changeRate: number }
  usd: { value: number; change: number }
  loading: boolean
}

const MarketOverview: React.FC = () => {
  const dispatch = useAppDispatch()
  const [marketData, setMarketData] = useState<MarketData>({
    kospi: { value: 2500, change: 15.2, changeRate: 0.61 },
    kosdaq: { value: 850, change: -5.3, changeRate: -0.62 },
    usd: { value: 1320, change: 5 },
    loading: false
  })

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