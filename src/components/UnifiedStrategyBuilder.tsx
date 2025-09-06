import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Stack,
  Chip,
  IconButton,
  Badge,
  Tooltip,
  Divider,
  Alert,
  Tabs,
  Tab,
  Drawer,
  Collapse,
  LinearProgress
} from '@mui/material'
import {
  FilterList,
  ShowChart,
  Business,
  CheckCircle,
  Settings,
  PlayArrow,
  Save,
  Assessment,
  TrendingUp,
  Info,
  KeyboardArrowLeft,
  KeyboardArrowRight,
  Dashboard,
  Speed,
  Visibility,
  VisibilityOff,
  AccountTree,
  Timeline
} from '@mui/icons-material'
// import InvestmentSettings from '../pages/InvestmentSettings'
// import StrategyBuilderUpdated from './StrategyBuilder'
import InvestmentWorkspace from './InvestmentWorkspace'
import InvestmentFlowManager from './InvestmentFlowManager'
import { supabase } from '../lib/supabase'

interface UnifiedStrategyBuilderProps {
  onNavigateHome?: () => void
}

const UnifiedStrategyBuilder: React.FC<UnifiedStrategyBuilderProps> = ({ onNavigateHome }) => {
  const [activeStep, setActiveStep] = useState(0)
  const [investmentConfig, setInvestmentConfig] = useState<any>(null)
  const [strategy, setStrategy] = useState<any>(null)
  const [filteredUniverse, setFilteredUniverse] = useState<any[]>([])
  const [selectedStock, setSelectedStock] = useState<any>(null)
  
  // 패널 표시 상태
  const [showFilters, setShowFilters] = useState(true)
  const [showStrategy, setShowStrategy] = useState(true)
  const [showUniverse, setShowUniverse] = useState(true)
  
  // 레이아웃 모드
  const [layoutMode, setLayoutMode] = useState<'workspace' | 'wizard'>('workspace')
  
  // 진행 상태
  const [progress, setProgress] = useState({
    filters: false,
    universe: false,
    strategy: false,
    backtest: false
  })

  const steps = [
    {
      label: '투자 필터 설정',
      icon: <FilterList />,
      description: '투자 유니버스 구성을 위한 재무/섹터 필터'
    },
    {
      label: '유니버스 확인',
      icon: <Business />,
      description: '필터링된 투자 대상 종목 확인'
    },
    {
      label: '전략 구성',
      icon: <ShowChart />,
      description: '매수/매도 조건 및 리스크 관리'
    },
    {
      label: '백테스트',
      icon: <Timeline />,
      description: '전략 성과 검증 및 최적화'
    }
  ]

  useEffect(() => {
    // localStorage에서 투자 설정 불러오기
    const saved = localStorage.getItem('investmentConfig')
    if (saved) {
      setInvestmentConfig(JSON.parse(saved))
      setProgress(prev => ({ ...prev, filters: true }))
    }
  }, [])

  const handleInvestmentConfigChange = (config: any) => {
    setInvestmentConfig(config)
    localStorage.setItem('investmentConfig', JSON.stringify(config))
    setProgress(prev => ({ ...prev, filters: true }))
  }

  const handleStrategyChange = (newStrategy: any) => {
    setStrategy(newStrategy)
    setProgress(prev => ({ ...prev, strategy: true }))
  }

  const handleUniverseChange = (stocks: any[]) => {
    setFilteredUniverse(stocks)
    setProgress(prev => ({ ...prev, universe: stocks.length > 0 }))
  }

  const handleStockSelect = (stock: any) => {
    setSelectedStock(stock)
    // 개별 종목 상세 분석 표시
  }

  const getProgressPercentage = () => {
    const completed = Object.values(progress).filter(v => v).length
    return (completed / 4) * 100
  }

  const renderWorkspaceMode = () => (
    <Grid container spacing={2} sx={{ height: 'calc(100vh - 200px)' }}>
      {/* 왼쪽: 투자 필터 (30%) */}
      <Grid item xs={showFilters ? 4 : 0.5} sx={{ transition: 'all 0.3s' }}>
        <Paper sx={{ height: '100%', overflow: 'hidden', position: 'relative' }}>
          {showFilters ? (
            <Box sx={{ height: '100%', overflow: 'auto', p: 2 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <FilterList />
                  투자 필터
                </Typography>
                <IconButton size="small" onClick={() => setShowFilters(false)}>
                  <KeyboardArrowLeft />
                </IconButton>
              </Stack>
              
              {/* 간소화된 투자 설정 */}
              <InvestmentFilterPanel 
                config={investmentConfig}
                onChange={handleInvestmentConfigChange}
              />
            </Box>
          ) : (
            <Box sx={{ 
              height: '100%', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              cursor: 'pointer'
            }}
            onClick={() => setShowFilters(true)}
            >
              <Stack alignItems="center" spacing={1}>
                <FilterList />
                <Typography variant="caption" sx={{ writingMode: 'vertical-rl' }}>
                  투자 필터
                </Typography>
              </Stack>
            </Box>
          )}
        </Paper>
      </Grid>

      {/* 가운데: 전략 빌더 (35%) */}
      <Grid item xs={showStrategy ? 4 : 0.5} sx={{ transition: 'all 0.3s' }}>
        <Paper sx={{ height: '100%', overflow: 'hidden' }}>
          {showStrategy ? (
            <Box sx={{ height: '100%', overflow: 'auto', p: 2 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ShowChart />
                  전략 구성
                </Typography>
                <IconButton size="small" onClick={() => setShowStrategy(false)}>
                  <VisibilityOff />
                </IconButton>
              </Stack>
              
              {/* 간소화된 전략 빌더 */}
              <StrategyPanel
                strategy={strategy}
                onChange={handleStrategyChange}
                universe={filteredUniverse}
              />
            </Box>
          ) : (
            <Box sx={{ 
              height: '100%', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              cursor: 'pointer'
            }}
            onClick={() => setShowStrategy(true)}
            >
              <Stack alignItems="center" spacing={1}>
                <ShowChart />
                <Typography variant="caption" sx={{ writingMode: 'vertical-rl' }}>
                  전략 구성
                </Typography>
              </Stack>
            </Box>
          )}
        </Paper>
      </Grid>

      {/* 오른쪽: 필터링된 유니버스 (35%) */}
      <Grid item xs={showUniverse ? 4 : 0.5} sx={{ transition: 'all 0.3s' }}>
        <Paper sx={{ height: '100%', overflow: 'hidden' }}>
          {showUniverse ? (
            <Box sx={{ height: '100%', overflow: 'hidden' }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ p: 2, pb: 0 }}>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Business />
                  투자 유니버스
                  <Badge badgeContent={filteredUniverse.length} color="primary" max={999}>
                    <Box />
                  </Badge>
                </Typography>
                <IconButton size="small" onClick={() => setShowUniverse(false)}>
                  <KeyboardArrowRight />
                </IconButton>
              </Stack>
              
              <Box sx={{ height: 'calc(100% - 60px)', overflow: 'auto' }}>
                <InvestmentWorkspace
                  investmentConfig={investmentConfig}
                  strategy={strategy}
                  onUniverseChange={handleUniverseChange}
                  onStockSelect={handleStockSelect}
                />
              </Box>
            </Box>
          ) : (
            <Box sx={{ 
              height: '100%', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              cursor: 'pointer'
            }}
            onClick={() => setShowUniverse(true)}
            >
              <Stack alignItems="center" spacing={1}>
                <Badge badgeContent={filteredUniverse.length} color="primary">
                  <Business />
                </Badge>
                <Typography variant="caption" sx={{ writingMode: 'vertical-rl' }}>
                  유니버스
                </Typography>
              </Stack>
            </Box>
          )}
        </Paper>
      </Grid>
    </Grid>
  )

  const renderWizardMode = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={3}>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => (
            <Step key={step.label}>
              <StepLabel
                StepIconComponent={() => (
                  <IconButton
                    color={activeStep === index ? 'primary' : 'default'}
                    onClick={() => setActiveStep(index)}
                  >
                    {step.icon}
                  </IconButton>
                )}
              >
                {step.label}
              </StepLabel>
              <StepContent>
                <Typography variant="body2" color="textSecondary">
                  {step.description}
                </Typography>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Grid>

      <Grid item xs={12} md={9}>
        {activeStep === 0 && (
          <Alert severity="info">투자 필터 설정 화면</Alert>
        )}
        {activeStep === 1 && (
          <InvestmentWorkspace
            investmentConfig={investmentConfig}
            strategy={strategy}
            onUniverseChange={handleUniverseChange}
            onStockSelect={handleStockSelect}
          />
        )}
        {activeStep === 2 && (
          <Alert severity="info">전략 구성 화면</Alert>
        )}
        {activeStep === 3 && (
          <Alert severity="info">백테스트 기능 준비 중...</Alert>
        )}
      </Grid>
    </Grid>
  )

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 헤더 */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container alignItems="center" spacing={2}>
          <Grid item xs>
            <Stack direction="row" spacing={2} alignItems="center">
              <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Dashboard />
                통합 투자 전략 워크스페이스
              </Typography>
              
              <Divider orientation="vertical" flexItem />
              
              <Chip
                icon={<CheckCircle />}
                label={`진행률 ${getProgressPercentage().toFixed(0)}%`}
                color={getProgressPercentage() === 100 ? 'success' : 'primary'}
                variant="outlined"
              />
            </Stack>
          </Grid>

          <Grid item>
            <Stack direction="row" spacing={1}>
              <Tooltip title="레이아웃 모드 전환">
                <IconButton
                  onClick={() => setLayoutMode(layoutMode === 'workspace' ? 'wizard' : 'workspace')}
                >
                  {layoutMode === 'workspace' ? <AccountTree /> : <Dashboard />}
                </IconButton>
              </Tooltip>
              
              <Button
                variant="outlined"
                startIcon={<Save />}
                disabled={!progress.strategy}
              >
                저장
              </Button>
              
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                disabled={!progress.strategy || !progress.universe}
              >
                백테스트
              </Button>
            </Stack>
          </Grid>
        </Grid>

        {/* 진행 상태 바 */}
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={getProgressPercentage()} />
          <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
            {Object.entries(progress).map(([key, value]) => (
              <Chip
                key={key}
                size="small"
                label={key}
                color={value ? 'success' : 'default'}
                variant={value ? 'filled' : 'outlined'}
              />
            ))}
          </Stack>
        </Box>
      </Paper>

      {/* 메인 컨텐츠 */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        {layoutMode === 'workspace' ? renderWorkspaceMode() : renderWizardMode()}
      </Box>

      {/* 선택된 종목 상세 (Drawer) */}
      <Drawer
        anchor="bottom"
        open={!!selectedStock}
        onClose={() => setSelectedStock(null)}
      >
        {selectedStock && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6">
              {selectedStock.name} ({selectedStock.code})
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={3}>
                <Typography variant="caption" color="textSecondary">시가총액</Typography>
                <Typography variant="body1">{selectedStock.marketCap}억원</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="caption" color="textSecondary">PER</Typography>
                <Typography variant="body1">{selectedStock.per}</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="caption" color="textSecondary">ROE</Typography>
                <Typography variant="body1">{selectedStock.roe}%</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="caption" color="textSecondary">전략 적합도</Typography>
                <Typography variant="body1">{selectedStock.score}점</Typography>
              </Grid>
            </Grid>
          </Box>
        )}
      </Drawer>
    </Box>
  )
}

// 간소화된 투자 필터 패널
const InvestmentFilterPanel: React.FC<any> = ({ config, onChange }) => {
  return (
    <Stack spacing={2}>
      <Alert severity="info" icon={<Info />}>
        투자 필터를 설정하여 투자 대상을 선별합니다
      </Alert>
      
      <Card variant="outlined">
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>시가총액</Typography>
          <Stack direction="row" spacing={1}>
            <Chip label="100억 이상" size="small" />
            <Chip label="5조 이하" size="small" />
          </Stack>
        </CardContent>
      </Card>

      <Card variant="outlined">
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>재무지표</Typography>
          <Stack spacing={1}>
            <Stack direction="row" spacing={1}>
              <Chip label="PER 5-25" size="small" />
              <Chip label="PBR 0.5-3" size="small" />
            </Stack>
            <Stack direction="row" spacing={1}>
              <Chip label="ROE 5-30%" size="small" />
              <Chip label="부채 0-100%" size="small" />
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      <Card variant="outlined">
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>섹터</Typography>
          <Stack direction="row" spacing={0.5} flexWrap="wrap">
            <Chip label="IT" size="small" color="primary" />
            <Chip label="바이오" size="small" color="primary" />
            <Chip label="2차전지" size="small" color="primary" />
          </Stack>
        </CardContent>
      </Card>

      <Button variant="outlined" fullWidth size="small">
        상세 설정
      </Button>
    </Stack>
  )
}

// 간소화된 전략 패널
const StrategyPanel: React.FC<any> = ({ strategy, onChange, universe }) => {
  return (
    <Stack spacing={2}>
      <Alert severity="info" icon={<Info />}>
        {universe.length}개 종목에 적용할 전략을 구성합니다
      </Alert>

      <Card variant="outlined">
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>매수 조건</Typography>
          <Stack spacing={1}>
            <Chip label="RSI < 30" size="small" color="success" />
            <Chip label="거래량 > 평균 150%" size="small" color="success" />
          </Stack>
        </CardContent>
        <CardActions>
          <Button size="small">조건 추가</Button>
        </CardActions>
      </Card>

      <Card variant="outlined">
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>매도 조건</Typography>
          <Stack spacing={1}>
            <Chip label="RSI > 70" size="small" color="error" />
            <Chip label="손절 -5%" size="small" color="error" />
          </Stack>
        </CardContent>
        <CardActions>
          <Button size="small">조건 추가</Button>
        </CardActions>
      </Card>

      <Card variant="outlined">
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>리스크 관리</Typography>
          <Stack spacing={0.5}>
            <Typography variant="caption">포지션: 10%</Typography>
            <Typography variant="caption">최대 보유: 10종목</Typography>
          </Stack>
        </CardContent>
      </Card>

      <Button variant="outlined" fullWidth size="small">
        상세 전략 설정
      </Button>
    </Stack>
  )
}

export default UnifiedStrategyBuilder