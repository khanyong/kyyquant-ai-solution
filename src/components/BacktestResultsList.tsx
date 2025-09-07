import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  PlayArrow as PlayArrowIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { BacktestService } from '../services/backtestService';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

interface BacktestResult {
  id: string;
  strategy_name: string;
  created_at: string;
  total_return: number;
  max_drawdown: number;
  total_trades: number;
  win_rate: number;
  sharpe_ratio: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  start_date: string;
  end_date: string;
}

const BacktestResultsList: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<BacktestResult[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    loadBacktestResults();
  }, []);

  const loadBacktestResults = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await BacktestService.getBacktestList();
      setResults(data || []);
      
    } catch (err: any) {
      console.error('Failed to load backtest results:', err);
      setError('백테스트 결과를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewResult = (resultId: string) => {
    navigate(`/backtest/results/${resultId}`);
  };

  const handleRunNewBacktest = () => {
    navigate('/backtest');
  };

  const handleDeleteResult = async (resultId: string) => {
    if (!window.confirm('이 백테스트 결과를 삭제하시겠습니까?')) {
      return;
    }

    try {
      await BacktestService.deleteBacktest(resultId);
      await loadBacktestResults();
    } catch (err: any) {
      console.error('Failed to delete backtest:', err);
      alert('백테스트 삭제에 실패했습니다.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'info';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '완료';
      case 'running':
        return '진행중';
      case 'failed':
        return '실패';
      case 'pending':
        return '대기중';
      default:
        return status;
    }
  };

  const filteredResults = results
    .filter(result => {
      if (statusFilter !== 'all' && result.status !== statusFilter) {
        return false;
      }
      if (searchTerm && !result.strategy_name.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
      return true;
    })
    .sort((a, b) => {
      let aValue: any = a[sortBy as keyof BacktestResult];
      let bValue: any = b[sortBy as keyof BacktestResult];
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
        <Button onClick={loadBacktestResults} sx={{ mt: 2 }}>
          다시 시도
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          백테스트 결과 목록
        </Typography>
        <Stack direction="row" spacing={2}>
          <Tooltip title="새로고침">
            <IconButton onClick={loadBacktestResults}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<PlayArrowIcon />}
            onClick={handleRunNewBacktest}
          >
            새 백테스트 실행
          </Button>
        </Stack>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" spacing={2}>
            <TextField
              fullWidth
              placeholder="전략명으로 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>상태</InputLabel>
              <Select
                value={statusFilter}
                label="상태"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="all">전체</MenuItem>
                <MenuItem value="completed">완료</MenuItem>
                <MenuItem value="running">진행중</MenuItem>
                <MenuItem value="failed">실패</MenuItem>
                <MenuItem value="pending">대기중</MenuItem>
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>정렬</InputLabel>
              <Select
                value={sortBy}
                label="정렬"
                onChange={(e) => setSortBy(e.target.value)}
              >
                <MenuItem value="created_at">생성일</MenuItem>
                <MenuItem value="total_return">수익률</MenuItem>
                <MenuItem value="max_drawdown">최대낙폭</MenuItem>
                <MenuItem value="win_rate">승률</MenuItem>
                <MenuItem value="sharpe_ratio">샤프비율</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </CardContent>
      </Card>

      {filteredResults.length === 0 ? (
        <Alert severity="info">
          {searchTerm || statusFilter !== 'all' 
            ? '검색 결과가 없습니다.' 
            : '아직 백테스트 결과가 없습니다. 새로운 백테스트를 실행해보세요.'}
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>전략명</TableCell>
                <TableCell>기간</TableCell>
                <TableCell align="right">총 수익률</TableCell>
                <TableCell align="right">최대 낙폭</TableCell>
                <TableCell align="right">승률</TableCell>
                <TableCell align="right">샤프비율</TableCell>
                <TableCell align="right">거래 횟수</TableCell>
                <TableCell>상태</TableCell>
                <TableCell>생성일</TableCell>
                <TableCell align="center">액션</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredResults.map((result) => (
                <TableRow key={result.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="bold">
                      {result.strategy_name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">
                      {format(new Date(result.start_date), 'yyyy.MM.dd', { locale: ko })} -
                      {format(new Date(result.end_date), 'yyyy.MM.dd', { locale: ko })}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={`${(result.total_return * 100).toFixed(2)}%`}
                      color={result.total_return >= 0 ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="error">
                      {(result.max_drawdown * 100).toFixed(2)}%
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      {(result.win_rate * 100).toFixed(1)}%
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      {result.sharpe_ratio.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      {result.total_trades}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusText(result.status)}
                      color={getStatusColor(result.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">
                      {format(new Date(result.created_at), 'yyyy.MM.dd HH:mm', { locale: ko })}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={1} justifyContent="center">
                      <Tooltip title="상세보기">
                        <IconButton
                          size="small"
                          onClick={() => handleViewResult(result.id)}
                          disabled={result.status !== 'completed'}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="삭제">
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteResult(result.id)}
                          color="error"
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default BacktestResultsList;