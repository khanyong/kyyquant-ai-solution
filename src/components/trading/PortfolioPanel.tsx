import React, { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Stack,
  Button,
  CircularProgress,
  Card,
  CardContent,
  Grid,
  Divider,
  Alert
} from '@mui/material'
import {
  Refresh,
  AccountBalanceWallet,
  TrendingUp,
  TrendingDown,
  ShowChart
} from '@mui/icons-material'
import { supabase } from '../../lib/supabase'
import { useAppSelector } from '../../hooks/redux'

interface AccountBalance {
  total_cash: number
  available_cash: number
  order_cash: number
  total_asset: number
  stock_value: number
  profit_loss: number
  profit_loss_rate: number
  updated_at: string
}

interface PortfolioHolding {
  stock_code: string
  stock_name: string
  quantity: number
  available_quantity: number
  avg_price: number
  purchase_amount: number
  current_price: number
  evaluated_amount: number
  profit_loss: number
  profit_loss_rate: number
  updated_at: string
}

const PortfolioPanel: React.FC = () => {
  const { user } = useAppSelector(state => state.auth)
  const [balance, setBalance] = useState<AccountBalance | null>(null)
  const [holdings, setHoldings] = useState<PortfolioHolding[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchPortfolio = async () => {
    if (!user) return

    setLoading(true)
    setError(null)
    try {
      // 계좌 잔고 조회
      const { data: balanceData, error: balanceError } = await supabase
        .from('kw_account_balance')
        .select('*')
        .eq('user_id', user.id)
        .single()

      if (balanceError && balanceError.code !== 'PGRST116') {
        throw balanceError
      }

      setBalance(balanceData)

      // 보유 주식 조회
      const { data: portfolioData, error: portfolioError } = await supabase
        .from('kw_portfolio')
        .select('*')
        .eq('user_id', user.id)
        .order('evaluated_amount', { ascending: false })

      if (portfolioError) throw portfolioError

      setHoldings(portfolioData || [])
    } catch (error: any) {
      console.error('Failed to fetch portfolio:', error)
      setError(error.message || '포트폴리오를 불러오는데 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const syncKiwoomBalance = async () => {
    if (!user) return

    setLoading(true)
    setError(null)
    try {
      // Supabase Edge Function 호출
      const { data, error } = await supabase.functions.invoke('sync-kiwoom-balance', {
        method: 'POST',
      })

      console.log('Edge Function raw response:', { data, error })

      if (error) {
        console.error('Edge Function error:', error)
        // data가 있으면 상세 에러 메시지 표시
        if (data) {
          console.error('Edge Function error details:', data)
          throw new Error(data.error || error.message)
        }
        throw error
      }

      console.log('Edge Function response:', data)

      if (!data || !data.success) {
        console.error('Edge Function failed:', data)
        throw new Error(data?.error || '동기화 실패')
      }

      // 성공 후 데이터 다시 조회
      await fetchPortfolio()

      console.log('✅ 키움 계좌 동기화 완료:', data)
    } catch (error: any) {
      console.error('Failed to sync Kiwoom balance:', error)
      setError(error.message || '키움 계좌 동기화 실패')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      fetchPortfolio()
    }
  }, [user])

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ko-KR').format(num)
  }

  const formatPercent = (num: number) => {
    const formatted = num.toFixed(2)
    return num >= 0 ? `+${formatted}%` : `${formatted}%`
  }

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h6">계좌 잔고 및 보유 자산</Typography>
        <Stack direction="row" spacing={1}>
          <Button
            startIcon={loading ? <CircularProgress size={16} /> : <Refresh />}
            onClick={fetchPortfolio}
            disabled={loading}
            variant="outlined"
            size="small"
          >
            새로고침
          </Button>
          <Button
            startIcon={loading ? <CircularProgress size={16} /> : <AccountBalanceWallet />}
            onClick={syncKiwoomBalance}
            disabled={loading}
            variant="contained"
            size="small"
            color="primary"
          >
            키움 계좌 동기화
          </Button>
        </Stack>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {!user ? (
        <Alert severity="info">로그인이 필요합니다</Alert>
      ) : loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : !balance && holdings.length === 0 ? (
        <Card>
          <CardContent>
            <Alert severity="info">
              계좌 데이터가 없습니다. 샘플 데이터를 생성하려면 Supabase에서 다음 SQL을 실행하세요:
              <br /><br />
              <code>SELECT insert_sample_account_data(auth.uid(), '계좌번호');</code>
            </Alert>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* 계좌 잔고 Summary */}
          {balance && (
            <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
              <CardContent>
                <Stack direction="row" spacing={1} alignItems="center" mb={2}>
                  <AccountBalanceWallet sx={{ color: 'white' }} />
                  <Typography variant="h6" color="white">
                    계좌 잔고
                  </Typography>
                </Stack>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        총 자산
                      </Typography>
                      <Typography variant="h5" fontWeight="bold" color="primary">
                        ₩{formatNumber(balance.total_asset)}
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        보유 현금
                      </Typography>
                      <Typography variant="h5" fontWeight="bold">
                        ₩{formatNumber(balance.total_cash)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        주문가능: ₩{formatNumber(balance.order_cash)}
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        주식 평가액
                      </Typography>
                      <Typography variant="h5" fontWeight="bold" color="info.main">
                        ₩{formatNumber(balance.stock_value)}
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        평가손익
                      </Typography>
                      <Stack direction="row" spacing={0.5} justifyContent="center" alignItems="center">
                        {balance.profit_loss >= 0 ? (
                          <TrendingUp color="success" />
                        ) : (
                          <TrendingDown color="error" />
                        )}
                        <Typography
                          variant="h5"
                          fontWeight="bold"
                          color={balance.profit_loss >= 0 ? 'success.main' : 'error.main'}
                        >
                          {balance.profit_loss >= 0 ? '+' : ''}
                          ₩{formatNumber(balance.profit_loss)}
                        </Typography>
                      </Stack>
                      <Chip
                        label={`${balance.profit_loss >= 0 ? '+' : ''}${balance.profit_loss_rate.toFixed(2)}%`}
                        color={balance.profit_loss >= 0 ? 'success' : 'error'}
                        size="small"
                        sx={{ mt: 1 }}
                      />
                    </Paper>
                  </Grid>
                </Grid>

                <Typography variant="caption" color="rgba(255,255,255,0.7)" sx={{ mt: 2, display: 'block' }}>
                  마지막 업데이트: {new Date(balance.updated_at).toLocaleString('ko-KR')}
                </Typography>
              </CardContent>
            </Card>
          )}

          {/* 보유 종목 테이블 */}
          <Card>
            <CardContent>
              <Stack direction="row" spacing={1} alignItems="center" mb={2}>
                <ShowChart color="primary" />
                <Typography variant="h6">보유 종목 ({holdings.length})</Typography>
              </Stack>

              {holdings.length === 0 ? (
                <Alert severity="info">보유 종목이 없습니다</Alert>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>종목명</TableCell>
                        <TableCell align="right">보유수량</TableCell>
                        <TableCell align="right">평균단가</TableCell>
                        <TableCell align="right">현재가</TableCell>
                        <TableCell align="right">평가금액</TableCell>
                        <TableCell align="right">평가손익</TableCell>
                        <TableCell align="right">수익률</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {holdings.map((holding) => (
                        <TableRow key={holding.stock_code} hover>
                          <TableCell>
                            <Stack>
                              <Typography variant="body2" fontWeight="medium">
                                {holding.stock_name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {holding.stock_code}
                              </Typography>
                            </Stack>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2">
                              {formatNumber(holding.quantity)}주
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              (매도가능: {formatNumber(holding.available_quantity)}주)
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            ₩{formatNumber(holding.avg_price)}
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight="medium">
                              ₩{formatNumber(holding.current_price)}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight="medium">
                              ₩{formatNumber(holding.evaluated_amount)}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Stack direction="row" spacing={0.5} justifyContent="flex-end" alignItems="center">
                              {holding.profit_loss >= 0 ? (
                                <TrendingUp fontSize="small" color="success" />
                              ) : (
                                <TrendingDown fontSize="small" color="error" />
                              )}
                              <Typography
                                variant="body2"
                                fontWeight="bold"
                                color={holding.profit_loss >= 0 ? 'success.main' : 'error.main'}
                              >
                                {holding.profit_loss >= 0 ? '+' : ''}
                                ₩{formatNumber(holding.profit_loss)}
                              </Typography>
                            </Stack>
                          </TableCell>
                          <TableCell align="right">
                            <Chip
                              label={`${holding.profit_loss_rate >= 0 ? '+' : ''}${holding.profit_loss_rate.toFixed(2)}%`}
                              color={holding.profit_loss_rate >= 0 ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  )
}

export default PortfolioPanel