import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  Chip,
  Stack,
  Divider,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { ko } from 'date-fns/locale';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { BacktestService } from '../services/backtestService';
import { supabase } from '../lib/supabase';
import { Link } from '@mui/material';

interface Strategy {
  id: string;
  name: string;
  description: string;
  type: string;
  parameters: any;
  created_at?: string;
}

interface BacktestConfig {
  strategyId: string;
  startDate: Date | null;
  endDate: Date | null;
  initialCapital: number;
  commission: number;
  slippage: number;
  dataInterval: string;
  stockCodes: string[];
}

export const BacktestRunner: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [backtestId, setBacktestId] = useState<string | null>(null);
  
  const [config, setConfig] = useState<BacktestConfig>({
    strategyId: '',
    startDate: new Date(new Date().setFullYear(new Date().getFullYear() - 1)),
    endDate: new Date(),
    initialCapital: 10000000,
    commission: 0.00015,
    slippage: 0.001,
    dataInterval: '1d',
    stockCodes: [],
  });

  // 전략 목록 로드 및 URL 파라미터 처리
  React.useEffect(() => {
    loadStrategies();
    
    // URL에서 strategyId 파라미터 가져오기
    const urlParams = new URLSearchParams(window.location.search);
    const strategyIdFromUrl = urlParams.get('strategyId');
    if (strategyIdFromUrl) {
      setConfig({ ...config, strategyId: strategyIdFromUrl });
    }
  }, []);

  const loadStrategies = async () => {
    try {
      const { data, error } = await supabase
        .from('strategies')
        .select('*')
        .eq('is_active', true)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      
      // 전략 데이터 형식 변환 (config 컬럼 사용)
      const formattedStrategies = data?.map(s => ({
        id: s.id,
        name: s.name,
        description: s.description || '',
        type: s.config?.strategy_type || s.type || 'custom',  // config 내 strategy_type 사용
        parameters: s.config || s.parameters || {},  // config 컬럼 우선 사용
        created_at: s.created_at
      })) || [];
      
      setStrategies(formattedStrategies);
      
      // URL에 strategyId가 있으면 해당 전략 선택
      const urlParams = new URLSearchParams(window.location.search);
      const strategyIdFromUrl = urlParams.get('strategyId');
      if (strategyIdFromUrl && formattedStrategies.some(s => s.id === strategyIdFromUrl)) {
        setConfig(prev => ({ ...prev, strategyId: strategyIdFromUrl }));
      }
    } catch (err) {
      console.error('전략 로드 실패:', err);
      setError('전략 목록을 불러올 수 었습니다.');
    }
  };

  const runBacktest = async () => {
    if (!config.strategyId || !config.startDate || !config.endDate) {
      setError('필수 항목을 모두 입력해주세요.');
      return;
    }

    setIsRunning(true);
    setError(null);
    setSuccess(null);
    setProgress(0);

    try {
      // 백테스트 실행 요청
      const response = await fetch('/api/backtest/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_id: config.strategyId,
          start_date: config.startDate.toISOString().split('T')[0],
          end_date: config.endDate.toISOString().split('T')[0],
          initial_capital: config.initialCapital,
          commission: config.commission,
          slippage: config.slippage,
          data_interval: config.dataInterval,
          stock_codes: config.stockCodes.length > 0 ? config.stockCodes : undefined,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || '백테스트 실행 실패');
      }

      setBacktestId(result.backtest_id);
      
      // 진행 상황 모니터링
      const subscription = BacktestService.subscribeToBacktestProgress(
        result.backtest_id,
        (progress) => {
          setProgress(progress.progress || 0);
          if (progress.status === 'completed') {
            setSuccess('백테스트가 성공적으로 완료되었습니다.');
            setIsRunning(false);
            subscription.unsubscribe();
          } else if (progress.status === 'failed') {
            setError(progress.error || '백테스트 실행 중 오류가 발생했습니다.');
            setIsRunning(false);
            subscription.unsubscribe();
          }
        }
      );
    } catch (err: any) {
      setError(err.message || '백테스트 실행 중 오류가 발생했습니다.');
      setIsRunning(false);
    }
  };

  const stopBacktest = async () => {
    if (!backtestId) return;

    try {
      const response = await fetch(`/api/backtest/stop/${backtestId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('백테스트 중단 실패');
      }

      setIsRunning(false);
      setProgress(0);
      setSuccess('백테스트가 중단되었습니다.');
    } catch (err: any) {
      setError(err.message || '백테스트 중단 중 오류가 발생했습니다.');
    }
  };

  const viewResults = () => {
    if (backtestId) {
      window.location.href = `/backtest/results/${backtestId}`;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          백테스트 실행
        </Typography>
        <Typography variant="body2" color="text.secondary">
          전략빌더에서 생성한 전략을 선택하여 백테스트를 실행할 수 있습니다.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Grid container spacing={3}>
            {/* 전략 선택 */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>전략 선택</InputLabel>
                <Select
                  value={config.strategyId}
                  onChange={(e) => setConfig({ ...config, strategyId: e.target.value })}
                  disabled={isRunning}
                >
                  <MenuItem value="">
                    <em>전략을 선택하세요</em>
                  </MenuItem>
                  {strategies.length === 0 ? (
                    <MenuItem disabled>
                      <em>저장된 전략이 없습니다. 전략빌더에서 생성해주세요.</em>
                    </MenuItem>
                  ) : (
                    strategies.map((strategy) => (
                      <MenuItem key={strategy.id} value={strategy.id}>
                        <Box>
                          <Typography>{strategy.name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {strategy.type} | {strategy.description?.substring(0, 50)}
                            {strategy.created_at && ` | ${new Date(strategy.created_at).toLocaleDateString('ko-KR')}`}
                          </Typography>
                        </Box>
                      </MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
            </Grid>

            {/* 데이터 간격 */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>데이터 간격</InputLabel>
                <Select
                  value={config.dataInterval}
                  onChange={(e) => setConfig({ ...config, dataInterval: e.target.value })}
                  disabled={isRunning}
                >
                  <MenuItem value="1m">1분</MenuItem>
                  <MenuItem value="5m">5분</MenuItem>
                  <MenuItem value="15m">15분</MenuItem>
                  <MenuItem value="30m">30분</MenuItem>
                  <MenuItem value="1h">1시간</MenuItem>
                  <MenuItem value="1d">1일</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* 기간 설정 */}
            <Grid item xs={12} md={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ko}>
                <DatePicker
                  label="시작일"
                  value={config.startDate}
                  onChange={(date: any) => setConfig({ ...config, startDate: date })}
                  disabled={isRunning}
                  sx={{ width: '100%' }}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12} md={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ko}>
                <DatePicker
                  label="종료일"
                  value={config.endDate}
                  onChange={(date: any) => setConfig({ ...config, endDate: date })}
                  disabled={isRunning}
                  sx={{ width: '100%' }}
                />
              </LocalizationProvider>
            </Grid>

            {/* 자본금 설정 */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="초기 자본금"
                type="number"
                value={config.initialCapital}
                onChange={(e) => setConfig({ ...config, initialCapital: Number(e.target.value) })}
                disabled={isRunning}
                InputProps={{
                  endAdornment: '원',
                }}
              />
            </Grid>

            {/* 수수료 */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="수수료율"
                type="number"
                value={config.commission}
                onChange={(e) => setConfig({ ...config, commission: Number(e.target.value) })}
                disabled={isRunning}
                InputProps={{
                  endAdornment: '%',
                }}
                helperText="거래금액 대비 수수료율"
              />
            </Grid>

            {/* 슬리피지 */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="슬리피지"
                type="number"
                value={config.slippage}
                onChange={(e) => setConfig({ ...config, slippage: Number(e.target.value) })}
                disabled={isRunning}
                InputProps={{
                  endAdornment: '%',
                }}
                helperText="예상 체결가와 실제 체결가의 차이"
              />
            </Grid>

            {/* 종목 코드 입력 */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="종목 코드 (선택사항)"
                placeholder="005930, 000660, 035720 (쉼표로 구분)"
                value={config.stockCodes.join(', ')}
                onChange={(e) => {
                  const codes = e.target.value
                    .split(',')
                    .map(code => code.trim())
                    .filter(code => code.length > 0);
                  setConfig({ ...config, stockCodes: codes });
                }}
                disabled={isRunning}
                helperText="비어있으면 전체 종목을 대상으로 백테스트 실행"
              />
            </Grid>

            {/* 진행 상황 */}
            {isRunning && (
              <Grid item xs={12}>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    백테스트 진행 중... {progress}%
                  </Typography>
                  <LinearProgress variant="determinate" value={progress} />
                </Box>
              </Grid>
            )}

            {/* 실행 버튼 */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Stack direction="row" spacing={2} justifyContent="flex-end">
                {!isRunning ? (
                  <>
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={<PlayArrowIcon />}
                      onClick={runBacktest}
                      disabled={!config.strategyId}
                    >
                      백테스트 실행
                    </Button>
                    {backtestId && (
                      <Button
                        variant="outlined"
                        size="large"
                        startIcon={<AssessmentIcon />}
                        onClick={viewResults}
                      >
                        결과 보기
                      </Button>
                    )}
                  </>
                ) : (
                  <Button
                    variant="contained"
                    color="error"
                    size="large"
                    startIcon={<StopIcon />}
                    onClick={stopBacktest}
                  >
                    백테스트 중단
                  </Button>
                )}
              </Stack>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* 전략이 없을 때 안내 */}
      {strategies.length === 0 && (
        <Card sx={{ mt: 2 }}>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" gutterBottom>
              아직 저장된 전략이 없습니다
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              전략빌더에서 새로운 전략을 만들어 저장한 후 백테스트를 실행할 수 있습니다.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              href="/strategy-builder"
              startIcon={<AssessmentIcon />}
            >
              전략빌더로 이동
            </Button>
          </CardContent>
        </Card>
      )}

      {/* 전략 정보 표시 */}
      {config.strategyId && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              선택한 전략 정보
            </Typography>
            {strategies
              .filter(s => s.id === config.strategyId)
              .map(strategy => (
                <Box key={strategy.id}>
                  <Typography variant="body1" gutterBottom>
                    <strong>{strategy.name}</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {strategy.description}
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Chip label={strategy.type} size="small" color="primary" />
                    {strategy.parameters && Object.keys(strategy.parameters)
                      .filter(key => typeof strategy.parameters[key] !== 'object')
                      .slice(0, 5)
                      .map(key => (
                        <Chip 
                          key={key}
                          label={`${key}: ${strategy.parameters[key]}`}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    {Object.keys(strategy.parameters || {}).length > 5 && (
                      <Chip 
                        label={`+${Object.keys(strategy.parameters).length - 5} more`}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                    )}
                  </Stack>
                </Box>
              ))}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};