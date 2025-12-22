import React, { useEffect, useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Stack,
  CircularProgress,
  Tooltip
} from '@mui/material'
import { TrendingUp, TrendingDown, AccessTime } from '@mui/icons-material'
import { useAppDispatch } from '../../hooks/redux'
import { updateMarketIndices } from '../../store/marketSlice'
import { supabase } from '../../lib/supabase'
import axios from 'axios'
import { format } from 'date-fns'

interface MarketIndexData {
  value: number
  change: number
  changeRate: number
  updatedAt: string
}

interface MarketData {
  kospi: MarketIndexData
  kosdaq: MarketIndexData
  usd: MarketIndexData
  sp500: MarketIndexData
  nasdaq: MarketIndexData
  ief: MarketIndexData
  tlt: MarketIndexData
  lqd: MarketIndexData
  loading: boolean
}

const initialIndexData: MarketIndexData = {
  value: 0,
  change: 0,
  changeRate: 0,
  updatedAt: ''
}

const MarketOverview: React.FC = () => {
  const dispatch = useAppDispatch()
  const [marketData, setMarketData] = useState<MarketData>({
    kospi: { ...initialIndexData },
    kosdaq: { ...initialIndexData },
    usd: { ...initialIndexData },
    sp500: { ...initialIndexData },
    nasdaq: { ...initialIndexData },
    ief: { ...initialIndexData },
    tlt: { ...initialIndexData },
    lqd: { ...initialIndexData },
    loading: true
  })

  // 시장 지수 데이터 로드 (Backend API 사용)
  const loadMarketIndices = async () => {
    try {
      setMarketData(prev => ({ ...prev, loading: true }))

      // API 호출 (VITE_API_URL 사용, 없으면 로컬호스트 기본값)
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001'
      const response = await axios.get(`${apiUrl}/api/market/global-indices`)

      const data = response.data

      if (!data || !Array.isArray(data)) throw new Error("Invalid API response")

      const findData = (code: string) => data.find((d: any) => d.index_code === code)

      const mapData = (code: string): MarketIndexData => {
        const item = findData(code)
        return {
          value: item?.current_value || 0,
          change: item?.change_value || 0,
          changeRate: item?.change_rate || 0,
          updatedAt: item?.updated_at || ''
        }
      }

      const newData = {
        kospi: mapData('KOSPI'),
        kosdaq: mapData('KOSDAQ'),
        usd: mapData('USD_KRW'),
        sp500: mapData('SPX'),
        nasdaq: mapData('COMP'),
        ief: mapData('IEF'),
        tlt: mapData('TLT'),
        lqd: mapData('LQD'),
        loading: false
      }

      setMarketData(newData)
    } catch (error: any) {
      console.error('시장 지수 로드 실패:', error)
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

  const formatUpdateTime = (isoString: string) => {
    if (!isoString) return '-'
    try {
      return format(new Date(isoString), 'MM/dd HH:mm')
    } catch (e) {
      return '-'
    }
  }

  const renderMarketCard = (title: string, data: MarketIndexData, isBond = false, isUsd = false) => (
    <Grid item xs={12} md={3}>
      <Paper sx={{ p: 2, bgcolor: isBond ? 'rgba(0, 0, 0, 0.02)' : 'background.paper', height: '100%' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box sx={{ width: '100%' }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="subtitle2" color="text.secondary">
                {title}
              </Typography>
              {isBond ? (
                <Chip label={title.includes('IEF') ? "금리/중기채" : title.includes('TLT') ? "장기채/금리민감" : "회사채/신용"} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.7rem' }} />
              ) : (
                <Box />
              )}
            </Stack>

            <Stack direction="row" justifyContent="space-between" alignItems="flex-end">
              <Box>
                <Typography variant="h5" fontWeight="bold">
                  {isBond || title.includes('USD') || title.includes('S&P') || title.includes('NASDAQ') ? (title.includes('S&P') || title.includes('NASDAQ') ? '' : '$') : ''}{data.value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </Typography>

                <Stack direction="row" spacing={1} alignItems="center" mt={0.5}>
                  {data.change >= 0 ? (
                    <TrendingUp color="error" fontSize="small" />
                  ) : (
                    <TrendingDown color="primary" fontSize="small" />
                  )}
                  <Typography
                    variant="body2"
                    color={data.change >= 0 ? 'error.main' : 'primary.main'}
                    fontWeight="medium"
                  >
                    {data.change >= 0 ? '+' : ''}{data.change.toFixed(2)}
                  </Typography>
                  {!isUsd && (
                    <Chip
                      label={`${data.changeRate >= 0 ? '+' : ''}${data.changeRate.toFixed(2)}%`}
                      color={data.changeRate >= 0 ? 'error' : 'primary'}
                      size="small"
                      sx={{ height: 20, '& .MuiChip-label': { px: 1, py: 0 } }}
                    />
                  )}
                </Stack>
              </Box>

              <Tooltip title={`데이터 기준: ${data.updatedAt ? new Date(data.updatedAt).toLocaleString() : '미확인'}`}>
                <Typography variant="caption" color="text.disabled" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <AccessTime sx={{ fontSize: 12 }} />
                  {formatUpdateTime(data.updatedAt)}
                </Typography>
              </Tooltip>
            </Stack>
          </Box>
        </Stack>
      </Paper>
    </Grid>
  )

  return (
    <Grid container spacing={2}>
      {renderMarketCard('KOSPI', marketData.kospi)}
      {renderMarketCard('KOSDAQ', marketData.kosdaq)}
      {renderMarketCard('S&P 500', marketData.sp500)}
      {renderMarketCard('NASDAQ', marketData.nasdaq)}
      {renderMarketCard('USD/KRW', marketData.usd, false, true)}
      {renderMarketCard('US Treasury 10Y (IEF)', marketData.ief, true)}
      {renderMarketCard('US Treasury 20Y+ (TLT)', marketData.tlt, true)}
      {renderMarketCard('Corp Bond Inv.Gr (LQD)', marketData.lqd, true)}
    </Grid>
  )
}

export default MarketOverview