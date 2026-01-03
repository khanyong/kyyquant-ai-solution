import React, { useEffect, useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Stack,
  Tooltip,
  Skeleton
} from '@mui/material'
import { TrendingUp, TrendingDown, AccessTime, Public, AttachMoney, ShowChart, Warning } from '@mui/icons-material'
import { useAppDispatch } from '../../hooks/redux'
import { updateMarketIndices } from '../../store/marketSlice'
import axios from 'axios'
import { format } from 'date-fns'

interface MarketIndexData {
  index_code: string
  current_value: number
  change_value: number
  change_rate: number
  updated_at: string
}

// 4x4 Layout Definition
const LAYOUT_GROUPS = [
  {
    title: "The Core (Major Indices)",
    icon: <ShowChart sx={{ color: 'primary.main' }} />,
    items: [
      { code: 'S&P500', label: 'S&P 500', desc: 'Global Benchmark' },
      { code: 'NASDAQ', label: 'NASDAQ', desc: 'Tech/Growth' },
      { code: 'KOSPI', label: 'KOSPI', desc: 'KR Main' },
      { code: 'KOSDAQ', label: 'KOSDAQ', desc: 'KR Growth' }
    ]
  },
  {
    title: "Global Pulse (Context)",
    icon: <Public sx={{ color: 'info.main' }} />,
    items: [
      { code: 'Nikkei225', label: 'Nikkei 225', desc: 'Japan' },
      { code: 'EuroStoxx50', label: 'Euro Stoxx 50', desc: 'Europe' },
      { code: 'DowJones', label: 'Dow Jones', desc: 'US Industrial' },
      { code: 'Russell2000', label: 'Russell 2000', desc: 'US Small Cap' }
    ]
  },
  {
    title: "Money Flow (Commodities & FX)",
    icon: <AttachMoney sx={{ color: 'warning.main' }} />,
    items: [
      { code: 'WTI_Oil', label: 'WTI Crude', desc: 'Energy', isCommodity: true },
      { code: 'Gold', label: 'Gold', desc: 'Safe Haven', isCommodity: true },
      { code: 'USD/KRW', label: 'USD/KRW', desc: 'Exchange Rate', isCurrency: true },
      { code: 'Bitcoin', label: 'Bitcoin', desc: 'Crypto', isCurrency: true }
    ]
  },
  {
    title: "Risk & Rates (Signals)",
    icon: <Warning sx={{ color: 'error.main' }} />,
    items: [
      { code: 'US10Y', label: 'US 10Y Yield', desc: 'Long Rate', isRate: true },
      { code: 'US2Y_ETF', label: 'US Short Term (SHY)', desc: 'Short Term Proxy', isRate: false },
      { code: 'VIX', label: 'VIX (Fear)', desc: 'Volatility', isRate: true },
      { code: 'TLT', label: 'TLT (20Y+ Bond)', desc: 'Long Bond ETF', isRate: false }
    ]
  }
]

const MarketOverview: React.FC = () => {
  const dispatch = useAppDispatch()
  const [indices, setIndices] = useState<MarketIndexData[]>([])
  const [loading, setLoading] = useState(true)

  const loadMarketIndices = async () => {
    try {
      // API 호출 (VITE_API_URL 사용, 없으면 로컬호스트 기본값)
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001'
      const response = await axios.get(`${apiUrl}/api/market/global-indices`)

      const data = response.data
      if (Array.isArray(data)) {
        setIndices(data)
        // Redux store update (mapping standard format)
        dispatch(updateMarketIndices(data.map((item: any) => ({
          name: item.index_code,
          value: item.current_value,
          change: item.change_value,
          changeRate: item.change_rate
        }))))
      }
    } catch (error) {
      console.error('시장 지수 로드 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMarketIndices()
    const interval = setInterval(loadMarketIndices, 60000) // 1분 갱신
    return () => clearInterval(interval)
  }, [])

  const formatUpdateTime = (isoString?: string) => {
    if (!isoString) return '-'
    try {
      return format(new Date(isoString), 'MM/dd HH:mm')
    } catch (e) {
      return '-'
    }
  }

  const renderCard = (config: { code: string, label: string, desc: string, isCommodity?: boolean, isCurrency?: boolean, isRate?: boolean }) => {
    const data = indices.find(i => i.index_code === config.code)

    // Default placeholder if no data yet (or loading)
    if (!data) {
      return (
        <Paper sx={{ p: 2, height: '100%', bgcolor: 'background.paper', opacity: 0.7 }}>
          <Stack direction="row" justifyContent="space-between" mb={1}>
            <Typography variant="subtitle2" color="text.secondary">{config.label}</Typography>
            <Skeleton variant="rectangular" width={40} height={20} />
          </Stack>
          <Skeleton variant="text" width="80%" height={40} />
          <Typography variant="caption" color="text.disabled">{config.desc}</Typography>
        </Paper>
      )
    }

    const isPositive = data.change_value >= 0
    const color = isPositive ? 'error.main' : 'primary.main' // Korea style: Red is Up, Blue is Down

    // Formatting nuances
    let prefix = ''
    if (!config.isRate && !config.isCommodity && !config.isCurrency && !['KOSPI', 'KOSDAQ', 'Nikkei225', 'EuroStoxx50'].includes(config.code)) prefix = '$'
    if (config.code === 'USD/KRW') prefix = '₩'
    if (config.code === 'Bitcoin') prefix = '₩' // Assuming KRW based on fetcher

    let suffix = ''
    if (config.isRate) suffix = '%'

    return (
      <Paper sx={{ p: 2, height: '100%', bgcolor: 'background.paper', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)', boxShadow: 3 } }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" mb={1}>
          <Typography variant="subtitle2" color="text.secondary" fontWeight="bold">
            {config.label}
          </Typography>
          <Tooltip title={config.desc}>
            <Chip label={config.desc} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.65rem' }} />
          </Tooltip>
        </Stack>

        <Stack direction="row" alignItems="baseline" justifyContent="space-between">
          <Typography variant="h5" fontWeight="bold">
            {prefix}{data.current_value.toLocaleString(undefined, { maximumFractionDigits: 2 })}{suffix}
          </Typography>
        </Stack>

        <Stack direction="row" spacing={1} alignItems="center" mt={0.5} justifyContent="space-between">
          <Stack direction="row" spacing={0.5} alignItems="center">
            {isPositive ? <TrendingUp color="error" fontSize="small" /> : <TrendingDown color="primary" fontSize="small" />}
            <Typography variant="body2" color={color} fontWeight="medium">
              {isPositive ? '+' : ''}{data.change_value.toFixed(2)}
            </Typography>
            <Chip
              label={`${isPositive ? '+' : ''}${data.change_rate.toFixed(2)}%`}
              color={isPositive ? 'error' : 'primary'}
              size="small"
              sx={{ height: 20, '& .MuiChip-label': { px: 0.8, py: 0 }, fontSize: '0.75rem', fontWeight: 'bold' }}
            />
          </Stack>

          <Tooltip title={`Updated: ${formatUpdateTime(data.updated_at)}`}>
            <AccessTime sx={{ fontSize: 14, color: 'text.disabled', cursor: 'help' }} />
          </Tooltip>
        </Stack>
      </Paper>
    )
  }

  return (
    <Box>
      {LAYOUT_GROUPS.map((group, groupIdx) => (
        <Box key={groupIdx} sx={{ mb: 3 }}>
          <Stack direction="row" alignItems="center" spacing={1} mb={1.5} sx={{ px: 0.5 }}>
            {group.icon}
            <Typography variant="h6" fontWeight="bold" color="text.primary">
              {group.title}
            </Typography>
          </Stack>
          <Grid container spacing={2}>
            {group.items.map((item, itemIdx) => (
              <Grid item xs={12} sm={6} md={3} key={itemIdx}>
                {renderCard(item)}
              </Grid>
            ))}
          </Grid>
        </Box>
      ))}
    </Box>
  )
}

export default MarketOverview