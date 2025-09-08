import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Stack,
  Alert,
  Tooltip,
  Divider,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  CompareArrows,
  TrendingUp,
  TrendingDown,
  Delete,
  Visibility,
  VisibilityOff,
  Download,
  FilterList,
  Search,
  DateRange,
  Assessment,
  Timeline,
  BarChart,
  TableChart,
} from '@mui/icons-material';
import { Line, Bar, Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler,
} from 'chart.js';
import { supabase } from '../../lib/supabase';
import { authService } from '../../services/auth';
import BacktestResultViewer from './BacktestResultViewer';

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  ChartTooltip,
  Legend,
  Filler
);

interface BacktestRecord {
  id: string;
  strategy_name?: string;
  created_at: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  total_return: number;
  max_drawdown: number;
  win_rate?: number;
  sharpe_ratio?: number;
  total_trades: number;
  profitable_trades: number;
  winning_trades?: number;
  losing_trades?: number;
  avg_profit?: number;
  avg_loss?: number;
  profit_factor?: number;
  recovery_factor?: number;
  results_data?: any;
  trade_details?: any;
  daily_returns?: any;
  selected?: boolean;
  visible?: boolean;
  color?: string;
}

const COLORS = [
  '#3F51B5', // Blue
  '#F44336', // Red
  '#4CAF50', // Green
  '#FF9800', // Orange
  '#9C27B0', // Purple
  '#00BCD4', // Cyan
  '#795548', // Brown
  '#607D8B', // Blue Grey
];

const BacktestComparison: React.FC = () => {
  const [records, setRecords] = useState<BacktestRecord[]>([]);
  const [filteredRecords, setFilteredRecords] = useState<BacktestRecord[]>([]);
  const [selectedRecords, setSelectedRecords] = useState<BacktestRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'table' | 'chart' | 'detail'>('table');
  const [chartType, setChartType] = useState<'line' | 'bar' | 'radar'>('line');
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState({
    startDate: '',
    endDate: '',
  });
  const [sortBy, setSortBy] = useState<keyof BacktestRecord>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedDetail, setSelectedDetail] = useState<BacktestRecord | null>(null);

  // 백테스트 기록 로드
  useEffect(() => {
    loadBacktestRecords();
  }, []);

  // 필터링 적용
  useEffect(() => {
    applyFilters();
  }, [records, searchTerm, dateFilter]);

  const loadBacktestRecords = async () => {
    try {
      setLoading(true);
      const user = await authService.getCurrentUser();
      
      if (!user) {
        console.warn('User not logged in');
        setLoading(false);
        return;
      }

      // Supabase에서 백테스트 결과 조회
      // 개발 모드: 모든 사용자의 데이터 조회 (user_id 필터 제거)
      // 프로덕션에서는 .eq('user_id', user.id) 추가 필요
      const { data, error } = await supabase
        .from('backtest_results')
        .select('*')
        // .eq('user_id', user.id)  // 개발 중 주석 처리
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error loading backtest results:', error);
        
        // 더미 데이터 (테스트용) - 실제 스키마에 맞춤
        const dummyData: BacktestRecord[] = [
          {
            id: '1',
            strategy_name: '골든크로스 전략',
            created_at: '2024-01-15T10:30:00',
            start_date: '2023-01-01',
            end_date: '2023-12-31',
            initial_capital: 10000000,
            final_capital: 11550000,
            total_return: 15.5,
            max_drawdown: -8.3,
            win_rate: 65.2,
            sharpe_ratio: 1.45,
            total_trades: 48,
            profitable_trades: 31,
            winning_trades: 31,
            losing_trades: 17,
            profit_factor: 1.8,
            visible: true,
          },
          {
            id: '2',
            strategy_name: 'RSI 전략',
            created_at: '2024-01-14T14:20:00',
            start_date: '2023-01-01',
            end_date: '2023-12-31',
            initial_capital: 10000000,
            final_capital: 11230000,
            total_return: 12.3,
            max_drawdown: -6.5,
            win_rate: 58.7,
            sharpe_ratio: 1.23,
            total_trades: 62,
            profitable_trades: 36,
            winning_trades: 36,
            losing_trades: 26,
            profit_factor: 1.5,
            visible: true,
          },
          {
            id: '3',
            strategy_name: '볼린저밴드 + MACD',
            created_at: '2024-01-13T09:15:00',
            start_date: '2023-01-01',
            end_date: '2023-12-31',
            initial_capital: 10000000,
            final_capital: 11870000,
            total_return: 18.7,
            max_drawdown: -10.2,
            win_rate: 61.4,
            sharpe_ratio: 1.56,
            total_trades: 35,
            profitable_trades: 21,
            winning_trades: 21,
            losing_trades: 14,
            profit_factor: 2.1,
            visible: true,
          },
        ];
        
        setRecords(dummyData.map((d, i) => ({ ...d, color: COLORS[i % COLORS.length] })));
      } else {
        // 실제 데이터 포맷팅 - 실제 스키마에 맞춤
        const formattedData = (data || []).map((item, index) => ({
          id: item.id,
          strategy_name: item.strategy_name || '알 수 없음',
          created_at: item.created_at,
          start_date: item.start_date,
          end_date: item.end_date,
          initial_capital: Number(item.initial_capital) || 0,
          final_capital: Number(item.final_capital) || 0,
          total_return: Number(item.total_return) || 0,
          max_drawdown: Number(item.max_drawdown) || 0,
          win_rate: Number(item.win_rate) || 0,
          sharpe_ratio: Number(item.sharpe_ratio) || 0,
          total_trades: item.total_trades || 0,
          profitable_trades: item.profitable_trades || 0,
          winning_trades: item.winning_trades || item.profitable_trades || 0,
          losing_trades: item.losing_trades || 0,
          avg_profit: Number(item.avg_profit) || 0,
          avg_loss: Number(item.avg_loss) || 0,
          profit_factor: Number(item.profit_factor) || 0,
          recovery_factor: Number(item.recovery_factor) || 0,
          results_data: item.results_data,
          trade_details: item.trade_details,
          daily_returns: item.daily_returns,
          visible: true,
          color: COLORS[index % COLORS.length],
        }));
        
        setRecords(formattedData);
      }
    } catch (error) {
      console.error('Error loading backtest records:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...records];

    // 검색어 필터
    if (searchTerm) {
      filtered = filtered.filter(record =>
        record.strategy_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // 날짜 필터
    if (dateFilter.startDate) {
      filtered = filtered.filter(record =>
        record.created_at >= dateFilter.startDate
      );
    }
    if (dateFilter.endDate) {
      filtered = filtered.filter(record =>
        record.created_at <= dateFilter.endDate
      );
    }

    // 정렬
    filtered.sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      const comparison = aVal > bVal ? 1 : -1;
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    setFilteredRecords(filtered);
  };

  const handleSelectRecord = (record: BacktestRecord) => {
    const isSelected = selectedRecords.some(r => r.id === record.id);
    
    if (isSelected) {
      setSelectedRecords(selectedRecords.filter(r => r.id !== record.id));
    } else {
      if (selectedRecords.length < 4) {
        setSelectedRecords([...selectedRecords, record]);
      } else {
        alert('최대 4개까지 비교할 수 있습니다.');
      }
    }
  };

  const handleToggleVisibility = (recordId: string) => {
    setRecords(records.map(r =>
      r.id === recordId ? { ...r, visible: !r.visible } : r
    ));
  };

  const handleDeleteRecord = async (recordId: string) => {
    if (!confirm('이 백테스트 결과를 삭제하시겠습니까?')) {
      return;
    }

    try {
      const { error } = await supabase
        .from('backtest_results')
        .delete()
        .eq('id', recordId);

      if (error) {
        console.error('Error deleting record:', error);
      } else {
        setRecords(records.filter(r => r.id !== recordId));
        setSelectedRecords(selectedRecords.filter(r => r.id !== recordId));
      }
    } catch (error) {
      console.error('Error deleting record:', error);
    }
  };

  // 비교 차트 데이터 생성
  const getComparisonChartData = () => {
    const visibleRecords = selectedRecords.filter(r => r.visible);
    
    if (chartType === 'radar') {
      return {
        labels: ['수익률', '승률', '샤프비율', '최대낙폭', '거래횟수'],
        datasets: visibleRecords.map(record => ({
          label: record.strategy_name,
          data: [
            record.total_return,
            record.win_rate,
            record.sharpe_ratio * 20,
            Math.abs(record.max_drawdown),
            record.total_trades / 2,
          ],
          backgroundColor: `${record.color}33`,
          borderColor: record.color,
          borderWidth: 2,
        })),
      };
    } else {
      const metrics = ['total_return', 'win_rate', 'sharpe_ratio', 'max_drawdown'];
      return {
        labels: metrics.map(m => {
          switch (m) {
            case 'total_return': return '총 수익률';
            case 'win_rate': return '승률';
            case 'sharpe_ratio': return '샤프 비율';
            case 'max_drawdown': return '최대 낙폭';
            default: return m;
          }
        }),
        datasets: visibleRecords.map(record => ({
          label: record.strategy_name,
          data: [
            record.total_return,
            record.win_rate,
            record.sharpe_ratio * 10,
            Math.abs(record.max_drawdown),
          ],
          backgroundColor: chartType === 'bar' ? `${record.color}99` : record.color,
          borderColor: record.color,
          borderWidth: 2,
          tension: 0.1,
          fill: chartType === 'line',
        })),
      };
    }
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '백테스트 결과 비교',
      },
    },
    scales: chartType !== 'radar' ? {
      y: {
        beginAtZero: true,
      },
    } : undefined,
  };

  return (
    <Box>
      {/* 헤더 */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          백테스트 결과 비교 분석
        </Typography>
        <Typography variant="body2" color="text.secondary">
          과거 백테스트 결과들을 비교하고 분석할 수 있습니다. 최대 4개까지 동시 비교가 가능합니다.
        </Typography>
      </Box>

      {/* 필터 및 검색 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="전략명 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>정렬 기준</InputLabel>
                <Select
                  value={sortBy}
                  label="정렬 기준"
                  onChange={(e) => setSortBy(e.target.value as keyof BacktestRecord)}
                >
                  <MenuItem value="created_at">실행 날짜</MenuItem>
                  <MenuItem value="total_return">총 수익률</MenuItem>
                  <MenuItem value="win_rate">승률</MenuItem>
                  <MenuItem value="sharpe_ratio">샤프 비율</MenuItem>
                  <MenuItem value="max_drawdown">최대 낙폭</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <ToggleButtonGroup
                value={sortOrder}
                exclusive
                onChange={(e, value) => value && setSortOrder(value)}
                fullWidth
              >
                <ToggleButton value="asc">오름차순</ToggleButton>
                <ToggleButton value="desc">내림차순</ToggleButton>
              </ToggleButtonGroup>
            </Grid>
            <Grid item xs={12} md={3}>
              <Stack direction="row" spacing={1}>
                <Chip
                  label={`${filteredRecords.length}개 결과`}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={`${selectedRecords.length}개 선택`}
                  color="secondary"
                  variant={selectedRecords.length > 0 ? 'filled' : 'outlined'}
                />
              </Stack>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* 뷰 모드 선택 */}
      <Box sx={{ mb: 2 }}>
        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={(e, value) => value && setViewMode(value)}
          sx={{ mb: 2 }}
        >
          <ToggleButton value="table">
            <TableChart sx={{ mr: 1 }} />
            테이블 뷰
          </ToggleButton>
          <ToggleButton value="chart" disabled={selectedRecords.length === 0}>
            <BarChart sx={{ mr: 1 }} />
            차트 비교
          </ToggleButton>
          <ToggleButton value="detail" disabled={selectedRecords.length === 0}>
            <Assessment sx={{ mr: 1 }} />
            상세 분석
          </ToggleButton>
        </ToggleButtonGroup>

        {viewMode === 'chart' && (
          <ToggleButtonGroup
            value={chartType}
            exclusive
            onChange={(e, value) => value && setChartType(value)}
            sx={{ ml: 2 }}
          >
            <ToggleButton value="line">라인</ToggleButton>
            <ToggleButton value="bar">막대</ToggleButton>
            <ToggleButton value="radar">레이더</ToggleButton>
          </ToggleButtonGroup>
        )}
      </Box>

      {/* 메인 콘텐츠 */}
      {viewMode === 'table' && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">선택</TableCell>
                <TableCell>전략명</TableCell>
                <TableCell>실행일</TableCell>
                <TableCell>기간</TableCell>
                <TableCell align="right">총 수익률</TableCell>
                <TableCell align="right">연간 수익률</TableCell>
                <TableCell align="right">승률</TableCell>
                <TableCell align="right">최대 낙폭</TableCell>
                <TableCell align="right">샤프 비율</TableCell>
                <TableCell align="right">거래 횟수</TableCell>
                <TableCell align="center">액션</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredRecords.map((record) => {
                const isSelected = selectedRecords.some(r => r.id === record.id);
                return (
                  <TableRow
                    key={record.id}
                    selected={isSelected}
                    hover
                    onClick={() => handleSelectRecord(record)}
                    sx={{ cursor: 'pointer', opacity: record.visible ? 1 : 0.5 }}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={isSelected}
                        color="primary"
                        onClick={(e) => e.stopPropagation()}
                      />
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Box
                          sx={{
                            width: 12,
                            height: 12,
                            borderRadius: '50%',
                            backgroundColor: record.color,
                          }}
                        />
                        <Typography>{record.strategy_name}</Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      {new Date(record.created_at).toLocaleDateString('ko-KR')}
                    </TableCell>
                    <TableCell>
                      {record.start_date} ~ {record.end_date}
                    </TableCell>
                    <TableCell align="right">
                      <Typography
                        color={record.total_return >= 0 ? 'success.main' : 'error.main'}
                        fontWeight="bold"
                      >
                        {record.total_return >= 0 ? '+' : ''}{(record.total_return || 0).toFixed(2)}%
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      {(record.annual_return || record.total_return || 0).toFixed(2)}%
                    </TableCell>
                    <TableCell align="right">
                      {(record.win_rate || 0).toFixed(1)}%
                    </TableCell>
                    <TableCell align="right">
                      <Typography color="error.main">
                        {(record.max_drawdown || 0).toFixed(2)}%
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      {(record.sharpe_ratio || 0).toFixed(2)}
                    </TableCell>
                    <TableCell align="right">
                      {record.total_trades}
                    </TableCell>
                    <TableCell align="center">
                      <Stack direction="row" spacing={0}>
                        <Tooltip title={record.visible ? '숨기기' : '보이기'}>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleVisibility(record.id);
                            }}
                          >
                            {record.visible ? <Visibility /> : <VisibilityOff />}
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="상세 보기">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedDetail(record);
                              setViewMode('detail');
                            }}
                          >
                            <Assessment />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="삭제">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteRecord(record.id);
                            }}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {viewMode === 'chart' && selectedRecords.length > 0 && (
        <Card>
          <CardContent>
            <Box sx={{ height: 400 }}>
              {chartType === 'line' && (
                <Line data={getComparisonChartData()} options={chartOptions} />
              )}
              {chartType === 'bar' && (
                <Bar data={getComparisonChartData()} options={chartOptions} />
              )}
              {chartType === 'radar' && (
                <Radar data={getComparisonChartData()} options={chartOptions} />
              )}
            </Box>
          </CardContent>
        </Card>
      )}

      {viewMode === 'detail' && selectedRecords.length > 0 && (
        <Grid container spacing={2}>
          {selectedRecords.map((record) => (
            <Grid item xs={12} lg={selectedRecords.length > 1 ? 6 : 12} key={record.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {record.strategy_name}
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  {record.results ? (
                    <BacktestResultViewer result={record.results} />
                  ) : (
                    <Alert severity="info">
                      상세 결과를 불러오는 중...
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* 비교 요약 카드 */}
      {selectedRecords.length > 1 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              비교 요약
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  최고 수익률
                </Typography>
                <Typography variant="h6">
                  {Math.max(...selectedRecords.map(r => r.total_return || 0)).toFixed(2)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {selectedRecords.find(r => 
                    r.total_return === Math.max(...selectedRecords.map(r => r.total_return))
                  )?.strategy_name}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  평균 수익률
                </Typography>
                <Typography variant="h6">
                  {(selectedRecords.reduce((sum, r) => sum + (r.total_return || 0), 0) / selectedRecords.length).toFixed(2)}%
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  최고 승률
                </Typography>
                <Typography variant="h6">
                  {Math.max(...selectedRecords.map(r => r.win_rate || 0)).toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {selectedRecords.find(r => 
                    r.win_rate === Math.max(...selectedRecords.map(r => r.win_rate))
                  )?.strategy_name}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  최고 샤프 비율
                </Typography>
                <Typography variant="h6">
                  {Math.max(...selectedRecords.map(r => r.sharpe_ratio || 0)).toFixed(2)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {selectedRecords.find(r => 
                    r.sharpe_ratio === Math.max(...selectedRecords.map(r => r.sharpe_ratio))
                  )?.strategy_name}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* 데이터 없음 표시 */}
      {!loading && filteredRecords.length === 0 && (
        <Alert severity="info">
          백테스트 결과가 없습니다. 백테스트를 실행한 후 결과를 확인할 수 있습니다.
        </Alert>
      )}
    </Box>
  );
};

export default BacktestComparison;