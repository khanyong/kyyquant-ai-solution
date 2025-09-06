import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  ToggleButtonGroup,
  ToggleButton,
  Alert,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Chip,
  Stack,
  Divider,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Badge,
  Tooltip
} from '@mui/material'
import {
  FilterList,
  TrendingUp,
  SwapHoriz,
  CheckCircle,
  Warning,
  Info,
  PlayArrow,
  Refresh,
  Timeline,
  Business,
  ShowChart,
  Assessment,
  ArrowForward,
  ArrowBack
} from '@mui/icons-material'
import { InvestmentFlowType, InvestmentFlow, TradingSignal } from '../types/investment'
import { supabase } from '../lib/supabase'

interface InvestmentFlowManagerProps {
  onFlowChange?: (flow: InvestmentFlowType) => void
  currentUniverse?: any
  currentStrategy?: any
}

const InvestmentFlowManager: React.FC<InvestmentFlowManagerProps> = ({
  onFlowChange,
  currentUniverse,
  currentStrategy
}) => {
  const [flowType, setFlowType] = useState<InvestmentFlowType>(InvestmentFlowType.FILTER_FIRST)
  const [activeStep, setActiveStep] = useState(0)
  const [tradingSignals, setTradingSignals] = useState<TradingSignal[]>([])
  const [universeStats, setUniverseStats] = useState({
    totalStocks: 0,
    filteredStocks: 0,
    activeStrategies: 0,
    pendingSignals: 0
  })
  const [isProcessing, setIsProcessing] = useState(false)

  // 흐름 1: 필터 우선 단계
  const filterFirstSteps = [
    {
      label: '투자 필터 설정',
      description: '시가총액, PER, PBR, ROE 등 재무지표 기준 설정',
      icon: <FilterList />,
      completed: currentUniverse?.financialFilters !== undefined
    },
    {
      label: '투자 유니버스 생성',
      description: '필터 조건에 맞는 종목 풀 생성',
      icon: <Business />,
      completed: universeStats.filteredStocks > 0
    },
    {
      label: '전략 설정',
      description: '기술적 지표 기반 매매 전략 구성',
      icon: <ShowChart />,
      completed: currentStrategy !== undefined
    },
    {
      label: '모니터링 & 매매',
      description: '유니버스 내 종목 모니터링 및 자동매매',
      icon: <Timeline />,
      completed: false
    }
  ]

  // 흐름 2: 전략 우선 단계
  const strategyFirstSteps = [
    {
      label: '전략 설정',
      description: '기술적 지표 기반 매매 전략 구성',
      icon: <ShowChart />,
      completed: currentStrategy !== undefined
    },
    {
      label: '전체 시장 스캔',
      description: '모든 종목에 대해 전략 조건 확인',
      icon: <Assessment />,
      completed: tradingSignals.length > 0
    },
    {
      label: '필터 검증',
      description: '신호 발생 종목의 재무지표 확인',
      icon: <FilterList />,
      completed: false
    },
    {
      label: '최종 매매 실행',
      description: '필터 통과 종목만 매매 실행',
      icon: <TrendingUp />,
      completed: false
    }
  ]

  const currentSteps = flowType === InvestmentFlowType.FILTER_FIRST ? filterFirstSteps : strategyFirstSteps

  useEffect(() => {
    loadUniverseStats()
    loadTradingSignals()
  }, [flowType])

  const loadUniverseStats = async () => {
    try {
      // 전체 종목 수 조회
      const { count: totalCount } = await supabase
        .from('kw_stock_list')
        .select('*', { count: 'exact', head: true })

      // 필터링된 종목 수 조회 (예시)
      if (currentUniverse?.financialFilters) {
        const { count: filteredCount } = await supabase
          .from('kw_stock_financials')
          .select('*', { count: 'exact', head: true })
          .gte('market_cap', currentUniverse.financialFilters.marketCap[0])
          .lte('market_cap', currentUniverse.financialFilters.marketCap[1])
          .gte('per', currentUniverse.financialFilters.per[0])
          .lte('per', currentUniverse.financialFilters.per[1])

        setUniverseStats(prev => ({
          ...prev,
          totalStocks: totalCount || 0,
          filteredStocks: filteredCount || 0
        }))
      } else {
        setUniverseStats(prev => ({
          ...prev,
          totalStocks: totalCount || 0
        }))
      }

      // 활성 전략 수 조회
      const { count: strategyCount } = await supabase
        .from('strategies')
        .select('*', { count: 'exact', head: true })
        .eq('is_active', true)

      setUniverseStats(prev => ({
        ...prev,
        activeStrategies: strategyCount || 0
      }))
    } catch (error) {
      console.error('Failed to load universe stats:', error)
    }
  }

  const loadTradingSignals = async () => {
    try {
      // 최근 거래 신호 조회 (예시)
      const { data: signals } = await supabase
        .from('trading_signals')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(10)

      if (signals) {
        setTradingSignals(signals.map(s => ({
          stockCode: s.stock_code,
          stockName: s.stock_name,
          signalType: s.signal_type,
          strategy: s.strategy_name,
          flowType: s.flow_type || flowType,
          passedFilters: s.passed_filters,
          confidence: s.confidence || 0,
          timestamp: new Date(s.created_at)
        })))

        setUniverseStats(prev => ({
          ...prev,
          pendingSignals: signals.filter(s => s.status === 'pending').length
        }))
      }
    } catch (error) {
      console.error('Failed to load trading signals:', error)
    }
  }

  const handleFlowTypeChange = (event: React.MouseEvent<HTMLElement>, newFlow: InvestmentFlowType | null) => {
    if (newFlow !== null) {
      setFlowType(newFlow)
      setActiveStep(0)
      if (onFlowChange) {
        onFlowChange(newFlow)
      }
    }
  }

  const handleStepClick = (step: number) => {
    setActiveStep(step)
  }

  const runFlowProcess = async () => {
    setIsProcessing(true)

    try {
      if (flowType === InvestmentFlowType.FILTER_FIRST) {
        // 흐름 1: 필터 → 유니버스 → 전략
        console.log('Running Filter-First Flow...')
        
        // 1. 필터링된 종목 조회
        // 2. 각 종목에 대해 전략 적용
        // 3. 신호 생성
        
      } else {
        // 흐름 2: 전략 → 스캔 → 필터
        console.log('Running Strategy-First Flow...')
        
        // 1. 모든 종목에 대해 전략 스캔
        // 2. 신호 발생 종목 필터링
        // 3. 필터 통과 종목만 최종 선택
      }

      await loadTradingSignals()
    } catch (error) {
      console.error('Flow process error:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SwapHoriz />
              투자 흐름 관리
            </Typography>
            <Typography variant="body2" color="textSecondary">
              투자 전략 실행 방식을 선택하고 관리합니다
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadUniverseStats}
              >
                새로고침
              </Button>
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={runFlowProcess}
                disabled={isProcessing}
              >
                실행
              </Button>
            </Stack>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        {/* 투자 흐름 선택 */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            투자 흐름 선택
          </Typography>
          <ToggleButtonGroup
            value={flowType}
            exclusive
            onChange={handleFlowTypeChange}
            fullWidth
            sx={{ mt: 2 }}
          >
            <ToggleButton value={InvestmentFlowType.FILTER_FIRST}>
              <Stack spacing={1} alignItems="center">
                <FilterList />
                <Typography variant="button">필터 우선</Typography>
                <Typography variant="caption" color="textSecondary">
                  필터 → 유니버스 → 전략
                </Typography>
              </Stack>
            </ToggleButton>
            <ToggleButton value={InvestmentFlowType.STRATEGY_FIRST}>
              <Stack spacing={1} alignItems="center">
                <ShowChart />
                <Typography variant="button">전략 우선</Typography>
                <Typography variant="caption" color="textSecondary">
                  전략 → 스캔 → 필터
                </Typography>
              </Stack>
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* 선택된 흐름 설명 */}
        <Alert 
          severity="info" 
          icon={<Info />}
          sx={{ mb: 3 }}
        >
          {flowType === InvestmentFlowType.FILTER_FIRST ? (
            <Box>
              <Typography variant="subtitle2" fontWeight="bold">
                필터 우선 흐름
              </Typography>
              <Typography variant="body2">
                재무지표 필터로 투자 유니버스를 먼저 생성한 후, 해당 종목들에 대해서만 전략을 적용합니다.
                안정적이고 보수적인 투자에 적합합니다.
              </Typography>
            </Box>
          ) : (
            <Box>
              <Typography variant="subtitle2" fontWeight="bold">
                전략 우선 흐름
              </Typography>
              <Typography variant="body2">
                전체 시장에서 기술적 신호를 먼저 찾은 후, 재무지표 필터로 검증합니다.
                적극적이고 기회 포착형 투자에 적합합니다.
              </Typography>
            </Box>
          )}
        </Alert>

        {/* 통계 카드 */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h4" color="primary">
                  {universeStats.totalStocks}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  전체 종목
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h4" color="success.main">
                  {universeStats.filteredStocks}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  필터 통과
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h4" color="warning.main">
                  {universeStats.activeStrategies}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  활성 전략
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h4" color="error.main">
                  {universeStats.pendingSignals}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  대기 신호
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {isProcessing && <LinearProgress sx={{ mb: 3 }} />}

        {/* 프로세스 단계 */}
        <Stepper activeStep={activeStep} orientation="vertical">
          {currentSteps.map((step, index) => (
            <Step key={step.label} completed={step.completed}>
              <StepLabel
                StepIconComponent={() => (
                  <IconButton 
                    color={step.completed ? 'success' : activeStep === index ? 'primary' : 'default'}
                    onClick={() => handleStepClick(index)}
                  >
                    {step.completed ? <CheckCircle /> : step.icon}
                  </IconButton>
                )}
              >
                <Typography variant="subtitle1">{step.label}</Typography>
              </StepLabel>
              <StepContent>
                <Typography variant="body2" color="textSecondary">
                  {step.description}
                </Typography>
                {activeStep === index && (
                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={step.completed ? <CheckCircle /> : <ArrowForward />}
                      disabled={isProcessing}
                    >
                      {step.completed ? '완료됨' : '실행'}
                    </Button>
                  </Box>
                )}
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* 최근 거래 신호 */}
      {tradingSignals.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            최근 거래 신호
          </Typography>
          <List>
            {tradingSignals.map((signal, index) => (
              <ListItem key={index} divider={index < tradingSignals.length - 1}>
                <ListItemIcon>
                  {signal.signalType === 'buy' ? (
                    <TrendingUp color="success" />
                  ) : (
                    <TrendingUp color="error" sx={{ transform: 'rotate(180deg)' }} />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography variant="subtitle2">
                        {signal.stockName} ({signal.stockCode})
                      </Typography>
                      <Chip
                        label={signal.signalType === 'buy' ? '매수' : '매도'}
                        size="small"
                        color={signal.signalType === 'buy' ? 'success' : 'error'}
                      />
                      {signal.passedFilters && (
                        <Chip
                          label="필터 통과"
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                    </Stack>
                  }
                  secondary={
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        전략: {signal.strategy} | 신뢰도: {signal.confidence}% | 
                        {signal.timestamp.toLocaleString()}
                      </Typography>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <Tooltip title={`흐름: ${signal.flowType === InvestmentFlowType.FILTER_FIRST ? '필터 우선' : '전략 우선'}`}>
                    <Badge badgeContent={signal.confidence + '%'} color="primary">
                      <IconButton size="small">
                        {signal.flowType === InvestmentFlowType.FILTER_FIRST ? <FilterList /> : <ShowChart />}
                      </IconButton>
                    </Badge>
                  </Tooltip>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  )
}

export default InvestmentFlowManager