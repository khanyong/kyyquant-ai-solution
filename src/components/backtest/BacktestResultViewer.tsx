import React, { useState, useEffect } from 'react';
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
} from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
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
} from 'chart.js';

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  Filler
);

interface BacktestResult {
  id: string;
  strategy_name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  total_return: number;
  annual_return: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  buy_count?: number;  // 매수 횟수
  sell_count?: number;  // 매도 횟수
  sharpe_ratio: number;
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
  signal_reason?: string;  // 매매 이유
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

  // 수익률 차트 데이터 생성
  const getChartData = () => {
    if (!result?.daily_returns || !Array.isArray(result.daily_returns) || result.daily_returns.length === 0) {
      console.log('No daily_returns data available for chart', {
        exists: !!result?.daily_returns,
        isArray: Array.isArray(result?.daily_returns),
        type: typeof result?.daily_returns,
        value: result?.daily_returns
      });
      return null;
    }

    console.log('Creating chart data with', result.daily_returns.length, 'data points');
    return {
      labels: result.daily_returns.map(d => d.date || ''),
      datasets: [
        {
          label: '누적 수익률 (%)',
          data: result.daily_returns.map(d => d.cumulative_return || 0),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1,
          fill: true,
        },
        {
          label: '일일 수익률 (%)',
          data: result.daily_returns.map(d => d.daily_return || 0),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.1,
          fill: false,
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
      },
      title: {
        display: true,
        text: '수익률 추이',
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: '날짜'
        }
      },
      y: {
        display: true,
        beginAtZero: true,
        title: {
          display: true,
          text: '수익률 (%)'
        },
        ticks: {
          callback: function(value: any) {
            return value + '%';
          },
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
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
                  color={result.total_return >= 0 ? 'success.main' : 'error.main'}
                >
                  {result.total_return >= 0 ? '+' : ''}{result.total_return.toFixed(2)}%
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
                  {result.sharpe_ratio.toFixed(2)}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  총 거래: {result.total_trades}회
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
                    data: [0, result?.total_return || 0],
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
                    상세 일일 수익률 데이터가 없습니다. 총 수익률만 표시합니다.
                  </Alert>
                  <Box sx={{ height: 400, position: 'relative' }}>
                    <Line data={dummyData} options={chartOptions} />
                  </Box>
                </Box>
              );
            }
            
            return (
              <Box sx={{ height: 400, position: 'relative' }}>
                <Line data={chartData} options={chartOptions} />
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
                    <TableCell>매매 이유</TableCell>
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
                        <Stack spacing={0.5}>
                          <Typography variant="caption" sx={{ maxWidth: 200, display: 'block' }}>
                            {(trade as any).reason || trade.signal_reason || '-'}
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
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        투자 유니버스:
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
                        {JSON.stringify(result.investment_config, null, 2)}
                      </pre>
                    </Box>
                  ) : (
                    <Typography variant="body2" color="textSecondary">
                      투자 설정 정보가 없습니다.
                    </Typography>
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
                      borderRadius: 4
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
          startIcon={<Download />}
          onClick={() => {
            // CSV 다운로드 로직
            const csvContent = `날짜,종목코드,종목명,구분,수량,단가,금액,손익,수익률\n` +
              result.trades.map(t => 
                `${t.date},${t.stock_code},${t.stock_name},${t.action},${t.quantity},${t.price},${t.amount},${t.profit_loss || ''},${t.profit_rate || ''}`
              ).join('\n');
            
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `backtest_result_${result.id}.csv`;
            link.click();
          }}
        >
          결과 다운로드
        </Button>
      </Box>
    </Box>
  );
};

export default BacktestResultViewer;