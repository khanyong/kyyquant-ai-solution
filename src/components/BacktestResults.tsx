import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
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
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SettingsIcon from '@mui/icons-material/Settings';
import FilterListIcon from '@mui/icons-material/FilterList';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import { BacktestService } from '../services/backtestService';

const BacktestResults: React.FC = () => {
  const { backtestId } = useParams<{ backtestId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [trades, setTrades] = useState<any[]>([]);

  useEffect(() => {
    loadBacktestResults();
  }, [backtestId]);

  const loadBacktestResults = async () => {
    if (!backtestId) {
      setError('백테스트 ID가 없습니다.');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      
      // 백테스트 결과 조회
      const resultData = await BacktestService.getBacktestDetail(backtestId);
      setResult(resultData);
      
      // 거래 내역 조회
      const tradesData = await BacktestService.getBacktestTrades(backtestId);
      console.log('Trades data from service:', tradesData);
      setTrades(tradesData || []);
      
    } catch (err: any) {
      console.error('Failed to load backtest results:', err);
      setError('백테스트 결과를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

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
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/backtest')}
          sx={{ mt: 2 }}
        >
          백테스트로 돌아가기
        </Button>
      </Box>
    );
  }

  if (!result) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">백테스트 결과가 없습니다.</Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/backtest')}
          sx={{ mt: 2 }}
        >
          백테스트로 돌아가기
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/backtest')}
          sx={{ mb: 2 }}
        >
          백테스트로 돌아가기
        </Button>
        
        <Typography variant="h4" gutterBottom>
          백테스트 결과
        </Typography>
        
        {result.strategy_name && (
          <Typography variant="subtitle1" color="text.secondary">
            전략: {result.strategy_name}
          </Typography>
        )}
      </Box>

      {/* 주요 지표 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                총 수익률
              </Typography>
              <Typography variant="h4" component="div" color={result.total_return_rate >= 0 ? 'success.main' : 'error.main'}>
                {result.total_return_rate >= 0 ? '+' : ''}{result.total_return_rate?.toFixed(2)}%
                {result.total_return_rate >= 0 ? <TrendingUpIcon /> : <TrendingDownIcon />}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                승률
              </Typography>
              <Typography variant="h4" component="div">
                {result.win_rate?.toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                최대 손실
              </Typography>
              <Typography variant="h4" component="div" color="error.main">
                {result.max_drawdown?.toFixed(2)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                총 거래 수
              </Typography>
              <Typography variant="h4" component="div">
                {result.total_trades}회
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 백테스트 설정 정보 */}
      <Box sx={{ mb: 3 }}>
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <SettingsIcon sx={{ mr: 1 }} />
            <Typography variant="h6">백테스트 설정</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="text.secondary">데이터 간격</Typography>
                <Typography variant="body1">
                  {result.results_data?.backtest_config?.data_interval === '1d' && '일봉 (Daily)'}
                  {result.results_data?.backtest_config?.data_interval === '1w' && '주봉 (Weekly)'}
                  {result.results_data?.backtest_config?.data_interval === '1M' && '월봉 (Monthly)'}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="text.secondary">수수료</Typography>
                <Typography variant="body1">
                  {((result.results_data?.backtest_config?.commission || 0) * 100).toFixed(3)}%
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="text.secondary">슬리피지</Typography>
                <Typography variant="body1">
                  {((result.results_data?.backtest_config?.slippage || 0) * 100).toFixed(2)}%
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="text.secondary">전략 유형</Typography>
                <Typography variant="body1">
                  {result.results_data?.backtest_config?.strategy_type || 'N/A'}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="text.secondary">종목 수</Typography>
                <Typography variant="body1">
                  {result.results_data?.backtest_config?.total_stocks || 0}개
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="text.secondary">필터링 모드</Typography>
                <Typography variant="body1">
                  {result.results_data?.backtest_config?.filtering_mode === 'filtering' && '필터링 모드'}
                  {result.results_data?.backtest_config?.filtering_mode === 'staged' && '단계별 전략'}
                  {!result.results_data?.backtest_config?.filtering_mode && 'N/A'}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">백테스트 종목</Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {result.results_data?.backtest_config?.stock_codes?.join(', ') || '종목 정보 없음'}
                  {result.results_data?.backtest_config?.total_stocks > 20 && 
                    ` ... 외 ${result.results_data.backtest_config.total_stocks - 20}개`}
                </Typography>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* 투자 필터 설정 */}
        {result.results_data?.backtest_config?.filter_rules && (
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <FilterListIcon sx={{ mr: 1 }} />
              <Typography variant="h6">투자 유니버스 필터</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {/* 가치지표 */}
                {result.results_data.backtest_config.filter_rules.valuation && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>가치지표</Typography>
                    <List dense>
                      {result.results_data.backtest_config.filter_rules.valuation.marketCap && (
                        <ListItem>
                          <ListItemText 
                            primary="시가총액"
                            secondary={`${result.results_data.backtest_config.filter_rules.valuation.marketCap[0]} ~ ${result.results_data.backtest_config.filter_rules.valuation.marketCap[1]} 억원`}
                          />
                        </ListItem>
                      )}
                      {result.results_data.backtest_config.filter_rules.valuation.per && (
                        <ListItem>
                          <ListItemText 
                            primary="PER"
                            secondary={`${result.results_data.backtest_config.filter_rules.valuation.per[0]} ~ ${result.results_data.backtest_config.filter_rules.valuation.per[1]}`}
                          />
                        </ListItem>
                      )}
                      {result.results_data.backtest_config.filter_rules.valuation.pbr && (
                        <ListItem>
                          <ListItemText 
                            primary="PBR"
                            secondary={`${result.results_data.backtest_config.filter_rules.valuation.pbr[0]} ~ ${result.results_data.backtest_config.filter_rules.valuation.pbr[1]}`}
                          />
                        </ListItem>
                      )}
                    </List>
                  </Grid>
                )}
                
                {/* 재무지표 */}
                {result.results_data.backtest_config.filter_rules.financial && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>재무지표</Typography>
                    <List dense>
                      {result.results_data.backtest_config.filter_rules.financial.roe && (
                        <ListItem>
                          <ListItemText 
                            primary="ROE"
                            secondary={`${result.results_data.backtest_config.filter_rules.financial.roe[0]} ~ ${result.results_data.backtest_config.filter_rules.financial.roe[1]}%`}
                          />
                        </ListItem>
                      )}
                      {result.results_data.backtest_config.filter_rules.financial.debtRatio && (
                        <ListItem>
                          <ListItemText 
                            primary="부채비율"
                            secondary={`${result.results_data.backtest_config.filter_rules.financial.debtRatio[0]} ~ ${result.results_data.backtest_config.filter_rules.financial.debtRatio[1]}%`}
                          />
                        </ListItem>
                      )}
                    </List>
                  </Grid>
                )}
                
                {/* 섹터 필터 */}
                {result.results_data.backtest_config.filter_rules.sector && 
                 result.results_data.backtest_config.filter_rules.sector.selectedSectors && 
                 result.results_data.backtest_config.filter_rules.sector.selectedSectors.length > 0 && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" gutterBottom>선택된 섹터</Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {result.results_data.backtest_config.filter_rules.sector.selectedSectors.map((sector: string) => (
                        <Chip key={sector} label={sector} size="small" />
                      ))}
                    </Box>
                  </Grid>
                )}
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}

        {/* 전략 조건 */}
        {result.results_data?.backtest_config?.strategy_config && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <ShowChartIcon sx={{ mr: 1 }} />
              <Typography variant="h6">전략 조건</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>매수 조건</Typography>
                  <List dense>
                    {result.results_data.backtest_config.strategy_config.buyConditions?.map((condition: any, index: number) => {
                      // 조건 텍스트 포맷팅
                      let conditionText = '';
                      if (condition.indicator) {
                        conditionText = condition.indicator;
                        if (condition.period) {
                          conditionText += `(${condition.period})`;
                        }
                        if (condition.operator) {
                          const operatorText: { [key: string]: string } = {
                            '>': ' >',
                            '<': ' <',
                            '>=': ' ≥',
                            '<=': ' ≤',
                            '==': ' =',
                            'crosses_above': ' 상향돌파',
                            'crosses_below': ' 하향돌파'
                          };
                          conditionText += operatorText[condition.operator] || ` ${condition.operator}`;
                        }
                        if (condition.value !== undefined && condition.value !== null) {
                          conditionText += ` ${condition.value}`;
                        }
                        if (condition.compareIndicator) {
                          conditionText += ` ${condition.compareIndicator}`;
                          if (condition.comparePeriod) {
                            conditionText += `(${condition.comparePeriod})`;
                          }
                        }
                      } else {
                        conditionText = JSON.stringify(condition);
                      }
                      
                      return (
                        <ListItem key={index}>
                          <ListItemText primary={conditionText} />
                        </ListItem>
                      );
                    })}
                    {(!result.results_data.backtest_config.strategy_config.buyConditions || 
                      result.results_data.backtest_config.strategy_config.buyConditions.length === 0) && (
                      <ListItem>
                        <ListItemText primary="조건 없음" />
                      </ListItem>
                    )}
                  </List>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>매도 조건</Typography>
                  <List dense>
                    {result.results_data.backtest_config.strategy_config.sellConditions?.map((condition: any, index: number) => {
                      // 조건 텍스트 포맷팅
                      let conditionText = '';
                      if (condition.indicator) {
                        conditionText = condition.indicator;
                        if (condition.period) {
                          conditionText += `(${condition.period})`;
                        }
                        if (condition.operator) {
                          const operatorText: { [key: string]: string } = {
                            '>': ' >',
                            '<': ' <',
                            '>=': ' ≥',
                            '<=': ' ≤',
                            '==': ' =',
                            'crosses_above': ' 상향돌파',
                            'crosses_below': ' 하향돌파'
                          };
                          conditionText += operatorText[condition.operator] || ` ${condition.operator}`;
                        }
                        if (condition.value !== undefined && condition.value !== null) {
                          conditionText += ` ${condition.value}`;
                        }
                        if (condition.compareIndicator) {
                          conditionText += ` ${condition.compareIndicator}`;
                          if (condition.comparePeriod) {
                            conditionText += `(${condition.comparePeriod})`;
                          }
                        }
                      } else {
                        conditionText = JSON.stringify(condition);
                      }
                      
                      return (
                        <ListItem key={index}>
                          <ListItemText primary={conditionText} />
                        </ListItem>
                      );
                    })}
                    {(!result.results_data.backtest_config.strategy_config.sellConditions || 
                      result.results_data.backtest_config.strategy_config.sellConditions.length === 0) && (
                      <ListItem>
                        <ListItemText primary="조건 없음" />
                      </ListItem>
                    )}
                  </List>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}
      </Box>

      {/* 상세 정보 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                투자 정보
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography color="text.secondary">기간</Typography>
                <Typography>
                  {new Date(result.start_date).toLocaleDateString()} ~ {new Date(result.end_date).toLocaleDateString()}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography color="text.secondary">초기 자본</Typography>
                <Typography>₩{result.initial_capital?.toLocaleString()}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography color="text.secondary">최종 자본</Typography>
                <Typography>₩{result.final_capital?.toLocaleString()}</Typography>
              </Box>
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
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography color="text.secondary">수익 거래</Typography>
                <Typography>{result.profitable_trades || 0}회</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography color="text.secondary">손실 거래</Typography>
                <Typography>{result.losing_trades || 0}회</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography color="text.secondary">샤프 비율</Typography>
                <Typography>{result.sharpe_ratio?.toFixed(2) || 'N/A'}</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 거래 내역 */}
      {trades.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              거래 내역
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>날짜</TableCell>
                    <TableCell>종목코드</TableCell>
                    <TableCell>종목명</TableCell>
                    <TableCell>거래</TableCell>
                    <TableCell>매매 이유</TableCell>
                    <TableCell align="right">가격</TableCell>
                    <TableCell align="right">수량</TableCell>
                    <TableCell align="right">금액</TableCell>
                    <TableCell align="right">손익</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {trades.map((trade, index) => (
                    <TableRow key={index}>
                      <TableCell>{new Date(trade.trade_date || trade.date).toLocaleDateString()}</TableCell>
                      <TableCell>{trade.stock_code}</TableCell>
                      <TableCell>{trade.stock_name || trade.stock_code}</TableCell>
                      <TableCell>
                        <Chip
                          label={trade.action === 'buy' ? '매수' : trade.action === 'sell' ? '매도' : trade.action.toUpperCase()}
                          size="small"
                          color={trade.action === 'buy' || trade.action === 'BUY' ? 'primary' : 'secondary'}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" style={{ maxWidth: 200, display: 'block' }}>
                          {trade.signal_reason || '-'}
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
                            sx={{ mt: 0.5 }}
                          />
                        )}
                      </TableCell>
                      <TableCell align="right">₩{trade.price?.toLocaleString()}</TableCell>
                      <TableCell align="right">{trade.quantity}</TableCell>
                      <TableCell align="right">₩{trade.amount?.toLocaleString()}</TableCell>
                      <TableCell align="right" sx={{
                        color: trade.profit_loss > 0 ? 'success.main' : trade.profit_loss < 0 ? 'error.main' : 'text.primary'
                      }}>
                        {trade.profit_loss ? `₩${trade.profit_loss.toLocaleString()}` : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default BacktestResults;