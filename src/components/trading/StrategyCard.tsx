import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Stack,
  Chip,
  Button,
  Divider,
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Collapse,
  IconButton,
  Alert
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  Stop,
  Settings,
  ExpandMore,
  ExpandLess,
  Warning,
  CheckCircle,
  Delete,
  BarChart as BarChartIcon,
  Star
} from '@mui/icons-material'
import { supabase } from '../../lib/supabase'



interface Position {
  stock_code: string
  stock_name: string
  quantity: number
  avg_price: number
  current_price: number
  profit_rate: number
  profit_amount: number
}

interface StrategyCardProps {
  strategyId: string
  strategyName: string
  universes: { filter_id: string; filter_name: string }[]
  allocatedCapital: number
  allocatedPercent: number
  onStop: () => void
  onEdit: () => void
  onDelete: () => void
}

export default function StrategyCard({
  strategyId,
  strategyName,
  universes,
  allocatedCapital,
  allocatedPercent,
  onStop,
  onEdit,
  onDelete
}: StrategyCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(true)
  const [showBuySignals, setShowBuySignals] = useState(false)
  const [showHoldings, setShowHoldings] = useState(false)
  const [showSellSignals, setShowSellSignals] = useState(false)

  const [monitoringSignals, setMonitoringSignals] = useState<any[]>([])

  useEffect(() => {
    loadStrategyData()
  }, [strategyId])

  const loadStrategyData = async () => {
    try {
      setLoading(true)

      // 포지션 조회 (실제 계좌 연동 데이터 사용 - portfolio 테이블)
      // 기존 positions 테이블은 봇 내부 로직용이나, 계좌 동기화된 현황을 우선 표시
      const { data: positionData, error: positionError } = await supabase
        .from('portfolio') // Changed from 'positions'
        .select('*')
      // .eq('strategy_id', strategyId) // portfolio table has no strategy_id

      if (!positionError && positionData) {
        // 현재가 정보와 조인하여 계산 (이미 portfolio에 sync된 데이터가 있지만 최신가 확인)
        const positionsWithPrice = await Promise.all(
          positionData.map(async (pos: any) => {
            const { data: priceData } = await supabase
              .from('kw_price_current')
              .select('current_price, stock_name')
              .eq('stock_code', pos.stock_code)
              .single()

            const currentPrice = priceData?.current_price || pos.current_price // Use sync price as fallback
            const avgPrice = pos.avg_price
            const invested = avgPrice * pos.quantity
            const value = currentPrice * pos.quantity

            // [FIX] Use DB value (Net Profit from Kiwoom) if available, otherwise calculate (Gross)
            const netProfit = pos.profit_loss
            const calculatedProfit = value - invested
            const finalProfit = netProfit !== null && netProfit !== undefined ? netProfit : calculatedProfit

            const finalProfitRate = invested > 0 ? (finalProfit / invested) * 100 : 0

            // Map portfolio fields to Position interface
            return {
              stock_code: pos.stock_code,
              stock_name: priceData?.stock_name || pos.stock_name,
              quantity: pos.quantity,
              avg_price: avgPrice,
              current_price: currentPrice,
              profit_rate: finalProfitRate,
              profit_amount: finalProfit
            }
          })
        )

        setPositions(positionsWithPrice)
      }

      // 모니터링 데이터 조회 (매수/매도 대기)
      const { data: monitoringData, error: monitoringError } = await supabase
        .from('strategy_monitoring')
        .select('*')
        .eq('strategy_id', strategyId)
        .or('is_near_entry.eq.true,is_near_exit.eq.true')
        .order('updated_at', { ascending: false })

      if (!monitoringError && monitoringData) {
        setMonitoringSignals(monitoringData)
      }

    } catch (error) {
      console.error('전략 데이터 로드 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ko-KR').format(value)
  }

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  const getProfitColor = (value: number) => {
    if (value > 0) return 'error.main'
    if (value < 0) return 'primary.main'
    return 'text.secondary'
  }

  const buySignals = monitoringSignals.filter(s => s.is_near_entry)
  const sellSignals = monitoringSignals.filter(s => s.is_near_exit)

  const totalInvested = positions.reduce((sum, pos) => sum + (pos.avg_price * pos.quantity), 0)
  const totalValue = positions.reduce((sum, pos) => sum + (pos.current_price * pos.quantity), 0)
  // [FIX] Sum individual profits (Net) instead of calculating Gross difference
  const totalProfit = positions.reduce((sum, pos) => sum + pos.profit_amount, 0)
  const totalProfitRate = totalInvested > 0 ? (totalProfit / totalInvested) * 100 : 0
  const availableCapital = allocatedCapital - totalInvested

  return (
    <Paper sx={{ p: 3, mb: 2, border: '1px solid', borderColor: 'divider' }}>
      <Stack spacing={2}>
        {/* 헤더 */}
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              {strategyName}
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip
                label={`${allocatedPercent}% 할당`}
                size="small"
                variant="outlined"
                sx={{ borderColor: 'text.secondary', color: 'text.secondary' }}
              />
              {universes.map((u) => (
                <Chip
                  key={u.filter_id}
                  label={u.filter_name}
                  size="small"
                  variant="outlined"
                  sx={{ borderColor: 'text.secondary', color: 'text.secondary' }}
                />
              ))}
            </Stack>
          </Box>

          <Stack direction="row" spacing={1}>
            <Button
              size="small"
              startIcon={<Settings />}
              onClick={onEdit}
              variant="outlined"
              sx={{ color: 'text.primary', borderColor: 'rgba(0,0,0,0.23)' }}
            >
              수정
            </Button>
            <Button
              size="small"
              startIcon={<Stop />}
              onClick={onStop}
              variant="outlined"
              sx={{ color: 'text.primary', borderColor: 'rgba(0,0,0,0.23)' }}
            >
              중지
            </Button>
            <Button
              size="small"
              startIcon={<Delete />}
              onClick={onDelete}
              variant="outlined"
              sx={{ color: 'text.primary', borderColor: 'rgba(0,0,0,0.23)' }}
            >
              삭제
            </Button>
            <IconButton onClick={() => setExpanded(!expanded)} size="small">
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Stack>
        </Stack>

        <Divider />

        {/* 요약 정보 */}
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                할당금액
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {formatCurrency(allocatedCapital)}원
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                투자 중
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {formatCurrency(totalInvested)}원
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {positions.length}개 종목
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                대기금액
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {formatCurrency(availableCapital)}원
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(totalInvested / allocatedCapital) * 100}
                sx={{ mt: 1 }}
              />
            </Box>
          </Grid>

          <Grid item xs={12} md={3}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                수익률
              </Typography>
              <Typography
                variant="h6"
                fontWeight="bold"
                color={getProfitColor(totalProfitRate)}
              >
                {formatPercent(totalProfitRate)}
              </Typography>
              <Typography variant="caption" color={getProfitColor(totalProfit)}>
                {formatCurrency(Math.abs(totalProfit))}원
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* 시그널 현황 */}
        <Box>
          <Typography variant="subtitle2" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <BarChartIcon sx={{ mr: 1, color: 'text.primary' }} /> 시그널 현황
          </Typography>
          <Stack spacing={1}>
            <Stack direction="row" spacing={2}>
              <Chip
                icon={<TrendingUp sx={{ color: 'text.secondary !important' }} />}
                label={`매수 대기: ${buySignals.length}종목`}
                variant="outlined"
                onClick={() => setShowBuySignals(!showBuySignals)}
                sx={{ cursor: 'pointer', borderColor: 'text.secondary', color: 'text.secondary' }}
              />
              <Chip
                icon={<CheckCircle sx={{ color: 'text.secondary !important' }} />}
                label={`보유 중: ${positions.length}종목`}
                variant="outlined"
                onClick={() => setShowHoldings(!showHoldings)}
                sx={{ cursor: 'pointer', borderColor: 'text.secondary', color: 'text.secondary' }}
              />
              <Chip
                icon={<TrendingDown sx={{ color: 'text.secondary !important' }} />}
                label={`매도 예정: ${sellSignals.length}종목`}
                variant="outlined"
                onClick={() => setShowSellSignals(!showSellSignals)}
                sx={{ cursor: 'pointer', borderColor: 'text.secondary', color: 'text.secondary' }}
              />
            </Stack>

            {/* 매수 대기 종목 리스트 */}
            <Collapse in={showBuySignals}>
              {buySignals.length > 0 ? (
                <Box sx={{ mt: 1, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="caption" fontWeight="bold" gutterBottom display="block">
                    💰 매수 대기 종목
                  </Typography>
                  <Stack spacing={0.5}>
                    {buySignals.slice(0, 5).map((signal, idx) => (
                      <Box
                        key={idx}
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          p: 1,
                          bgcolor: 'background.paper',
                          borderRadius: 0.5
                        }}
                      >
                        <Typography variant="body2">
                          {signal.stock_name} ({signal.stock_code})
                        </Typography>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Typography variant="body2">
                            {formatCurrency(signal.current_price)}원
                          </Typography>
                          <Chip
                            label={`${signal.condition_match_score}점`}
                            size="small"
                            variant="outlined"
                            sx={{ borderColor: 'text.secondary', color: 'text.secondary' }}
                          />
                        </Stack>
                      </Box>
                    ))}
                    {buySignals.length > 5 && (
                      <Typography variant="caption" color="text.secondary" sx={{ pl: 1 }}>
                        외 {buySignals.length - 5}종목 (전체 {buySignals.length}종목)
                      </Typography>
                    )}
                  </Stack>
                </Box>
              ) : (
                <Box sx={{ mt: 1, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    매수 대기 종목이 없습니다.
                  </Typography>
                </Box>
              )}
            </Collapse>

            {/* 보유 중 종목 리스트 */}
            <Collapse in={showHoldings}>
              {positions.length > 0 ? (
                <Box sx={{ mt: 1, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="caption" fontWeight="bold" gutterBottom display="block">
                    📈 보유 중인 종목
                  </Typography>
                  <Stack spacing={0.5}>
                    {positions.slice(0, 5).map((pos) => (
                      <Box
                        key={pos.stock_code}
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          p: 1,
                          bgcolor: 'background.paper',
                          borderRadius: 0.5
                        }}
                      >
                        <Typography variant="body2">
                          {pos.stock_name} ({pos.stock_code})
                        </Typography>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Typography variant="body2">
                            {pos.quantity}주
                          </Typography>
                          <Typography
                            variant="caption"
                            color={getProfitColor(pos.profit_rate)}
                            fontWeight="bold"
                          >
                            {formatPercent(pos.profit_rate)}
                          </Typography>
                        </Stack>
                      </Box>
                    ))}
                    {positions.length > 5 && (
                      <Typography variant="caption" color="text.secondary" sx={{ pl: 1 }}>
                        외 {positions.length - 5}종목 (전체 {positions.length}종목)
                      </Typography>
                    )}
                  </Stack>
                </Box>
              ) : (
                <Box sx={{ mt: 1, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    보유 중인 종목이 없습니다.
                  </Typography>
                </Box>
              )}
            </Collapse>

            {/* 매도 예정 종목 리스트 */}
            <Collapse in={showSellSignals}>
              {sellSignals.length > 0 ? (
                <Box sx={{ mt: 1, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="caption" fontWeight="bold" gutterBottom display="block">
                    📉 매도 예정 종목
                  </Typography>
                  <Stack spacing={0.5}>
                    {sellSignals.slice(0, 5).map((signal, idx) => {
                      const position = positions.find(p => p.stock_code === signal.stock_code)
                      return (
                        <Box
                          key={idx}
                          sx={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            p: 1,
                            bgcolor: 'background.paper',
                            borderRadius: 0.5
                          }}
                        >
                          <Typography variant="body2">
                            {signal.stock_name} ({signal.stock_code})
                          </Typography>
                          <Stack direction="row" spacing={1} alignItems="center">
                            <Typography variant="body2">
                              {formatCurrency(signal.current_price)}원
                            </Typography>
                            {position && (
                              <Typography
                                variant="caption"
                                color={getProfitColor(position.profit_rate)}
                                fontWeight="bold"
                              >
                                {formatPercent(position.profit_rate)}
                              </Typography>
                            )}
                            <Chip
                              label={`${signal.exit_condition_match_score || signal.condition_match_score}점`}
                              size="small"
                              variant="outlined"
                              sx={{ borderColor: 'text.secondary', color: 'text.secondary' }}
                            />
                          </Stack>
                        </Box>
                      )
                    })}
                    {sellSignals.length > 5 && (
                      <Typography variant="caption" color="text.secondary" sx={{ pl: 1 }}>
                        외 {sellSignals.length - 5}종목 (전체 {sellSignals.length}종목)
                      </Typography>
                    )}
                  </Stack>
                </Box>
              ) : (
                <Box sx={{ mt: 1, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    매도 예정 종목이 없습니다.
                  </Typography>
                </Box>
              )}
            </Collapse>
          </Stack>
        </Box>

        {/* 주요 종목 */}
        {positions.length > 0 && (
          <Box>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Star sx={{ mr: 1, color: 'text.primary' }} /> 주요 보유 종목 (상위 3개)
            </Typography>
            <Stack spacing={1}>
              {positions
                .sort((a, b) => Math.abs(b.profit_rate) - Math.abs(a.profit_rate))
                .slice(0, 3)
                .map((pos) => (
                  <Box
                    key={pos.stock_code}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 1,
                      bgcolor: 'background.default',
                      borderRadius: 1
                    }}
                  >
                    <Typography variant="body2" fontWeight="medium">
                      {pos.stock_name} ({pos.stock_code})
                    </Typography>
                    <Stack direction="row" spacing={2} alignItems="center">
                      <Typography
                        variant="body2"
                        color={getProfitColor(pos.profit_rate)}
                        fontWeight="bold"
                      >
                        {formatPercent(pos.profit_rate)}
                      </Typography>
                      {pos.profit_rate >= 10 && (
                        <Chip
                          icon={<TrendingUp sx={{ color: 'text.secondary !important' }} />}
                          label="매도 근접"
                          size="small"
                          variant="outlined"
                          sx={{ borderColor: 'text.secondary', color: 'text.secondary' }}
                        />
                      )}
                      {pos.profit_rate <= -7 && (
                        <Chip
                          icon={<Warning sx={{ color: 'text.secondary !important' }} />}
                          label="손절 주의"
                          size="small"
                          variant="outlined"
                          sx={{ borderColor: 'text.secondary', color: 'text.secondary' }}
                        />
                      )}
                    </Stack>
                  </Box>
                ))}
            </Stack>
          </Box>
        )}

        {/* 상세 정보 (접을 수 있음) */}
        <Collapse in={expanded}>
          <Stack spacing={2}>
            <Divider />

            {/* 전체 포지션 */}
            {positions.length > 0 ? (
              <Box>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                  전체 보유 종목
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>종목명</TableCell>
                        <TableCell align="right">수량</TableCell>
                        <TableCell align="right">평균단가</TableCell>
                        <TableCell align="right">현재가</TableCell>
                        <TableCell align="right">수익률</TableCell>
                        <TableCell align="right">평가손익</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {positions.map((pos) => (
                        <TableRow key={pos.stock_code}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {pos.stock_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {pos.stock_code}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">{pos.quantity}주</TableCell>
                          <TableCell align="right">{formatCurrency(pos.avg_price)}원</TableCell>
                          <TableCell align="right">{formatCurrency(pos.current_price)}원</TableCell>
                          <TableCell align="right">
                            <Typography
                              variant="body2"
                              color={getProfitColor(pos.profit_rate)}
                              fontWeight="bold"
                            >
                              {formatPercent(pos.profit_rate)}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography
                              variant="body2"
                              color={getProfitColor(pos.profit_amount)}
                              fontWeight="bold"
                            >
                              {formatCurrency(Math.abs(pos.profit_amount))}원
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            ) : (
              <Alert severity="info">보유 중인 종목이 없습니다.</Alert>
            )}


          </Stack>
        </Collapse>
      </Stack>
    </Paper>
  )
}
