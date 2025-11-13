import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Stack,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import { ExpandMore, Refresh } from '@mui/icons-material'
import { supabase } from '../lib/supabase'

interface DebugData {
  [key: string]: any[]
}

export default function DebugPortfolio() {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<DebugData>({})
  const [error, setError] = useState('')

  const loadDebugData = async () => {
    try {
      setLoading(true)
      setError('')
      const results: DebugData = {}

      // 1. 활성 전략 확인
      const { data: strategies, error: stratError } = await supabase
        .from('strategies')
        .select('id, name, auto_execute, auto_trade_enabled, is_active, allocated_capital, allocated_percent, created_at')
        .eq('auto_execute', true)
        .eq('is_active', true)

      if (stratError) throw stratError
      results['활성 전략'] = strategies || []

      // 2. get_active_strategies_with_universe 결과
      const { data: rpcData, error: rpcError } = await supabase
        .rpc('get_active_strategies_with_universe')

      if (rpcError) throw rpcError
      results['RPC 결과'] = rpcData || []

      // 3. 포지션 확인
      const { data: positions, error: posError } = await supabase
        .from('positions')
        .select('*')
        .eq('status', 'open')

      if (posError) throw posError
      results['현재 포지션'] = positions || []

      // 4. 대기 주문 확인
      const { data: orders, error: ordersError } = await supabase
        .from('orders')
        .select('*')
        .eq('status', 'PENDING')

      if (ordersError) throw ordersError
      results['대기 주문'] = orders || []

      // 5. 최근 시그널 (24시간)
      const { data: signals, error: signalsError } = await supabase
        .from('trading_signals')
        .select('*')
        .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())

      if (signalsError) throw signalsError
      results['최근 시그널 (24h)'] = signals || []

      // 6. 현재가 데이터
      const { data: prices, error: pricesError } = await supabase
        .from('kw_price_current')
        .select('stock_code, stock_name, current_price, change_rate, updated_at')
        .order('updated_at', { ascending: false })
        .limit(10)

      if (pricesError) throw pricesError
      results['현재가 데이터 (최신 10개)'] = prices || []

      // 7. 전략-유니버스 연결
      const { data: universes, error: universeError } = await supabase
        .from('strategy_universes')
        .select('strategy_id, investment_filter_id, is_active')
        .eq('is_active', true)

      if (universeError) throw universeError
      results['전략-유니버스 연결'] = universes || []

      setData(results)
    } catch (error: any) {
      console.error('디버그 데이터 로드 실패:', error)
      setError(error.message || '알 수 없는 오류')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDebugData()
  }, [])

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          🔍 포트폴리오 데이터 디버깅
        </Typography>
        <Button
          startIcon={<Refresh />}
          onClick={loadDebugData}
          variant="contained"
          disabled={loading}
        >
          새로고침
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Stack spacing={2}>
          {Object.entries(data).map(([key, value]) => (
            <Accordion key={key} defaultExpanded={['활성 전략', 'RPC 결과'].includes(key)}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6" fontWeight="bold">
                  {key} ({value.length}개)
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {value.length === 0 ? (
                  <Alert severity="info">데이터가 없습니다.</Alert>
                ) : (
                  <Paper sx={{ p: 2, bgcolor: 'grey.50', maxHeight: 400, overflow: 'auto' }}>
                    <pre style={{ margin: 0, fontSize: '12px' }}>
                      {JSON.stringify(value, null, 2)}
                    </pre>
                  </Paper>
                )}
              </AccordionDetails>
            </Accordion>
          ))}

          {/* 요약 통계 */}
          <Paper sx={{ p: 3, bgcolor: 'primary.50' }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              📊 요약 통계
            </Typography>
            <Stack spacing={1}>
              <Typography>
                ✅ 활성 전략: <strong>{data['활성 전략']?.length || 0}</strong>개
              </Typography>
              <Typography>
                📍 현재 포지션: <strong>{data['현재 포지션']?.length || 0}</strong>개
              </Typography>
              <Typography>
                ⏳ 대기 주문: <strong>{data['대기 주문']?.length || 0}</strong>개
              </Typography>
              <Typography>
                📡 최근 시그널: <strong>{data['최근 시그널 (24h)']?.length || 0}</strong>개
              </Typography>
              <Typography>
                💰 현재가 데이터: <strong>{data['현재가 데이터 (최신 10개)']?.length || 0}</strong>개
              </Typography>
            </Stack>

            {data['활성 전략'] && data['활성 전략'].length > 0 && (
              <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                  전략별 할당금액:
                </Typography>
                {data['활성 전략'].map((strategy: any) => (
                  <Typography key={strategy.id} variant="body2">
                    • {strategy.name}:
                    {strategy.allocated_capital ?
                      ` ${strategy.allocated_capital.toLocaleString()}원 (${strategy.allocated_percent}%)` :
                      ' ❌ 할당 안 됨 (0원)'}
                  </Typography>
                ))}
              </Box>
            )}
          </Paper>
        </Stack>
      )}
    </Box>
  )
}
