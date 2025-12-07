import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Tabs,
  Tab,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  LinearProgress,
  Button,
  Divider,
  Stack,
  IconButton,
  Tooltip,
  TablePagination,
  useTheme,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Assessment,
  TrendingUp,
  TrendingDown,
  ShowChart,
  Receipt,
  Settings,
  Download,
  Refresh,
  ArrowUpward,
  ArrowDownward,
  Lock,
} from '@mui/icons-material';
import { Chart } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler,
  TimeScale,
  TimeSeriesScale,
  ScatterController,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  Filler,
  TimeScale,
  TimeSeriesScale,
  ScatterController
);

interface BacktestResult {
  id: string;
  strategy_name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  total_return_rate: number; // 수익률 (%, percentage)
  annual_return: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  buy_count?: number;  // 매수 횟수
  sell_count?: number;  // 매도 횟수
  sharpe_ratio?: number;  // 샤프 비율
  sortino_ratio?: number;  // 소르티노 비율
  treynor_ratio?: number;  // 트레이너 비율
  volatility: number;
  trades: Trade[];
  daily_returns: DailyReturn[];
  strategy_config: any;
  investment_config: any;
  filtering_config: any;
  data_source?: string;  // 데이터 소스: "supabase", "mock", "external"
  data_source_detail?: {  // 데이터 소스 상세
    supabase: number;
    mock: number;
    unknown: number;
  };
}

interface Trade {
  date: string;
  stock_code?: string;
  stock_name?: string;
  code?: string;  // 백엔드에서 사용하는 필드
  action: 'buy' | 'sell';
  quantity?: number;
  shares?: number;  // 백엔드에서 사용하는 필드
  price: number;
  amount?: number;
  cost?: number;  // 백엔드에서 사용하는 필드 (매수)
  revenue?: number;  // 백엔드에서 사용하는 필드 (매도)
  profit_loss?: number;
  profit_rate?: number;
  profit_pct?: number;  // 백엔드에서 사용하는 수익률 필드
  proceeds?: number;  // 백엔드에서 사용하는 매도 수익금
  reason?: string;  // 백엔드 거래 이유 (engine.py에서 생성)
  signal_reason?: string;  // 매매 이유 (레거시)
  signal_details?: {  // 신호 상세 정보
    type?: string;
    profit_pct?: number;
    target?: number;
    loss_pct?: number;
    stop_loss?: number;
    signal_value?: number;
    matched_conditions?: string[];
  };
  profit?: number;  // 백엔드에서 사용하는 순이익
}

interface DailyReturn {
  date: string;
  portfolio_value: number;
  daily_return: number;
  cumulative_return: number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface BacktestResultViewerProps {
  result?: BacktestResult | null;
  onRefresh?: () => void;
}

const BacktestResultViewer: React.FC<BacktestResultViewerProps> = ({
  result: propResult,
  onRefresh
}) => {
  const theme = useTheme();
  const { hasRole } = useAuth();
  const [premiumDialogOpen, setPremiumDialogOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [result, setResult] = useState<BacktestResult | null>(propResult || null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    console.log('BacktestResultViewer received propResult:', propResult);
    if (propResult) {
      setResult(propResult);
      console.log('Result set with trades:', propResult.trades?.length, 'daily_returns:', propResult.daily_returns?.length);

      // 거래 사유 필드 디버깅
      if (propResult.trades && propResult.trades.length > 0) {
        const sampleTrade = propResult.trades[0];
        console.log('[Trade Debug] Sample trade keys:', Object.keys(sampleTrade));
        console.log('[Trade Debug] Sample trade reason field:', sampleTrade.reason);
        console.log('[Trade Debug] Sample trade signal_reason field:', sampleTrade.signal_reason);
      }
    }
  }, [propResult]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // 거래 중심 수익률 차트 데이터 생성
  const getChartData = () => {
    if (!result?.trades || !Array.isArray(result.trades) || result.trades.length === 0) {
      console.log('No trades data available for chart');
      return null;
    }

    // 거래를 날짜순으로 정렬
    const sortedTrades = [...result.trades].sort((a, b) =>
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );

    // 초기 자본금으로 시작
    let cumulativeCapital = result.initial_capital;
    const tradePoints: any[] = [];
    const buyPoints: any[] = [];
    const sellProfitPoints: any[] = [];
    const sellLossPoints: any[] = [];

    // 시작점 추가
    tradePoints.push({
      x: result.start_date,
      y: 0,
      label: '시작',
      capital: cumulativeCapital
    });

    sortedTrades.forEach((trade, index) => {
      const isBuy = trade.action === 'buy';
      const isSell = trade.action === 'sell';

      if (isSell) {
        // 매도 시 수익/손실 반영
        const profit = trade.profit_loss || trade.profit || 0;
        cumulativeCapital += profit;
      }

      const cumulativeReturn = ((cumulativeCapital - result.initial_capital) / result.initial_capital) * 100;

      const point = {
        x: trade.date,
        y: cumulativeReturn,
        trade: trade,
        capital: cumulativeCapital
      };

      tradePoints.push(point);

      // 매수/매도 포인트 분리
      if (isBuy) {
        buyPoints.push(point);
      } else if (isSell) {
        const profitRate = trade.profit_rate || trade.profit_pct || 0;
        if (profitRate >= 0) {
          sellProfitPoints.push(point);
        } else {
          sellLossPoints.push(point);
        }
      }
    });

    // 종료점 추가
    tradePoints.push({
      x: result.end_date,
      y: result.total_return_rate || 0,
      label: '종료',
      capital: result.final_capital
    });

    console.log('Creating trade-based chart with', sortedTrades.length, 'trades');

    return {
      datasets: [
        {
          type: 'line' as const,
          label: '포트폴리오 수익률',
          data: tradePoints,
          borderColor: 'rgb(100, 149, 237)',
          backgroundColor: 'rgba(100, 149, 237, 0.1)',
          borderWidth: 2,
          tension: 0.3,
          fill: true,
          pointRadius: 0,
          pointHoverRadius: 0,
        },
        {
          type: 'scatter' as const,
          label: '매수',
          data: buyPoints,
          backgroundColor: 'rgb(59, 130, 246)',
          borderColor: 'rgb(37, 99, 235)',
          borderWidth: 2,
          pointRadius: 6,
          pointHoverRadius: 8,
        },
        {
          type: 'scatter' as const,
          label: '매도 (수익)',
          data: sellProfitPoints,
          backgroundColor: 'rgb(34, 197, 94)',
          borderColor: 'rgb(22, 163, 74)',
          borderWidth: 2,
          pointRadius: 7,
          pointHoverRadius: 9,
          pointStyle: 'triangle',
        },
        {
          type: 'scatter' as const,
          label: '매도 (손실)',
          data: sellLossPoints,
          backgroundColor: 'rgb(239, 68, 68)',
          borderColor: 'rgb(220, 38, 38)',
          borderWidth: 2,
          pointRadius: 7,
          pointHoverRadius: 9,
          pointStyle: 'triangle',
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 15,
        }
      },
      title: {
        display: true,
        text: '거래별 수익률 추이',
        font: {
          size: 16,
          weight: 'bold' as const,
        }
      },
      tooltip: {
        enabled: true,
        callbacks: {
          title: function (context: any) {
            const dataPoint = context[0]?.raw;
            if (dataPoint?.label) {
              return dataPoint.label;
            }
            return dataPoint?.x || '';
          },
          label: function (context: any) {
            const dataPoint = context.raw;
            const labels = [];

            if (dataPoint?.trade) {
              const trade = dataPoint.trade;
              labels.push(`${trade.stock_name || trade.stock_code || ''}`);
              labels.push(`${trade.action === 'buy' ? '매수' : '매도'}: ${(trade.price || 0).toLocaleString()}원`);
              labels.push(`수량: ${(trade.quantity || trade.shares || 0).toLocaleString()}주`);

              if (trade.action === 'sell') {
                const profitRate = trade.profit_rate || trade.profit_pct || 0;
                const profit = trade.profit_loss || trade.profit || 0;
                labels.push(`수익: ${profit >= 0 ? '+' : ''}${profit.toLocaleString()}원 (${profitRate >= 0 ? '+' : ''}${profitRate.toFixed(2)}%)`);
                if (trade.reason) {
                  labels.push(`사유: ${trade.reason}`);
                }
              }
            }

            labels.push(`누적 수익률: ${(dataPoint?.y || 0).toFixed(2)}%`);
            labels.push(`포트폴리오: ${(dataPoint?.capital || 0).toLocaleString()}원`);

            return labels;
          }
        }
      },
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'day' as const,
          displayFormats: {
            day: 'yyyy-MM-dd'
          },
          tooltipFormat: 'yyyy-MM-dd'
        },
        title: {
          display: true,
          text: '거래 날짜'
        },
        grid: {
          display: true,
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          maxRotation: 45,
          minRotation: 0,
          autoSkip: true,
          maxTicksLimit: 15,
        }
      },
      y: {
        display: true,
        title: {
          display: true,
          text: '누적 수익률 (%)'
        },
        ticks: {
          callback: function (value: any) {
            return value.toFixed(1) + '%';
          },
        },
        grid: {
          display: true,
          color: 'rgba(255, 255, 255, 0.1)',
        }
      },
    },
    interaction: {
      mode: 'nearest' as const,
      intersect: true
    }
  };

  if (!result) {
    return (
      <Alert severity="info">
        백테스트 결과가 없습니다. 백테스트를 실행해주세요.
      </Alert>
    );
  }

  return (
    <Box>
      {/* 요약 정보 카드 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Stack spacing={1}>
                <Typography color="textSecondary" variant="body2">
                  총 수익률
                </Typography>
                <Typography
                  variant="h4"
                  color={result.total_return_rate >= 0 ? 'success.main' : 'error.main'}
                >
                  {result.total_return_rate >= 0 ? '+' : ''}{result.total_return_rate.toFixed(2)}%
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  연간 수익률: {result.annual_return.toFixed(2)}%
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Stack spacing={1}>
                <Typography color="textSecondary" variant="body2">
                  승률
                </Typography>
                <Typography variant="h4">
                  {result.win_rate.toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {result.winning_trades}승 {result.losing_trades}패
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Stack spacing={1}>
                <Typography color="textSecondary" variant="body2">
                  최대 낙폭
                </Typography>
                <Typography variant="h4" color="error.main">
                  {result.max_drawdown.toFixed(2)}%
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  변동성: {result.volatility.toFixed(2)}%
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Stack spacing={1}>
                <Typography color="textSecondary" variant="body2">
                  샤프 비율
                </Typography>
                <Typography variant="h4">
                  {result.sharpe_ratio?.toFixed(2) || 'N/A'}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  위험 대비 수익
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Stack spacing={1}>
                <Typography color="textSecondary" variant="body2">
                  소르티노 비율
                </Typography>
                <Typography variant="h4">
                  {result.sortino_ratio?.toFixed(2) || 'N/A'}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  하방 위험 대비 수익
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Stack spacing={1}>
                <Typography color="textSecondary" variant="body2">
                  트레이너 비율
                </Typography>
                <Typography variant="h4">
                  {result.treynor_ratio?.toFixed(2) || 'N/A'}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  시장 위험 대비 수익
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 상세 정보 탭 */}
      <Paper sx={{ width: '100%' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="백테스트 결과 탭">
          <Tab icon={<ShowChart />} iconPosition="start" label="수익률 차트" />
          <Tab icon={<Receipt />} iconPosition="start" label="거래 내역" />
          <Tab icon={<Assessment />} iconPosition="start" label="통계 분석" />
          <Tab icon={<Settings />} iconPosition="start" label="설정 정보" />
        </Tabs>

        {/* 수익률 차트 탭 */}
        <TabPanel value={tabValue} index={0}>
          {(() => {
            const chartData = getChartData();
            console.log('Chart data for rendering:', chartData);

            if (!chartData) {
              // 데이터가 없어도 더미 데이터로 차트를 표시
              const dummyData = {
                labels: ['시작', '종료'],
                datasets: [
                  {
                    label: '누적 수익률 (%)',
                    data: [0, result?.total_return_rate || 0],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1,
                    fill: true,
                  }
                ]
              };

              return (
                <Box>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    거래 데이터가 없습니다. 총 수익률만 표시합니다.
                  </Alert>
                  <Box sx={{ height: 400, position: 'relative' }}>
                    <Chart type='line' data={dummyData} options={chartOptions} />
                  </Box>
                </Box>
              );
            }

            return (
              <Box sx={{ height: 500, position: 'relative' }}>
                <Chart type='line' data={chartData} options={chartOptions} />
              </Box>
            );
          })()}
        </TabPanel>

        {/* 거래 내역 탭 */}
        <TabPanel value={tabValue} index={1}>
          {result.trades && Array.isArray(result.trades) && result.trades.length > 0 ? (
            <TableContainer component={Paper}>
              <Table sx={{ minWidth: 650 }} aria-label="거래 내역">
                <TableHead>
                  <TableRow>
                    <TableCell>날짜</TableCell>
                    <TableCell>종목</TableCell>
                    <TableCell align="center">구분</TableCell>
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={0.5}>
                        <span>매매 이유</span>
                        {!hasRole(['premium', 'admin']) && (
                          <Lock sx={{ fontSize: 16, color: 'warning.main' }} />
                        )}
                      </Stack>
                    </TableCell>
                    <TableCell align="right">수량</TableCell>
                    <TableCell align="right">단가</TableCell>
                    <TableCell align="right">금액</TableCell>
                    <TableCell align="right">손익</TableCell>
                    <TableCell align="right">수익률</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {result.trades
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((trade, index) => (
                      <TableRow key={index}>
                        <TableCell>{trade.date}</TableCell>
                        <TableCell>
                          <Stack>
                            <Typography variant="body2">{trade.stock_name || '종목'}</Typography>
                            <Typography variant="caption" color="textSecondary">
                              {trade.stock_code || trade.code || ''}
                            </Typography>
                          </Stack>
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={trade.action === 'buy' ? '매수' : '매도'}
                            color={trade.action === 'buy' ? 'primary' : 'secondary'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {hasRole(['premium', 'admin']) ? (
                            <Stack spacing={0.5}>
                              <Typography variant="caption" sx={{ maxWidth: 200, display: 'block' }}>
                                {trade.reason || trade.signal_reason || '-'}
                              </Typography>
                              {trade.signal_details?.type && (
                                <Chip
                                  label={trade.signal_details.type === 'target_profit' ? '목표달성' :
                                    trade.signal_details.type === 'stop_loss' ? '손절' :
                                      trade.signal_details.type === 'signal' ? '신호' :
                                        trade.signal_details.type === 'backtest_end' ? '청산' :
                                          trade.signal_details.type}
                                  size="small"
                                  variant="outlined"
                                  color={trade.signal_details.type === 'target_profit' ? 'success' :
                                    trade.signal_details.type === 'stop_loss' ? 'error' : 'default'}
                                />
                              )}
                            </Stack>
                          ) : (
                            <Chip
                              icon={<Lock />}
                              label="프리미엄 전용"
                              size="small"
                              color="warning"
                              onClick={() => setPremiumDialogOpen(true)}
                              sx={{ cursor: 'pointer' }}
                            />
                          )}
                        </TableCell>
                        <TableCell align="right">{(trade.shares || trade.quantity || 0).toLocaleString()}</TableCell>
                        <TableCell align="right">{(trade.price || 0).toLocaleString()}원</TableCell>
                        <TableCell align="right">{(trade.cost || trade.revenue || trade.amount || 0).toLocaleString()}원</TableCell>
                        <TableCell align="right">
                          {(trade.profit_loss !== undefined || trade.revenue !== undefined) && (
                            <Typography
                              color={trade.action === 'sell' ? 'success.main' : 'text.secondary'}
                            >
                              {trade.action === 'sell' ? '매도' : '-'}
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell align="right">
                          {(trade.profit_rate !== undefined || trade.profit_pct !== undefined) ? (
                            <Typography
                              color={(trade.profit_rate || trade.profit_pct || 0) >= 0 ? 'success.main' : 'error.main'}
                            >
                              {(trade.profit_rate || trade.profit_pct || 0) >= 0 ? '+' : ''}
                              {(trade.profit_rate || trade.profit_pct || 0).toFixed(2)}%
                            </Typography>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
              <TablePagination
                rowsPerPageOptions={[5, 10, 25, 50]}
                component="div"
                count={result.trades.length}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
                labelRowsPerPage="페이지당 행 수:"
              />
            </TableContainer>
          ) : (
            <Alert severity="info">거래 내역이 없습니다.</Alert>
          )}
        </TabPanel>

        {/* 통계 분석 탭 */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            {/* 데이터 소스 정보 */}
            {(result.data_source || result.data_source_detail) && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      데이터 소스
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Stack spacing={1}>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Typography>주 데이터 소스:</Typography>
                        <Chip
                          label={
                            result.data_source === 'supabase' ? '실제 시장 데이터 (Supabase)' :
                              result.data_source === 'mock' ? '시뮬레이션 데이터 (Mock)' :
                                '알 수 없음'
                          }
                          color={result.data_source === 'supabase' ? 'success' : 'warning'}
                          variant="outlined"
                        />
                      </Box>
                      {result.data_source_detail && (
                        <Box display="flex" alignItems="center" gap={2}>
                          <Typography variant="body2">상세:</Typography>
                          {result.data_source_detail.supabase > 0 && (
                            <Chip
                              label={`실제 데이터: ${result.data_source_detail.supabase}개`}
                              size="small"
                              color="success"
                            />
                          )}
                          {result.data_source_detail.mock > 0 && (
                            <Chip
                              label={`Mock 데이터: ${result.data_source_detail.mock}개`}
                              size="small"
                              color="warning"
                            />
                          )}
                          {result.data_source_detail.unknown > 0 && (
                            <Chip
                              label={`알 수 없음: ${result.data_source_detail.unknown}개`}
                              size="small"
                            />
                          )}
                        </Box>
                      )}
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            )}

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    수익 분석
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  <Stack spacing={2}>
                    <Box display="flex" justifyContent="space-between">
                      <Typography>초기 자본금</Typography>
                      <Typography fontWeight="bold">
                        {result.initial_capital.toLocaleString()}원
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Typography>최종 자본금</Typography>
                      <Typography fontWeight="bold">
                        {result.final_capital.toLocaleString()}원
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Typography>순손익</Typography>
                      <Typography
                        fontWeight="bold"
                        color={(result.final_capital - result.initial_capital) >= 0 ? 'success.main' : 'error.main'}
                      >
                        {(result.final_capital - result.initial_capital >= 0 ? '+' : '')}
                        {(result.final_capital - result.initial_capital).toLocaleString()}원
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    거래 통계
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  <Stack spacing={2}>
                    <Box display="flex" justifyContent="space-between">
                      <Typography>총 거래 횟수 (완료)</Typography>
                      <Typography fontWeight="bold">{result.total_trades}회</Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Typography>매수 횟수</Typography>
                      <Typography fontWeight="bold" color="primary.main">
                        {result.buy_count || result.total_trades || 0}회
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Typography>매도 횟수</Typography>
                      <Typography fontWeight="bold" color="secondary.main">
                        {result.sell_count || result.total_trades || 0}회
                      </Typography>
                    </Box>
                    <Divider />
                    <Box display="flex" justifyContent="space-between">
                      <Typography>승리 거래</Typography>
                      <Typography fontWeight="bold" color="success.main">
                        {result.winning_trades}회
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Typography>패배 거래</Typography>
                      <Typography fontWeight="bold" color="error.main">
                        {result.losing_trades}회
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 설정 정보 탭 */}
        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            {/* 전략 설정 */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    전략 설정
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  <Stack spacing={1}>
                    <Typography variant="body2">
                      <strong>전략명:</strong> {result.strategy_name}
                    </Typography>
                    <Typography variant="body2">
                      <strong>기간:</strong> {result.start_date} ~ {result.end_date}
                    </Typography>
                    {result.strategy_config && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          전략 파라미터:
                        </Typography>
                        <pre style={{
                          fontSize: '0.8rem',
                          overflow: 'auto',
                          backgroundColor: theme.palette.mode === 'dark' ? '#2a2a2a' : '#f5f5f5',
                          color: theme.palette.text.primary,
                          padding: 8,
                          borderRadius: 4,
                          border: `1px solid ${theme.palette.divider}`
                        }}>
                          {JSON.stringify(result.strategy_config, null, 2)}
                        </pre>
                      </Box>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            {/* 투자 설정 */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    투자 설정
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  {result.investment_config ? (
                    <Stack spacing={2}>
                      {/* 투자 유니버스 타입 */}
                      <Box>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          투자 유니버스 유형
                        </Typography>
                        <Chip
                          label={
                            result.investment_config.universe_type === 'single_stock'
                              ? '단일 종목'
                              : result.investment_config.universe_type === 'investment_filter'
                                ? '투자유니버스 (필터)'
                                : result.investment_config.universe_type === 'multiple_stocks'
                                  ? '복수 종목 (수동 선택)'
                                  : result.investment_config.universe_type || '알 수 없음'
                          }
                          color={
                            result.investment_config.universe_type === 'single_stock'
                              ? 'primary'
                              : result.investment_config.universe_type === 'investment_filter'
                                ? 'success'
                                : result.investment_config.universe_type === 'multiple_stocks'
                                  ? 'info'
                                  : 'default'
                          }
                          size="small"
                        />
                      </Box>

                      {/* 단일 종목인 경우 */}
                      {result.investment_config.universe_type === 'single_stock' && (
                        <Box>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            종목 정보
                          </Typography>
                          <Paper variant="outlined" sx={{ p: 1.5 }}>
                            <Typography variant="body2">
                              <strong>종목코드:</strong> {result.investment_config.stock_code || '-'}
                            </Typography>
                            {result.investment_config.stock_name && (
                              <Typography variant="body2">
                                <strong>종목명:</strong> {result.investment_config.stock_name}
                              </Typography>
                            )}
                          </Paper>
                        </Box>
                      )}

                      {/* 투자유니버스인 경우 */}
                      {result.investment_config.universe_type === 'investment_filter' && (
                        <Box>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            투자유니버스 정보
                          </Typography>
                          <Paper variant="outlined" sx={{ p: 1.5 }}>
                            {result.investment_config.filter_name && (
                              <Typography variant="body2" gutterBottom>
                                <strong>유니버스명:</strong> {result.investment_config.filter_name}
                              </Typography>
                            )}
                            {result.investment_config.filter_id && (
                              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                                ID: {result.investment_config.filter_id}
                              </Typography>
                            )}
                            {result.investment_config.stock_count && (
                              <Box sx={{ mt: 1 }}>
                                <Chip
                                  label={`${result.investment_config.stock_count}개 종목`}
                                  size="small"
                                  color="success"
                                  variant="outlined"
                                />
                              </Box>
                            )}
                            {result.investment_config.stocks && Array.isArray(result.investment_config.stocks) && (
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="caption" color="text.secondary" display="block">
                                  포함 종목 샘플:
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {result.investment_config.stocks.slice(0, 10).join(', ')}
                                  {result.investment_config.stocks.length > 10 ? '...' : ''}
                                </Typography>
                              </Box>
                            )}
                          </Paper>
                        </Box>
                      )}

                      {/* 복수 종목 (수동 선택)인 경우 */}
                      {result.investment_config.universe_type === 'multiple_stocks' && (
                        <Box>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            선택 종목 정보
                          </Typography>
                          <Paper variant="outlined" sx={{ p: 1.5 }}>
                            {result.investment_config.stock_count && (
                              <Box sx={{ mb: 1 }}>
                                <Chip
                                  label={`${result.investment_config.stock_count}개 종목 (수동 선택)`}
                                  size="small"
                                  color="info"
                                  variant="outlined"
                                />
                              </Box>
                            )}
                            {result.investment_config.stocks && Array.isArray(result.investment_config.stocks) && (
                              <Box>
                                <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                                  선택된 종목:
                                </Typography>
                                <Typography variant="body2">
                                  {result.investment_config.stocks.join(', ')}
                                </Typography>
                              </Box>
                            )}
                          </Paper>
                        </Box>
                      )}

                      {/* 초기 자본금 */}
                      {result.investment_config.initial_capital && (
                        <Box>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            초기 자본금
                          </Typography>
                          <Typography variant="body1" fontWeight="medium">
                            {result.investment_config.initial_capital.toLocaleString()}원
                          </Typography>
                        </Box>
                      )}

                      {/* 기타 설정이 있는 경우 */}
                      {Object.keys(result.investment_config).some(key =>
                        !['universe_type', 'stock_code', 'stock_name', 'filter_name', 'filter_id', 'stock_count', 'stocks', 'initial_capital'].includes(key)
                      ) && (
                          <Box>
                            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                              추가 설정
                            </Typography>
                            <Paper variant="outlined" sx={{ p: 1, bgcolor: 'grey.50' }}>
                              <pre style={{
                                fontSize: '0.75rem',
                                overflow: 'auto',
                                margin: 0,
                                maxHeight: 150,
                                color: '#000'
                              }}>
                                {JSON.stringify(
                                  Object.fromEntries(
                                    Object.entries(result.investment_config).filter(([key]) =>
                                      !['universe_type', 'stock_code', 'stock_name', 'filter_name', 'filter_id', 'stock_count', 'stocks', 'initial_capital'].includes(key)
                                    )
                                  ),
                                  null,
                                  2
                                )}
                              </pre>
                            </Paper>
                          </Box>
                        )}
                    </Stack>
                  ) : (
                    <Alert severity="info">
                      투자 설정 정보가 없습니다.
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* 필터링 설정 */}
            {result.filtering_config && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      필터링 설정
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <pre style={{
                      fontSize: '0.8rem',
                      overflow: 'auto',
                      backgroundColor: '#f5f5f5',
                      padding: 8,
                      borderRadius: 4,
                      color: '#000'
                    }}>
                      {JSON.stringify(result.filtering_config, null, 2)}
                    </pre>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        </TabPanel>
      </Paper>

      {/* 액션 버튼 */}
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        {onRefresh && (
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={onRefresh}
          >
            새로고침
          </Button>
        )}
        <Button
          variant="contained"
          startIcon={hasRole(['premium', 'admin']) ? <Download /> : <Lock />}
          color={hasRole(['premium', 'admin']) ? 'primary' : 'warning'}
          onClick={() => {
            // Premium 권한 확인
            if (!hasRole(['premium', 'admin'])) {
              setPremiumDialogOpen(true);
              return;
            }

            // CSV 다운로드 로직 (UTF-8 BOM 추가, 모든 지표 포함)

            // 1. 모든 거래에서 사용된 지표 목록 수집
            const allIndicatorKeys = new Set<string>();
            result.trades.forEach(t => {
              const indicators = (t as any).indicators || {};
              Object.keys(indicators).forEach(key => allIndicatorKeys.add(key));
            });
            const indicatorColumns = Array.from(allIndicatorKeys).sort();

            // 2. 헤더 생성 (기본 컬럼 + 단계 + 지표들)
            const baseHeaders = ['날짜', '종목코드', '종목명', '구분', '수량', '단가', '금액', '손익', '수익률', '단계', '매수이유'];
            const indicatorHeaders = indicatorColumns.map(key => {
              // 지표명을 한글로 변환 (선택적)
              const displayName = key.toUpperCase();
              return displayName;
            });
            const headers = [...baseHeaders, ...indicatorHeaders].join(',');

            // 3. 데이터 행 생성
            const rows = result.trades.map(t => {
              const baseData = [
                t.date,
                t.stock_code,
                t.stock_name,
                t.action,
                t.quantity,
                t.price,
                t.amount,
                t.profit_loss || '',
                t.profit_rate || '',
                (t as any).stage || '',
                (t as any).reason || ''
              ];

              // 각 지표 값 추가
              const indicators = (t as any).indicators || {};
              const indicatorValues = indicatorColumns.map(key => {
                const value = indicators[key];
                if (value !== undefined && value !== null) {
                  // 숫자면 소수점 2자리로 포맷
                  return typeof value === 'number' ? value.toFixed(2) : value;
                }
                return '';
              });

              return [...baseData, ...indicatorValues].join(',');
            });

            const csvContent = headers + '\n' + rows.join('\n');

            // UTF-8 BOM 추가 (엑셀에서 한글 깨짐 방지)
            const BOM = '\uFEFF';
            const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `backtest_result_${result.id}.csv`;
            link.click();
          }}
        >
          결과 다운로드
        </Button>
      </Box>

      {/* Premium 업그레이드 다이얼로그 */}
      <Dialog open={premiumDialogOpen} onClose={() => setPremiumDialogOpen(false)}>
        <DialogTitle>프리미엄 기능</DialogTitle>
        <DialogContent>
          <Typography>
            백테스트 결과 다운로드는 프리미엄 회원 전용 기능입니다.
          </Typography>
          <Typography sx={{ mt: 2 }} variant="body2" color="text.secondary">
            프리미엄 회원이 되면 다음과 같은 혜택을 받으실 수 있습니다:
          </Typography>
          <ul>
            <li>백테스트 결과 CSV 다운로드</li>
            <li>전략 분석 도구 사용</li>
            <li>고급 기술 지표 활용</li>
          </ul>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPremiumDialogOpen(false)}>닫기</Button>
          <Button variant="contained" color="primary" onClick={() => setPremiumDialogOpen(false)}>
            프리미엄 업그레이드
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BacktestResultViewer;