import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Stack,
  Switch,
  FormControlLabel,
  Slider,
  Alert,
  IconButton,
  Tooltip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Badge,
  Tabs,
  Tab
} from '@mui/material'
import {
  Add,
  Remove,
  PlayArrow,
  Save,
  FolderOpen,
  TrendingUp,
  TrendingDown,
  ShowChart,
  Timeline,
  Speed,
  Info,
  CheckCircle,
  Warning,
  Security,
  Delete,
  Edit,
  ContentCopy,
  Settings,
  Build,
  Home,
  ArrowBack
} from '@mui/icons-material'
import InvestmentSettingsSummary from './InvestmentSettingsSummary'

interface Indicator {
  id: string
  name: string
  type: 'trend' | 'momentum' | 'volume' | 'volatility'
  params: { [key: string]: number | string }
  enabled: boolean
}

interface Condition {
  id: string
  type: 'buy' | 'sell'
  indicator: string
  operator: '>' | '<' | '=' | 'cross_above' | 'cross_below' | 
    'cloud_above' | 'cloud_below' | 'cloud_break_up' | 'cloud_break_down' |
    'tenkan_kijun_cross_up' | 'tenkan_kijun_cross_down' | 'chikou_above' | 'chikou_below'
  value: number | string
  combineWith: 'AND' | 'OR'
  // 일목균형표 전용 파라미터
  ichimokuLine?: 'tenkan' | 'kijun' | 'senkou_a' | 'senkou_b' | 'chikou'
  confirmBars?: number // 확인봉 개수
}

interface Strategy {
  id: string
  name: string
  description: string
  indicators: Indicator[]
  buyConditions: Condition[]
  sellConditions: Condition[]
  riskManagement: {
    stopLoss: number
    takeProfit: number
    trailingStop: boolean
    trailingStopPercent: number
    positionSize: number
    maxPositions: number
    // 추가된 리스크 관리 옵션
    systemCut?: boolean
    maxDailyLoss?: number
    maxDrawdown?: number
    consecutiveLosses?: number
  }
  // 추가된 고급 기능
  timeframe?: '1분' | '5분' | '15분' | '30분' | '60분' | '일봉' | '주봉' | '월봉'
  splitTrading?: {
    enabled: boolean
    levels: number
    percentages: number[]
  }
  sectorFilter?: {
    enabled: boolean
    sectors: string[]
    comparison: 'outperform' | 'underperform' | 'correlation'
  }
  universe?: {
    minMarketCap?: number
    maxMarketCap?: number
    minPER?: number
    maxPER?: number
    minPBR?: number
    maxPBR?: number
    minROE?: number
    maxROE?: number
  }
  quickTestResult?: {
    returns: number
    winRate: number
    maxDrawdown: number
    trades: number
  }
  advanced?: {
    splitTrading?: {
      enabled: boolean
      levels: number
      percentages: number[]
    }
    sectorFilter?: {
      enabled: boolean
      sectors: string[]
      comparison: 'outperform' | 'underperform' | 'correlation'
    }
    universe?: {
      minMarketCap?: number
      maxMarketCap?: number
      minPER?: number
      maxPER?: number
      minPBR?: number
      maxPBR?: number
      minROE?: number
      maxROE?: number
    }
  }
}

const AVAILABLE_INDICATORS = [
  { id: 'sma', name: 'SMA (단순이동평균)', type: 'trend', defaultParams: { period: 20 } },
  { id: 'ema', name: 'EMA (지수이동평균)', type: 'trend', defaultParams: { period: 20 } },
  { id: 'bb', name: '볼린저밴드', type: 'volatility', defaultParams: { period: 20, stdDev: 2 } },
  { id: 'rsi', name: 'RSI', type: 'momentum', defaultParams: { period: 14 } },
  { id: 'macd', name: 'MACD', type: 'momentum', defaultParams: { fast: 12, slow: 26, signal: 9 } },
  { id: 'stochastic', name: '스토캐스틱', type: 'momentum', defaultParams: { k: 14, d: 3 } },
  { id: 'ichimoku', name: '일목균형표', type: 'trend', defaultParams: { 
    tenkan: 9,  // 전환선
    kijun: 26,  // 기준선 
    senkou: 52, // 선행스팬
    chikou: 26  // 후행스팬
  } },
  { id: 'volume', name: '거래량', type: 'volume', defaultParams: { period: 20 } },
  { id: 'obv', name: 'OBV (누적거래량)', type: 'volume', defaultParams: {} },
  { id: 'vwap', name: 'VWAP (거래량가중평균)', type: 'volume', defaultParams: {} },
  { id: 'atr', name: 'ATR (변동성)', type: 'volatility', defaultParams: { period: 14 } },
  { id: 'cci', name: 'CCI', type: 'momentum', defaultParams: { period: 20 } },
  { id: 'williams', name: 'Williams %R', type: 'momentum', defaultParams: { period: 14 } },
  { id: 'adx', name: 'ADX (추세강도)', type: 'trend', defaultParams: { period: 14 } },
  { id: 'dmi', name: 'DMI (+DI/-DI)', type: 'trend', defaultParams: { period: 14 } },
  { id: 'parabolic', name: 'Parabolic SAR', type: 'trend', defaultParams: { acc: 0.02, max: 0.2 } }
]

const PRESET_STRATEGIES = [
  {
    name: '골든크로스 전략',
    description: '단기 이평선이 장기 이평선을 상향 돌파할 때 매수',
    indicators: ['sma_20', 'sma_60'],
    buyCondition: 'SMA(20) > SMA(60)',
    sellCondition: 'SMA(20) < SMA(60)'
  },
  {
    name: 'RSI 과매도 전략',
    description: 'RSI가 과매도 구간에서 반등할 때 매수',
    indicators: ['rsi_14'],
    buyCondition: 'RSI < 30',
    sellCondition: 'RSI > 70'
  },
  {
    name: '볼린저밴드 전략',
    description: '하단 밴드 터치 후 반등 시 매수',
    indicators: ['bb_20_2'],
    buyCondition: 'Price < BB Lower',
    sellCondition: 'Price > BB Upper'
  }
]

interface StrategyBuilderProps {
  onExecute?: (strategy: Strategy) => void
  onNavigateHome?: () => void
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  )
}

const StrategyBuilderUpdated: React.FC<StrategyBuilderProps> = ({ onExecute, onNavigateHome }) => {
  const [currentTab, setCurrentTab] = useState(0)
  const [strategy, setStrategy] = useState<Strategy>({
    id: 'custom-1',
    name: '나의 전략',
    description: '',
    indicators: [],
    buyConditions: [],
    sellConditions: [],
    riskManagement: {
      stopLoss: -5,
      takeProfit: 10,
      trailingStop: false,
      trailingStopPercent: 3,
      positionSize: 10,
      maxPositions: 10
    }
  })

  const [quickTestRunning, setQuickTestRunning] = useState(false)
  const [savedStrategies, setSavedStrategies] = useState<Strategy[]>([])
  const [dialogOpen, setDialogOpen] = useState(false)
  const [conditionDialogOpen, setConditionDialogOpen] = useState(false)
  const [currentConditionType, setCurrentConditionType] = useState<'buy' | 'sell'>('buy')
  const [tempCondition, setTempCondition] = useState<Condition>({
    id: '',
    type: 'buy',
    indicator: 'rsi',
    operator: '>',
    value: 30,
    combineWith: 'AND'
  })

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
  }

  // 지표 추가
  const addIndicator = (indicatorId: string) => {
    const indicator = AVAILABLE_INDICATORS.find(i => i.id === indicatorId)
    if (!indicator) return

    const newIndicator: Indicator = {
      id: `${indicatorId}_${Date.now()}`,
      name: indicator.name,
      type: indicator.type as any,
      params: Object.fromEntries(
        Object.entries(indicator.defaultParams).map(([key, value]) => [key, value])
      ) as { [key: string]: string | number },
      enabled: true
    }

    setStrategy({
      ...strategy,
      indicators: [...strategy.indicators, newIndicator]
    })
  }

  // 매수/매도 조건 추가
  const addCondition = (type: 'buy' | 'sell') => {
    setCurrentConditionType(type)
    setTempCondition({
      id: `cond_${Date.now()}`,
      type,
      indicator: strategy.indicators[0]?.id || 'rsi',
      operator: type === 'buy' ? '<' : '>',
      value: type === 'buy' ? 30 : 70,
      combineWith: strategy[type === 'buy' ? 'buyConditions' : 'sellConditions'].length > 0 ? 'AND' : 'AND'
    })
    setConditionDialogOpen(true)
  }

  // 조건 저장
  const saveCondition = () => {
    const newCondition = { ...tempCondition, id: `cond_${Date.now()}` }
    if (currentConditionType === 'buy') {
      setStrategy({
        ...strategy,
        buyConditions: [...strategy.buyConditions, newCondition]
      })
    } else {
      setStrategy({
        ...strategy,
        sellConditions: [...strategy.sellConditions, newCondition]
      })
    }
    setConditionDialogOpen(false)
  }

  // 조건 제거
  const removeCondition = (type: 'buy' | 'sell', conditionId: string) => {
    if (type === 'buy') {
      setStrategy({
        ...strategy,
        buyConditions: strategy.buyConditions.filter(c => c.id !== conditionId)
      })
    } else {
      setStrategy({
        ...strategy,
        sellConditions: strategy.sellConditions.filter(c => c.id !== conditionId)
      })
    }
  }

  // 일목균형표 연산자 가져오기
  const getIchimokuOperators = () => [
    { value: 'cloud_above', label: '구름대 상단' },
    { value: 'cloud_below', label: '구름대 하단' },
    { value: 'cloud_break_up', label: '구름대 상향돌파' },
    { value: 'cloud_break_down', label: '구름대 하향돌파' },
    { value: 'tenkan_kijun_cross_up', label: '전환선 > 기준선 교차' },
    { value: 'tenkan_kijun_cross_down', label: '전환선 < 기준선 교차' },
    { value: 'chikou_above', label: '후행스팬 > 주가' },
    { value: 'chikou_below', label: '후행스팬 < 주가' }
  ]

  // 일반 연산자 가져오기
  const getStandardOperators = () => [
    { value: '>', label: '초과 (>)' },
    { value: '<', label: '미만 (<)' },
    { value: '=', label: '같음 (=)' },
    { value: 'cross_above', label: '상향돌파' },
    { value: 'cross_below', label: '하향돌파' }
  ]

  // 빠른 백테스트 실행
  const runQuickTest = async () => {
    setQuickTestRunning(true)
    
    // 시뮬레이션 (실제로는 API 호출)
    setTimeout(() => {
      setStrategy({
        ...strategy,
        quickTestResult: {
          returns: 15.7,
          winRate: 62.5,
          maxDrawdown: -8.3,
          trades: 48
        }
      })
      setQuickTestRunning(false)
    }, 2000)
  }

  // 전략 저장
  const saveStrategy = () => {
    setSavedStrategies([...savedStrategies, { ...strategy, id: `saved_${Date.now()}` }])
    alert('전략이 저장되었습니다')
  }

  // 전략 불러오기
  const loadStrategy = (savedStrategy: Strategy) => {
    setStrategy(savedStrategy)
    setDialogOpen(false)
  }

  // 프리셋 전략 적용
  const applyPreset = (preset: any) => {
    // 프리셋에 따라 전략 설정
    alert(`${preset.name} 전략을 적용합니다`)
  }

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {onNavigateHome && (
              <Button
                variant="contained"
                color="secondary"
                startIcon={<Home />}
                onClick={onNavigateHome}
                size="medium"
              >
                메인으로
              </Button>
            )}
            <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ShowChart />
              전략 빌더
            </Typography>
          </Box>
          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              startIcon={<FolderOpen />}
              onClick={() => setDialogOpen(true)}
            >
              불러오기
            </Button>
            <Button
              variant="outlined"
              startIcon={<Save />}
              onClick={saveStrategy}
            >
              저장
            </Button>
            <Button
              variant="contained"
              startIcon={<Speed />}
              onClick={runQuickTest}
              disabled={quickTestRunning}
              color="secondary"
            >
              퀵 백테스트 (1년)
            </Button>
          </Stack>
        </Box>

        {/* 전략 기본 정보 */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="전략 이름"
              value={strategy.name}
              onChange={(e) => setStrategy({ ...strategy, name: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="설명"
              value={strategy.description}
              onChange={(e) => setStrategy({ ...strategy, description: e.target.value })}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* 탭 메뉴 */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange} variant="fullWidth">
          <Tab icon={<Build />} iconPosition="start" label="전략 구성" />
          <Tab icon={<Settings />} iconPosition="start" label="투자 설정 요약" />
        </Tabs>
      </Paper>

      {/* 전략 구성 탭 */}
      <TabPanel value={currentTab} index={0}>
        {/* 프리셋 전략 */}
        <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          프리셋 전략
        </Typography>
        <Grid container spacing={2}>
          {PRESET_STRATEGIES.map((preset, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" fontWeight="bold">
                    {preset.name}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                    {preset.description}
                  </Typography>
                  <Stack direction="row" spacing={0.5} sx={{ mb: 1 }}>
                    {preset.indicators.map(ind => (
                      <Chip key={ind} label={ind} size="small" />
                    ))}
                  </Stack>
                </CardContent>
                <CardActions>
                  <Button size="small" onClick={() => applyPreset(preset)}>
                    적용
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      <Grid container spacing={3}>
        {/* 기술적 지표 설정 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              기술적 지표
            </Typography>
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>지표 추가</InputLabel>
              <Select
                value=""
                onChange={(e) => addIndicator(e.target.value)}
                label="지표 추가"
              >
                {AVAILABLE_INDICATORS.map(indicator => (
                  <MenuItem key={indicator.id} value={indicator.id}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography>{indicator.name}</Typography>
                      <Chip label={indicator.type} size="small" />
                    </Stack>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Stack spacing={2}>
              {strategy.indicators.map((indicator) => (
                <Card key={indicator.id} variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="subtitle2">{indicator.name}</Typography>
                      <Stack direction="row" spacing={1}>
                        <Switch
                          size="small"
                          checked={indicator.enabled}
                          onChange={(e) => {
                            const updated = strategy.indicators.map(i =>
                              i.id === indicator.id ? { ...i, enabled: e.target.checked } : i
                            )
                            setStrategy({ ...strategy, indicators: updated })
                          }}
                        />
                        <IconButton size="small">
                          <Delete fontSize="small" />
                        </IconButton>
                      </Stack>
                    </Box>
                    
                    {/* 파라미터 설정 */}
                    <Box sx={{ mt: 2 }}>
                      {Object.entries(indicator.params).map(([key, value]) => (
                        <TextField
                          key={key}
                          size="small"
                          label={key}
                          value={value}
                          type="number"
                          sx={{ mr: 1, mb: 1, width: 100 }}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </Paper>
        </Grid>

        {/* 매수/매도 조건 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              매수 조건
            </Typography>
            <Button
              startIcon={<Add />}
              onClick={() => addCondition('buy')}
              size="small"
              sx={{ mb: 2 }}
            >
              조건 추가
            </Button>
            
            <Stack spacing={1}>
              {strategy.buyConditions.map((condition, index) => {
                const indicator = AVAILABLE_INDICATORS.find(i => i.id === condition.indicator)
                const operatorLabel = condition.indicator === 'ichimoku' && 
                  (condition.operator.includes('cloud') || condition.operator.includes('tenkan') || condition.operator.includes('chikou'))
                  ? getIchimokuOperators().find(o => o.value === condition.operator)?.label || condition.operator
                  : getStandardOperators().find(o => o.value === condition.operator)?.label || condition.operator
                
                return (
                  <Chip
                    key={condition.id}
                    label={`${index > 0 ? condition.combineWith + ' ' : ''}${indicator?.name || condition.indicator} ${operatorLabel} ${condition.value}${condition.confirmBars ? ` (확인 ${condition.confirmBars}봉)` : ''}`}
                    onDelete={() => removeCondition('buy', condition.id)}
                    color="success"
                  />
                )
              })}
            </Stack>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              매도 조건
            </Typography>
            <Button
              startIcon={<Add />}
              onClick={() => addCondition('sell')}
              size="small"
              sx={{ mb: 2 }}
            >
              조건 추가
            </Button>
            
            <Stack spacing={1}>
              {strategy.sellConditions.map((condition, index) => {
                const indicator = AVAILABLE_INDICATORS.find(i => i.id === condition.indicator)
                const operatorLabel = condition.indicator === 'ichimoku' && 
                  (condition.operator.includes('cloud') || condition.operator.includes('tenkan') || condition.operator.includes('chikou'))
                  ? getIchimokuOperators().find(o => o.value === condition.operator)?.label || condition.operator
                  : getStandardOperators().find(o => o.value === condition.operator)?.label || condition.operator
                
                return (
                  <Chip
                    key={condition.id}
                    label={`${index > 0 ? condition.combineWith + ' ' : ''}${indicator?.name || condition.indicator} ${operatorLabel} ${condition.value}${condition.confirmBars ? ` (확인 ${condition.confirmBars}봉)` : ''}`}
                    onDelete={() => removeCondition('sell', condition.id)}
                    color="error"
                  />
                )
              })}
            </Stack>
          </Paper>
        </Grid>

        {/* 리스크 관리 */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              리스크 관리
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Typography gutterBottom>손절 (%)</Typography>
                <Slider
                  value={strategy.riskManagement.stopLoss}
                  onChange={(e, v) => setStrategy({
                    ...strategy,
                    riskManagement: {
                      ...strategy.riskManagement,
                      stopLoss: v as number
                    }
                  })}
                  min={0}
                  max={10}
                  step={0.5}
                  marks
                  valueLabelDisplay="auto"
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <Typography gutterBottom>익절 (%)</Typography>
                <Slider
                  value={strategy.riskManagement.takeProfit}
                  onChange={(e, v) => setStrategy({
                    ...strategy,
                    riskManagement: {
                      ...strategy.riskManagement,
                      takeProfit: v as number
                    }
                  })}
                  min={0}
                  max={20}
                  step={0.5}
                  marks
                  valueLabelDisplay="auto"
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <Typography gutterBottom>포지션 크기 (%)</Typography>
                <Slider
                  value={strategy.riskManagement.positionSize}
                  onChange={(e, v) => setStrategy({
                    ...strategy,
                    riskManagement: {
                      ...strategy.riskManagement,
                      positionSize: v as number
                    }
                  })}
                  min={1}
                  max={100}
                  step={1}
                  marks
                  valueLabelDisplay="auto"
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={strategy.riskManagement.trailingStop}
                      onChange={(e) => setStrategy({
                        ...strategy,
                        riskManagement: {
                          ...strategy.riskManagement,
                          trailingStop: e.target.checked
                        }
                      })}
                    />
                  }
                  label="트레일링 스탑"
                />
                {strategy.riskManagement.trailingStop && (
                  <TextField
                    size="small"
                    label="트레일링 %"
                    type="number"
                    value={strategy.riskManagement.trailingStopPercent || 2}
                    onChange={(e) => setStrategy({
                      ...strategy,
                      riskManagement: {
                        ...strategy.riskManagement,
                        trailingStopPercent: Number(e.target.value)
                      }
                    })}
                    fullWidth
                  />
                )}
              </Grid>
            </Grid>
            
            <Divider sx={{ my: 2 }} />
            
            {/* 고급 옵션 */}
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>고급 옵션</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={strategy.riskManagement.systemCut || false}
                      onChange={(e) => setStrategy({
                        ...strategy,
                        riskManagement: {
                          ...strategy.riskManagement,
                          systemCut: e.target.checked
                        }
                      })}
                    />
                  }
                  label={
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Security color="error" />
                      <Typography>시스템 CUT 활성화</Typography>
                    </Stack>
                  }
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={strategy.advanced?.splitTrading?.enabled || false}
                      onChange={(e) => setStrategy({
                        ...strategy,
                        advanced: {
                          ...strategy.advanced,
                          splitTrading: {
                            ...strategy.advanced?.splitTrading,
                            enabled: e.target.checked,
                            levels: 3,
                            percentages: [40, 30, 30]
                          }
                        }
                      })}
                    />
                  }
                  label={
                    <Stack direction="row" spacing={1} alignItems="center">
                      <ShowChart color="primary" />
                      <Typography>분할매매 활성화</Typography>
                    </Stack>
                  }
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* 빠른 테스트 결과 */}
        {strategy.quickTestResult && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3, bgcolor: 'background.default', border: '2px solid', borderColor: 'secondary.main' }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Speed color="secondary" />
                퀵 백테스트 결과 (최근 1년 간략 검증)
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={6} md={3}>
                  <Stack alignItems="center">
                    <Typography variant="h4" color="primary">
                      {strategy.quickTestResult.returns}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      수익률
                    </Typography>
                  </Stack>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Stack alignItems="center">
                    <Typography variant="h4" color="success.main">
                      {strategy.quickTestResult.winRate}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      승률
                    </Typography>
                  </Stack>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Stack alignItems="center">
                    <Typography variant="h4" color="error.main">
                      {strategy.quickTestResult.maxDrawdown}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      최대 낙폭
                    </Typography>
                  </Stack>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Stack alignItems="center">
                    <Typography variant="h4">
                      {strategy.quickTestResult.trades}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      거래 횟수
                    </Typography>
                  </Stack>
                </Grid>
              </Grid>
              
              <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Timeline />}
                  onClick={() => {
                    if (onExecute) onExecute(strategy)
                  }}
                >
                  상세 백테스팅으로 이동
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<TrendingUp />}
                >
                  자동매매 적용
                </Button>
              </Box>
            </Paper>
          </Grid>
        )}
      </Grid>
      </TabPanel>

      {/* 투자 설정 요약 탭 */}
      <TabPanel value={currentTab} index={1}>
        <InvestmentSettingsSummary />
      </TabPanel>

      {/* 저장된 전략 다이얼로그 */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>저장된 전략</DialogTitle>
        <DialogContent>
          <List>
            {savedStrategies.map((saved) => (
              <ListItem key={saved.id} button onClick={() => loadStrategy(saved)}>
                <ListItemIcon>
                  <ShowChart />
                </ListItemIcon>
                <ListItemText
                  primary={saved.name}
                  secondary={saved.description}
                />
                {saved.quickTestResult && (
                  <Chip
                    label={`수익률: ${saved.quickTestResult.returns}%`}
                    color="primary"
                    size="small"
                  />
                )}
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>닫기</Button>
        </DialogActions>
      </Dialog>

      {/* 조건 추가 다이얼로그 */}
      <Dialog open={conditionDialogOpen} onClose={() => setConditionDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {currentConditionType === 'buy' ? '매수' : '매도'} 조건 추가
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {/* 조건 연결 */}
            {(currentConditionType === 'buy' ? strategy.buyConditions : strategy.sellConditions).length > 0 && (
              <Grid item xs={12}>
                <FormControl fullWidth size="small">
                  <InputLabel>조건 연결</InputLabel>
                  <Select
                    value={tempCondition.combineWith}
                    onChange={(e) => setTempCondition({ ...tempCondition, combineWith: e.target.value as 'AND' | 'OR' })}
                    label="조건 연결"
                  >
                    <MenuItem value="AND">AND (&&)</MenuItem>
                    <MenuItem value="OR">OR (||)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            )}
            
            {/* 지표 선택 */}
            <Grid item xs={12}>
              <FormControl fullWidth size="small">
                <InputLabel>지표</InputLabel>
                <Select
                  value={tempCondition.indicator}
                  onChange={(e) => {
                    const newIndicator = e.target.value
                    setTempCondition({ 
                      ...tempCondition, 
                      indicator: newIndicator,
                      operator: newIndicator === 'ichimoku' ? 'cloud_above' : '>',
                      value: newIndicator === 'rsi' ? (currentConditionType === 'buy' ? 30 : 70) : 0
                    })
                  }}
                  label="지표"
                >
                  {AVAILABLE_INDICATORS.map(ind => (
                    <MenuItem key={ind.id} value={ind.id}>{ind.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            {/* 일목균형표 선 선택 */}
            {tempCondition.indicator === 'ichimoku' && (
              <Grid item xs={12}>
                <FormControl fullWidth size="small">
                  <InputLabel>일목균형표 선</InputLabel>
                  <Select
                    value={tempCondition.ichimokuLine || 'tenkan'}
                    onChange={(e) => setTempCondition({ ...tempCondition, ichimokuLine: e.target.value as any })}
                    label="일목균형표 선"
                  >
                    <MenuItem value="tenkan">전환선 (9일)</MenuItem>
                    <MenuItem value="kijun">기준선 (26일)</MenuItem>
                    <MenuItem value="senkou_a">선행스팬 A</MenuItem>
                    <MenuItem value="senkou_b">선행스팬 B</MenuItem>
                    <MenuItem value="chikou">후행스팬</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            )}
            
            {/* 연산자 */}
            <Grid item xs={12}>
              <FormControl fullWidth size="small">
                <InputLabel>조건</InputLabel>
                <Select
                  value={tempCondition.operator}
                  onChange={(e) => setTempCondition({ ...tempCondition, operator: e.target.value as any })}
                  label="조건"
                >
                  {tempCondition.indicator === 'ichimoku' ? (
                    getIchimokuOperators().map(op => (
                      <MenuItem key={op.value} value={op.value}>{op.label}</MenuItem>
                    ))
                  ) : (
                    getStandardOperators().map(op => (
                      <MenuItem key={op.value} value={op.value}>{op.label}</MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
            </Grid>
            
            {/* 값 */}
            {tempCondition.indicator === 'ichimoku' && 
             (tempCondition.operator.includes('cloud') || tempCondition.operator.includes('tenkan')) ? (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  size="small"
                  type="number"
                  label="확인봉 개수"
                  value={tempCondition.confirmBars || 1}
                  onChange={(e) => setTempCondition({ ...tempCondition, confirmBars: parseInt(e.target.value) })}
                  helperText="연속으로 조건을 만족해야 하는 봉의 개수"
                />
              </Grid>
            ) : tempCondition.operator !== 'cross_above' && tempCondition.operator !== 'cross_below' ? (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  size="small"
                  type="number"
                  label="값"
                  value={tempCondition.value}
                  onChange={(e) => setTempCondition({ ...tempCondition, value: parseFloat(e.target.value) })}
                />
              </Grid>
            ) : null}
            
            {/* 설명 */}
            <Grid item xs={12}>
              <Alert severity="info">
                {tempCondition.indicator === 'ichimoku' ? (
                  <>
                    일목균형표는 전환선(9일), 기준선(26일), 선행스팬(52일), 후행스팬(26일)으로 구성됩니다.
                    구름대는 선행스팬 A와 B 사이의 영역을 의미합니다.
                  </>
                ) : tempCondition.indicator === 'rsi' ? (
                  <>RSI {currentConditionType === 'buy' ? '30 미만은 과매도' : '70 초과는 과매수'} 신호입니다.</>
                ) : tempCondition.indicator === 'macd' ? (
                  <>MACD와 시그널선의 교차를 통해 매매 시점을 포착합니다.</>
                ) : (
                  <>선택한 지표와 조건에 따라 {currentConditionType === 'buy' ? '매수' : '매도'} 신호가 발생합니다.</>
                )}
              </Alert>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConditionDialogOpen(false)}>취소</Button>
          <Button onClick={saveCondition} variant="contained">추가</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default StrategyBuilderUpdated