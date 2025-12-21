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
  AccountBalance,
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
  total_assets: number
  total_evaluation: number // Changed from total_evaluation_amount to match DB column
  total_profit_loss: number
  total_profit_loss_rate: number
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
      console.log('Fetching portfolio for user:', user.id)

      // 계좌 잔고 조회
      const { data: balanceData, error: balanceError } = await supabase
        .from('account_balance')
        .select('*')
        .eq('user_id', user.id)
        .order('updated_at', { ascending: false }) // Added order/limit to get latest
        .limit(1)
        .single()

      console.log('Balance Data:', balanceData)
      console.log('Balance Error:', balanceError)

      if (balanceError && balanceError.code !== 'PGRST116') {
        throw balanceError
      }

      setBalance(balanceData)

      // 보유 주식 조회
      const { data: portfolioData, error: portfolioError } = await supabase
        .from('portfolio')
        .select('*')
        .eq('user_id', user.id)
        .order('stock_code', { ascending: true }) // Changed from 'evaluated_amount' which doesn't exist

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
    console.log('Sync button clicked')
    if (!user) {
      alert('로그인이 필요합니다 (세션 만료 가능성)')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001'
      alert(`[디버그] 동기화 요청 시작\nAPI: ${apiUrl}\n사용자: ${user.id}`)

      const response = await fetch(`${apiUrl}/api/sync/account`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error(`Sync Request Failed: ${response.status}`)
      }

      const data = await response.json()
      console.log('Sync Response:', data)

      // 성공 메시지 및 디버그 정보 표시
      alert(`동기화 완료!\n종목수: ${data.holdings_updated}\n잔고성공여부: ${data.balance_updated}\n\n[디버그 정보]\n재계산됨: ${data.debug?.recalc_triggered}\n보유종목수(서버): ${data.debug?.holdings_count}\n사용자ID: ${data.debug?.user_id}`)

      // 성공 후 데이터 다시 조회
      await fetchPortfolio()

      console.log('✅ 키움 계좌 동기화 완료:', data)
    } catch (error: any) {
      console.error('Failed to sync Kiwoom balance:', error)
      alert(`동기화 실패: ${error.message}`)
      setError(error.message || '키움 계좌 동기화 실패')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      fetchPortfolio()

      // Realtime 구독: orders 테이블 변경 감지
      const ordersChannel = supabase
        .channel('orders_changes_portfolio')
        .on(
          'postgres_changes',
          {
            event: 'UPDATE',
            schema: 'public',
            table: 'orders'
          },
          (payload) => {
            console.log('📦 Order status changed:', payload)
            // 주문 상태가 EXECUTED나 PARTIAL로 변경되면 포트폴리오 새로고침
            if (payload.new && (payload.new.status === 'EXECUTED' || payload.new.status === 'PARTIAL')) {
              console.log('✅ Order executed, refreshing portfolio...')
              fetchPortfolio()
            }
          }
        )
        .subscribe()

      // Realtime 구독: kw_account_balance 테이블 변경 감지
      const balanceChannel = supabase
        .channel('balance_changes')
        .on(
          'postgres_changes',
          {
            event: '*',
            schema: 'public',
            table: 'kw_account_balance'
          },
          (payload) => {
            console.log('💰 Account balance changed:', payload)
            fetchPortfolio()
          }
        )
        .subscribe()

      // Realtime 구독: kw_portfolio 테이블 변경 감지
      const portfolioChannel = supabase
        .channel('portfolio_changes')
        .on(
          'postgres_changes',
          {
            event: '*',
            schema: 'public',
            table: 'kw_portfolio'
          },
          (payload) => {
            console.log('📊 Portfolio changed:', payload)
            fetchPortfolio()
          }
        )
        .subscribe()

      return () => {
        supabase.removeChannel(ordersChannel)
        supabase.removeChannel(balanceChannel)
        supabase.removeChannel(portfolioChannel)
      }
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
        <Typography variant="h6" fontFamily="serif" fontWeight="bold">
          계좌 잔고 및 보유 자산
          <Chip label="Source: 키움증권" size="small" variant="outlined" sx={{ ml: 1, verticalAlign: 'middle', borderColor: '#EF6C00', color: '#EF6C00' }} />
          {balance && balance.updated_at && (
            <Typography variant="caption" color="text.secondary" sx={{ ml: 1, verticalAlign: 'middle' }}>
              ({new Date(balance.updated_at).toLocaleString('ko-KR')})
            </Typography>
          )}
        </Typography>
        <Stack direction="row" spacing={1}>
          <Button
            startIcon={loading ? <CircularProgress size={16} /> : <Refresh />}
            onClick={fetchPortfolio}
            disabled={loading}
            variant="outlined"
            size="small"
            sx={{ whiteSpace: 'nowrap', minWidth: 'fit-content' }}
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
            sx={{ whiteSpace: 'nowrap', minWidth: 'fit-content' }}
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
            <Card sx={{ mb: 3, border: '1px solid black', borderRadius: 0 }}>
              <CardContent>
                <Stack direction="row" spacing={1} alignItems="center" mb={2}>
                  <AccountBalance color="action" />
                  <Typography variant="h6" color="text.primary" fontFamily="serif" fontWeight="bold">
                    계좌 잔고
                  </Typography>
                </Stack>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', minHeight: 100, display: 'flex', flexDirection: 'column', justifyContent: 'center', border: '1px solid #e0e0e0', borderRadius: 0 }} elevation={0}>
                      <Typography variant="caption" color="text.secondary" gutterBottom>
                        총 자산
                      </Typography>
                      <Typography
                        variant="h6"
                        fontWeight="bold"
                        color="text.primary"
                        fontFamily="serif"
                        sx={{
                          fontSize: { xs: '0.9rem', sm: '1rem', md: '1.1rem' },
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}
                      >
                        ₩{formatNumber(balance.total_assets)}
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', minHeight: 100, display: 'flex', flexDirection: 'column', justifyContent: 'center', border: '1px solid #e0e0e0', borderRadius: 0 }} elevation={0}>
                      <Typography variant="caption" color="text.secondary" gutterBottom>
                        가능 현금
                      </Typography>
                      <Typography
                        variant="h6"
                        fontWeight="bold"
                        fontFamily="serif"
                        sx={{
                          fontSize: { xs: '0.9rem', sm: '1rem', md: '1.1rem' },
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}
                      >
                        ₩{formatNumber(balance.available_cash)}
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', minHeight: 100, display: 'flex', flexDirection: 'column', justifyContent: 'center', border: '1px solid #e0e0e0', borderRadius: 0 }} elevation={0}>
                      <Typography variant="caption" color="text.secondary" gutterBottom>
                        주식 평가액
                      </Typography>
                      <Typography
                        variant="h6"
                        fontWeight="bold"
                        color="text.primary"
                        fontFamily="serif"
                        sx={{
                          fontSize: { xs: '0.9rem', sm: '1rem', md: '1.1rem' },
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}
                      >
                        ₩{formatNumber(balance.total_evaluation)}
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', minHeight: 100, display: 'flex', flexDirection: 'column', justifyContent: 'center', border: '1px solid #e0e0e0', borderRadius: 0 }} elevation={0}>
                      <Typography variant="caption" color="text.secondary" gutterBottom>
                        평가손익
                      </Typography>
                      <Stack direction="row" spacing={0.5} justifyContent="center" alignItems="center">
                        {balance.total_profit_loss >= 0 ? (
                          <TrendingUp htmlColor="#C62828" fontSize="small" />
                        ) : (
                          <TrendingDown htmlColor="#1565C0" fontSize="small" />
                        )}
                        <Typography
                          variant="h6"
                          fontWeight="bold"
                          fontFamily="serif"
                          color={balance.total_profit_loss >= 0 ? '#C62828' : '#1565C0'}
                          sx={{
                            fontSize: { xs: '0.85rem', sm: '0.95rem', md: '1rem' },
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis'
                          }}
                        >
                          {balance.total_profit_loss >= 0 ? '+' : ''}
                          ₩{formatNumber(balance.total_profit_loss)}
                        </Typography>
                      </Stack>
                      <Chip
                        label={`${balance.total_profit_loss >= 0 ? '+' : ''}${balance.total_profit_loss_rate.toFixed(2)}%`}
                        variant="outlined"
                        size="small"
                        sx={{ mt: 1, borderColor: balance.total_profit_loss >= 0 ? '#C62828' : '#1565C0', color: balance.total_profit_loss >= 0 ? '#C62828' : '#1565C0', fontWeight: 'bold' }}
                      />
                    </Paper>
                  </Grid>
                </Grid>

                <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                  마지막 업데이트: {new Date(balance.updated_at).toLocaleString('ko-KR')}
                </Typography>
              </CardContent>
            </Card>
          )}

          {/* 보유 종목 테이블 */}
          <Card sx={{ border: '1px solid black', borderRadius: 0 }}>
            <CardContent>
              <Stack direction="row" spacing={1} alignItems="center" mb={2}>
                <ShowChart color="action" />
                <Typography variant="h6" fontFamily="serif" fontWeight="bold">보유 종목 ({holdings.length})</Typography>
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
                      {holdings.map((holding) => {
                        // Calculate missing fields if DB doesn't provide them
                        const evaluatedAmount = holding.evaluated_amount || (holding.current_price * holding.quantity)
                        const availableQty = holding.available_quantity ?? holding.quantity // Default to total quantity

                        return (
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
                                (매도가능: {formatNumber(availableQty)}주)
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
                                ₩{formatNumber(evaluatedAmount)}
                              </Typography>
                            </TableCell>
                            <TableCell align="right">
                              <Stack direction="row" spacing={0.5} justifyContent="flex-end" alignItems="center">
                                {holding.profit_loss >= 0 ? (
                                  <TrendingUp fontSize="small" color="error" />
                                ) : (
                                  <TrendingDown fontSize="small" color="primary" />
                                )}
                                <Typography
                                  variant="body2"
                                  fontWeight="bold"
                                  color={holding.profit_loss >= 0 ? 'error.main' : 'primary.main'}
                                >
                                  {holding.profit_loss >= 0 ? '+' : ''}
                                  ₩{formatNumber(holding.profit_loss)}
                                </Typography>
                              </Stack>
                            </TableCell>
                            <TableCell align="right">
                              <Chip
                                label={`${holding.profit_loss_rate >= 0 ? '+' : ''}${holding.profit_loss_rate.toFixed(2)}%`}
                                variant="outlined"
                                size="small"
                                sx={{ borderColor: holding.profit_loss_rate >= 0 ? '#C62828' : '#1565C0', color: holding.profit_loss_rate >= 0 ? '#C62828' : '#1565C0', fontWeight: 'bold' }}
                              />
                            </TableCell>
                          </TableRow>
                        )
                      })}
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