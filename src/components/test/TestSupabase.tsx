import React, { useEffect, useState } from 'react'
import { Box, Paper, Typography, Button, Alert, Stack, Chip, Divider } from '@mui/material'
import { CheckCircle, Error, Refresh } from '@mui/icons-material'
import { supabase } from '../../lib/supabase'
import TestEmailVerification from './TestEmailVerification'

const TestSupabase: React.FC = () => {
  const [connectionStatus, setConnectionStatus] = useState<'testing' | 'connected' | 'error'>('testing')
  const [stocks, setStocks] = useState<any[]>([])
  const [marketIndex, setMarketIndex] = useState<any[]>([])
  const [errorMessage, setErrorMessage] = useState<string>('')

  const testConnection = async () => {
    setConnectionStatus('testing')
    setErrorMessage('')
    
    try {
      // 1. stocks 테이블 테스트
      const { data: stocksData, error: stocksError } = await supabase
        .from('stocks')
        .select('*')
        .limit(5)
      
      if (stocksError) throw stocksError
      setStocks(stocksData || [])
      
      // 2. market_index 테이블 테스트
      const { data: indexData, error: indexError } = await supabase
        .from('market_index')
        .select('*')
      
      if (indexError) throw indexError
      setMarketIndex(indexData || [])
      
      setConnectionStatus('connected')
    } catch (error: any) {
      console.error('Supabase connection error:', error)
      setConnectionStatus('error')
      setErrorMessage(error.message || 'Unknown error')
    }
  }

  useEffect(() => {
    testConnection()
  }, [])

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5">
            Supabase 연결 테스트
          </Typography>
          <Button 
            variant="outlined" 
            startIcon={<Refresh />}
            onClick={testConnection}
          >
            다시 테스트
          </Button>
        </Stack>

        {/* 연결 상태 */}
        <Alert 
          severity={connectionStatus === 'connected' ? 'success' : connectionStatus === 'error' ? 'error' : 'info'}
          icon={connectionStatus === 'connected' ? <CheckCircle /> : connectionStatus === 'error' ? <Error /> : undefined}
          sx={{ mb: 3 }}
        >
          {connectionStatus === 'testing' && '연결 테스트 중...'}
          {connectionStatus === 'connected' && '✅ Supabase 연결 성공!'}
          {connectionStatus === 'error' && `❌ 연결 실패: ${errorMessage}`}
        </Alert>

        {/* 테이블 정보 */}
        {connectionStatus === 'connected' && (
          <Stack spacing={3}>
            {/* 시장 지수 */}
            <Box>
              <Typography variant="h6" gutterBottom>
                시장 지수
              </Typography>
              <Stack direction="row" spacing={2}>
                {marketIndex.map((index) => (
                  <Paper key={index.id} sx={{ p: 2, minWidth: 150 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      {index.index_name}
                    </Typography>
                    <Typography variant="h6">
                      {index.current_value.toLocaleString()}
                    </Typography>
                    <Chip 
                      label={`${index.change_rate > 0 ? '+' : ''}${index.change_rate}%`}
                      color={index.change_rate > 0 ? 'success' : 'error'}
                      size="small"
                    />
                  </Paper>
                ))}
              </Stack>
            </Box>

            {/* 종목 리스트 */}
            <Box>
              <Typography variant="h6" gutterBottom>
                등록된 종목 ({stocks.length}개)
              </Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                {stocks.map((stock) => (
                  <Chip 
                    key={stock.code}
                    label={`${stock.name} (${stock.code})`}
                    variant="outlined"
                  />
                ))}
              </Stack>
            </Box>

            {/* 데이터베이스 정보 */}
            <Box>
              <Typography variant="h6" gutterBottom>
                데이터베이스 정보
              </Typography>
              <Stack spacing={1}>
                <Typography variant="body2">
                  • Project URL: {import.meta.env.VITE_SUPABASE_URL}
                </Typography>
                <Typography variant="body2">
                  • 테이블: stocks, price_data, orders, portfolio, strategies 등
                </Typography>
                <Typography variant="body2">
                  • RLS 활성화: profiles, orders, portfolio, strategies
                </Typography>
              </Stack>
            </Box>
          </Stack>
        )}
      </Paper>
      
      <Divider sx={{ my: 3 }} />
      
      {/* Email Verification Test */}
      <TestEmailVerification />
    </Box>
  )
}

export default TestSupabase