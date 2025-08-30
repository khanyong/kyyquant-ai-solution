import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Slider,
  TextField,
  Chip,
  Stack,
  FormControlLabel,
  Switch,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Divider,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  RadioGroup,
  Radio,
  FormLabel,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Breadcrumbs,
  Link
} from '@mui/material'
import {
  TrendingUp,
  Analytics,
  AccountBalance,
  FilterList,
  Save,
  RestartAlt,
  Info,
  Warning,
  ShowChart,
  Business,
  Shield,
  Schedule,
  Notifications,
  CompareArrows,
  Percent,
  Add,
  Remove,
  AttachMoney,
  Assessment,
  ArrowBack,
  Home
} from '@mui/icons-material'

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
      id={`investment-tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

interface CompleteInvestmentConfig {
  // 투자 유니버스
  universe: {
    marketCap: [number, number]
    per: [number, number]
    pbr: [number, number]
    roe: [number, number]
    debtRatio: [number, number]
    tradingVolume: [number, number]
    foreignOwnership: [number, number] // 외국인 지분율
    institutionalOwnership: [number, number] // 기관 지분율
    excludeTradingHalt: boolean // 거래정지 종목 제외
    excludeWarningStock: boolean // 투자주의 종목 제외
    excludePennyStock: boolean // 동전주 제외
    pennyStockPrice: number // 동전주 기준가격
  }
  
  // 섹터 설정
  sectors: {
    include: string[]
    exclude: string[]
    sectorWeights: { [key: string]: number }
    sectorIndices: {
      code: string
      name: string
      enabled: boolean
      weight: number
      correlation?: number // 상관계수
      performance?: number // 최근 성과
    }[]
    correlationAnalysis: boolean // 상관관계 분석 사용
    sectorRotation: boolean // 섹터 로테이션 사용
    rotationPeriod: 'weekly' | 'monthly' | 'quarterly'
  }
  
  // 포트폴리오 관리
  portfolio: {
    maxPositions: number
    minPositions: number
    positionSizeMethod: 'equal' | 'risk_parity' | 'kelly' | 'market_cap' | 'custom'
    maxPositionSize: number
    minPositionSize: number
    cashBuffer: number
    rebalancePeriod: 'daily' | 'weekly' | 'monthly' | 'quarterly'
    rebalanceThreshold: number
    diversification: {
      maxSectorConcentration: number // 섹터별 최대 비중
      maxStockConcentration: number // 개별 종목 최대 비중
      minCorrelation: number // 종목간 최소 상관계수
    }
  }
  
  // 리스크 관리
  risk: {
    maxDrawdown: number
    stopLoss: number
    takeProfit: number
    trailingStop: boolean
    trailingStopPercent: number
    timeStop: boolean
    timeStopDays: number
    positionScaling: boolean
    scaleInThreshold: number
    scaleOutThreshold: number
    correlationLimit: number
    volatilityFilter: boolean
    maxVolatility: number
    systemCut: { // 시스템 컷 설정
      enabled: boolean
      maxDailyLoss: number // 일일 최대 손실
      maxWeeklyLoss: number // 주간 최대 손실
      maxMonthlyLoss: number // 월간 최대 손실
      maxConsecutiveLosses: number // 연속 손실 횟수
      pauseDuration: number // 일시정지 기간 (분)
      action: 'stop' | 'pause' | 'reduce' // 컷 발생시 동작
      reducePositionRatio: number // 포지션 축소 비율
    }
    hedging: {
      enabled: boolean
      method: 'futures' | 'options' | 'inverse_etf'
      hedgeRatio: number
    }
  }
  
  // 매매 조건
  trading: {
    orderType: 'limit' | 'market' | 'stop' | 'stop_limit'
    slippage: number // 슬리피지 허용치
    commission: number // 수수료율
    tax: number // 세금율
    minTradeAmount: number // 최소 거래금액
    maxTradeAmount: number // 최대 거래금액
    tradingHours: {
      start: string
      end: string
      preMarketTrading: boolean
      afterHoursTrading: boolean
    }
    splitTrading: { // 분할매매 설정
      enabled: boolean
      buyLevels: number[] // 매수 분할 레벨 (%)
      sellLevels: number[] // 매도 분할 레벨 (%)
      buyRatios: number[] // 매수 비율
      sellRatios: number[] // 매도 비율
      useTimeBasedSplit: boolean // 시간 분할 사용
      timeIntervals: number[] // 시간 간격 (분)
    }
    marketConditions: {
      bullMarketSettings: any
      bearMarketSettings: any
      sidewaysMarketSettings: any
    }
  }
  
  // 업종 대비 분석
  sectorComparison: {
    enabled: boolean
    mainIndices: {
      code: string
      name: string
      enabled: boolean
      timeframe: string
    }[]
    comparison: 'outperform' | 'underperform' | 'correlation'
    threshold: number
    timeframes: string[]
  }
  
  // 자동화 설정
  automation: {
    autoStart: boolean
    autoStartTime: string
    autoStopTime: string
    weekendTrading: boolean
    holidayTrading: boolean
    emergencyStop: {
      enabled: boolean
      maxDailyLoss: number
      maxConsecutiveLosses: number
      systemErrorAction: 'stop' | 'pause' | 'continue'
    }
  }
  
  // 알림 설정
  notifications: {
    email: {
      enabled: boolean
      address: string
      events: string[]
    }
    kakao: {
      enabled: boolean
      token: string
      events: string[]
    }
    telegram: {
      enabled: boolean
      botToken: string
      chatId: string
      events: string[]
    }
    webhook: {
      enabled: boolean
      url: string
      events: string[]
    }
  }
}

const SECTORS = [
  'IT/소프트웨어', '반도체', '2차전지', '바이오/헬스케어', 
  '자동차', '화학', '철강/소재', '금융', '건설/부동산',
  '유통/소비재', '엔터테인먼트', '조선/기계', '에너지',
  '통신', '운송', '게임', '화장품', '식품/음료', '전기전자'
]

const NOTIFICATION_EVENTS = [
  '매수 체결', '매도 체결', '손절매 발생', '익절매 발생',
  '일일 수익률', '주간 리포트', '월간 리포트', '시스템 오류',
  '비상 정지', '리밸런싱 실행', '새로운 신호', '포트폴리오 알림'
]

const InvestmentSettingsComplete: React.FC = () => {
  const navigate = useNavigate()
  const [currentTab, setCurrentTab] = useState(0)
  const [config, setConfig] = useState<CompleteInvestmentConfig>({
    universe: {
      marketCap: [100, 50000],
      per: [5, 25],
      pbr: [0.5, 3],
      roe: [5, 30],
      debtRatio: [0, 100],
      tradingVolume: [100, 10000],
      foreignOwnership: [5, 50],
      institutionalOwnership: [10, 70],
      excludeTradingHalt: true,
      excludeWarningStock: true,
      excludePennyStock: false,
      pennyStockPrice: 1000
    },
    sectors: {
      include: ['IT/소프트웨어', '반도체', '2차전지', '바이오/헬스케어'],
      exclude: ['건설/부동산', '조선/기계'],
      sectorWeights: {},
      sectorIndices: [
        { code: 'IT', name: 'IT/소프트웨어', enabled: true, weight: 1.0, correlation: 0.75, performance: 15.2 },
        { code: 'BIO', name: '바이오/헬스케어', enabled: true, weight: 1.2, correlation: 0.45, performance: 8.7 },
        { code: 'BATT', name: '2차전지', enabled: true, weight: 1.1, correlation: 0.82, performance: 22.5 },
        { code: 'SEMI', name: '반도체', enabled: true, weight: 0.9, correlation: 0.91, performance: 18.3 }
      ],
      correlationAnalysis: true,
      sectorRotation: false,
      rotationPeriod: 'monthly'
    },
    portfolio: {
      maxPositions: 20,
      minPositions: 5,
      positionSizeMethod: 'equal',
      maxPositionSize: 20,
      minPositionSize: 3,
      cashBuffer: 10,
      rebalancePeriod: 'monthly',
      rebalanceThreshold: 5,
      diversification: {
        maxSectorConcentration: 30,
        maxStockConcentration: 10,
        minCorrelation: 0.3
      }
    },
    risk: {
      maxDrawdown: 20,
      stopLoss: -7,
      takeProfit: 15,
      trailingStop: false,
      trailingStopPercent: 5,
      timeStop: false,
      timeStopDays: 30,
      positionScaling: false,
      scaleInThreshold: -3,
      scaleOutThreshold: 10,
      correlationLimit: 0.7,
      volatilityFilter: true,
      maxVolatility: 30,
      systemCut: {
        enabled: true,
        maxDailyLoss: -3,
        maxWeeklyLoss: -7,
        maxMonthlyLoss: -15,
        maxConsecutiveLosses: 5,
        pauseDuration: 60,
        action: 'pause',
        reducePositionRatio: 0.5
      },
      hedging: {
        enabled: false,
        method: 'futures',
        hedgeRatio: 0.5
      }
    },
    trading: {
      orderType: 'limit',
      slippage: 0.3,
      commission: 0.015,
      tax: 0.23,
      minTradeAmount: 100000,
      maxTradeAmount: 10000000,
      tradingHours: {
        start: '09:00',
        end: '15:20',
        preMarketTrading: false,
        afterHoursTrading: false
      },
      splitTrading: {
        enabled: false,
        buyLevels: [-2, -5, -10],
        sellLevels: [3, 5, 10],
        buyRatios: [0.3, 0.3, 0.4],
        sellRatios: [0.3, 0.3, 0.4],
        useTimeBasedSplit: false,
        timeIntervals: [30, 60, 120]
      },
      marketConditions: {
        bullMarketSettings: {},
        bearMarketSettings: {},
        sidewaysMarketSettings: {}
      }
    },
    sectorComparison: {
      enabled: true,
      mainIndices: [
        { code: 'KOSPI', name: 'KOSPI', enabled: true, timeframe: '일봉' },
        { code: 'KOSDAQ', name: 'KOSDAQ', enabled: true, timeframe: '일봉' }
      ],
      comparison: 'outperform',
      threshold: 5,
      timeframes: ['일봉', '주봉', '월봉']
    },
    automation: {
      autoStart: false,
      autoStartTime: '09:00',
      autoStopTime: '15:30',
      weekendTrading: false,
      holidayTrading: false,
      emergencyStop: {
        enabled: true,
        maxDailyLoss: -5,
        maxConsecutiveLosses: 3,
        systemErrorAction: 'pause'
      }
    },
    notifications: {
      email: {
        enabled: false,
        address: '',
        events: []
      },
      kakao: {
        enabled: false,
        token: '',
        events: []
      },
      telegram: {
        enabled: false,
        botToken: '',
        chatId: '',
        events: []
      },
      webhook: {
        enabled: false,
        url: '',
        events: []
      }
    }
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = () => {
    const saved = localStorage.getItem('completeInvestmentConfig')
    if (saved) {
      setConfig(JSON.parse(saved))
    }
  }

  const saveSettings = () => {
    setSaving(true)
    localStorage.setItem('completeInvestmentConfig', JSON.stringify(config))
    setTimeout(() => {
      setSaving(false)
      setMessage('투자 설정이 저장되었습니다')
      setTimeout(() => setMessage(''), 3000)
    }, 500)
  }

  const resetSettings = () => {
    if (confirm('모든 설정을 초기값으로 되돌리시겠습니까?')) {
      localStorage.removeItem('completeInvestmentConfig')
      window.location.reload()
    }
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
  }

  const toggleSector = (sector: string, type: 'include' | 'exclude') => {
    const currentList = config.sectors[type]
    const otherType = type === 'include' ? 'exclude' : 'include'
    const otherList = config.sectors[otherType]
    
    if (currentList.includes(sector)) {
      setConfig({
        ...config,
        sectors: {
          ...config.sectors,
          [type]: currentList.filter(s => s !== sector)
        }
      })
    } else {
      setConfig({
        ...config,
        sectors: {
          ...config.sectors,
          [type]: [...currentList, sector],
          [otherType]: otherList.filter(s => s !== sector)
        }
      })
    }
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        {/* Breadcrumbs */}
        <Breadcrumbs sx={{ mb: 2 }}>
          <Link
            underline="hover"
            color="inherit"
            onClick={() => navigate('/')}
            sx={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            <Home fontSize="small" />
            메인
          </Link>
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <TrendingUp fontSize="small" />
            투자 설정
          </Typography>
        </Breadcrumbs>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Tooltip title="메인으로 돌아가기">
              <IconButton 
                onClick={() => navigate('/')}
                sx={{ 
                  bgcolor: 'action.hover',
                  '&:hover': { bgcolor: 'action.selected' }
                }}
              >
                <ArrowBack />
              </IconButton>
            </Tooltip>
            <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TrendingUp sx={{ fontSize: 35 }} />
              투자 설정
            </Typography>
          </Box>
          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              color="secondary"
              startIcon={<Home />}
              onClick={() => navigate('/')}
              size="large"
            >
              메인으로 돌아가기
            </Button>
            <Button
              variant="outlined"
              startIcon={<RestartAlt />}
              onClick={resetSettings}
            >
              초기화
            </Button>
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={saveSettings}
              disabled={saving}
            >
              저장
            </Button>
          </Stack>
        </Box>

        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={currentTab} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
              <Tab icon={<FilterList />} iconPosition="start" label="투자 유니버스" />
              <Tab icon={<Business />} iconPosition="start" label="섹터 설정" />
              <Tab icon={<AccountBalance />} iconPosition="start" label="포트폴리오" />
              <Tab icon={<Shield />} iconPosition="start" label="리스크 관리" />
              <Tab icon={<CompareArrows />} iconPosition="start" label="업종 대비" />
              <Tab icon={<AttachMoney />} iconPosition="start" label="매매 설정" />
              <Tab icon={<Schedule />} iconPosition="start" label="자동화" />
              <Tab icon={<Notifications />} iconPosition="start" label="알림" />
            </Tabs>
          </Box>

          {/* 투자 유니버스 탭 */}
          <TabPanel value={currentTab} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Alert severity="info" icon={<Info />}>
                  투자 대상 종목을 필터링하는 기준을 설정합니다. 이 조건을 만족하는 종목만 매매 대상이 됩니다.
                </Alert>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      재무 지표 필터
                    </Typography>
                    
                    <Box sx={{ mt: 3 }}>
                      <Typography gutterBottom>시가총액 (억원)</Typography>
                      <Slider
                        value={config.universe.marketCap}
                        onChange={(e, value) => setConfig({
                          ...config,
                          universe: { ...config.universe, marketCap: value as [number, number] }
                        })}
                        valueLabelDisplay="auto"
                        min={0}
                        max={100000}
                        step={100}
                        marks={[
                          { value: 0, label: '0' },
                          { value: 50000, label: '5조' },
                          { value: 100000, label: '10조' }
                        ]}
                      />
                    </Box>
                    
                    <Box sx={{ mt: 3 }}>
                      <Typography gutterBottom>PER (주가수익비율)</Typography>
                      <Slider
                        value={config.universe.per}
                        onChange={(e, value) => setConfig({
                          ...config,
                          universe: { ...config.universe, per: value as [number, number] }
                        })}
                        valueLabelDisplay="auto"
                        min={0}
                        max={50}
                      />
                    </Box>
                    
                    <Box sx={{ mt: 3 }}>
                      <Typography gutterBottom>PBR (주가순자산비율)</Typography>
                      <Slider
                        value={config.universe.pbr}
                        onChange={(e, value) => setConfig({
                          ...config,
                          universe: { ...config.universe, pbr: value as [number, number] }
                        })}
                        valueLabelDisplay="auto"
                        min={0}
                        max={10}
                        step={0.1}
                      />
                    </Box>
                    
                    <Box sx={{ mt: 3 }}>
                      <Typography gutterBottom>ROE (자기자본이익률) %</Typography>
                      <Slider
                        value={config.universe.roe}
                        onChange={(e, value) => setConfig({
                          ...config,
                          universe: { ...config.universe, roe: value as [number, number] }
                        })}
                        valueLabelDisplay="auto"
                        min={-10}
                        max={50}
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      시장 지표 필터
                    </Typography>
                    
                    <Box sx={{ mt: 3 }}>
                      <Typography gutterBottom>부채비율 %</Typography>
                      <Slider
                        value={config.universe.debtRatio}
                        onChange={(e, value) => setConfig({
                          ...config,
                          universe: { ...config.universe, debtRatio: value as [number, number] }
                        })}
                        valueLabelDisplay="auto"
                        min={0}
                        max={300}
                      />
                    </Box>
                    
                    <Box sx={{ mt: 3 }}>
                      <Typography gutterBottom>일평균 거래대금 (백만원)</Typography>
                      <Slider
                        value={config.universe.tradingVolume}
                        onChange={(e, value) => setConfig({
                          ...config,
                          universe: { ...config.universe, tradingVolume: value as [number, number] }
                        })}
                        valueLabelDisplay="auto"
                        min={0}
                        max={50000}
                        step={100}
                      />
                    </Box>
                    
                    <Box sx={{ mt: 3 }}>
                      <Typography gutterBottom>외국인 지분율 %</Typography>
                      <Slider
                        value={config.universe.foreignOwnership}
                        onChange={(e, value) => setConfig({
                          ...config,
                          universe: { ...config.universe, foreignOwnership: value as [number, number] }
                        })}
                        valueLabelDisplay="auto"
                        min={0}
                        max={100}
                      />
                    </Box>
                    
                    <Box sx={{ mt: 3 }}>
                      <Typography gutterBottom>기관 지분율 %</Typography>
                      <Slider
                        value={config.universe.institutionalOwnership}
                        onChange={(e, value) => setConfig({
                          ...config,
                          universe: { ...config.universe, institutionalOwnership: value as [number, number] }
                        })}
                        valueLabelDisplay="auto"
                        min={0}
                        max={100}
                      />
                    </Box>
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="subtitle2" gutterBottom>
                      제외 조건
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.universe.excludeTradingHalt}
                          onChange={(e) => setConfig({
                            ...config,
                            universe: { ...config.universe, excludeTradingHalt: e.target.checked }
                          })}
                        />
                      }
                      label="거래정지 종목 제외"
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.universe.excludeWarningStock}
                          onChange={(e) => setConfig({
                            ...config,
                            universe: { ...config.universe, excludeWarningStock: e.target.checked }
                          })}
                        />
                      }
                      label="투자주의 종목 제외"
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.universe.excludePennyStock}
                          onChange={(e) => setConfig({
                            ...config,
                            universe: { ...config.universe, excludePennyStock: e.target.checked }
                          })}
                        />
                      }
                      label="동전주 제외"
                    />
                    
                    {config.universe.excludePennyStock && (
                      <TextField
                        fullWidth
                        type="number"
                        label="동전주 기준가격 (원)"
                        value={config.universe.pennyStockPrice}
                        onChange={(e) => setConfig({
                          ...config,
                          universe: { ...config.universe, pennyStockPrice: parseInt(e.target.value) }
                        })}
                        sx={{ mt: 1 }}
                        helperText="이 가격 미만의 종목을 제외"
                      />
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 섹터 설정 탭 */}
          <TabPanel value={currentTab} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      포함 섹터
                    </Typography>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      투자 대상에 포함할 섹터를 선택하세요
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      {SECTORS.map(sector => (
                        <Chip
                          key={sector}
                          label={sector}
                          onClick={() => toggleSector(sector, 'include')}
                          color={config.sectors.include.includes(sector) ? 'primary' : 'default'}
                          sx={{ m: 0.5 }}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="error">
                      제외 섹터
                    </Typography>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      투자에서 제외할 섹터를 선택하세요
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      {SECTORS.map(sector => (
                        <Chip
                          key={sector}
                          label={sector}
                          onClick={() => toggleSector(sector, 'exclude')}
                          color={config.sectors.exclude.includes(sector) ? 'error' : 'default'}
                          sx={{ m: 0.5 }}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      섹터별 가중치 및 분석
                    </Typography>
                    
                    <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={config.sectors.correlationAnalysis}
                            onChange={(e) => setConfig({
                              ...config,
                              sectors: { ...config.sectors, correlationAnalysis: e.target.checked }
                            })}
                          />
                        }
                        label="상관관계 분석"
                      />
                      
                      <FormControlLabel
                        control={
                          <Switch
                            checked={config.sectors.sectorRotation}
                            onChange={(e) => setConfig({
                              ...config,
                              sectors: { ...config.sectors, sectorRotation: e.target.checked }
                            })}
                          />
                        }
                        label="섹터 로테이션"
                      />
                      
                      {config.sectors.sectorRotation && (
                        <FormControl size="small">
                          <Select
                            value={config.sectors.rotationPeriod}
                            onChange={(e) => setConfig({
                              ...config,
                              sectors: { ...config.sectors, rotationPeriod: e.target.value as any }
                            })}
                          >
                            <MenuItem value="weekly">주간</MenuItem>
                            <MenuItem value="monthly">월간</MenuItem>
                            <MenuItem value="quarterly">분기별</MenuItem>
                          </Select>
                        </FormControl>
                      )}
                    </Stack>
                    
                    <List>
                      {config.sectors.sectorIndices.map((sector) => (
                        <ListItem key={sector.code}>
                          <ListItemText
                            primary={sector.name}
                            secondary={
                              <Stack direction="row" spacing={2}>
                                <Typography variant="caption">
                                  가중치: {sector.weight}
                                </Typography>
                                {config.sectors.correlationAnalysis && sector.correlation && (
                                  <Typography variant="caption" color="textSecondary">
                                    상관계수: {sector.correlation.toFixed(2)}
                                  </Typography>
                                )}
                                {sector.performance && (
                                  <Typography 
                                    variant="caption" 
                                    color={sector.performance > 0 ? 'success.main' : 'error.main'}
                                  >
                                    성과: {sector.performance > 0 ? '+' : ''}{sector.performance.toFixed(1)}%
                                  </Typography>
                                )}
                              </Stack>
                            }
                          />
                          <ListItemSecondaryAction>
                            <TextField
                              type="number"
                              value={sector.weight}
                              onChange={(e) => {
                                const updated = config.sectors.sectorIndices.map(s =>
                                  s.code === sector.code ? { ...s, weight: parseFloat(e.target.value) } : s
                                )
                                setConfig({
                                  ...config,
                                  sectors: { ...config.sectors, sectorIndices: updated }
                                })
                              }}
                              inputProps={{ min: 0, max: 2, step: 0.1 }}
                              size="small"
                              sx={{ width: 80, mr: 1 }}
                            />
                            <Switch
                              edge="end"
                              checked={sector.enabled}
                              onChange={(e) => {
                                const updated = config.sectors.sectorIndices.map(s =>
                                  s.code === sector.code ? { ...s, enabled: e.target.checked } : s
                                )
                                setConfig({
                                  ...config,
                                  sectors: { ...config.sectors, sectorIndices: updated }
                                })
                              }}
                            />
                          </ListItemSecondaryAction>
                        </ListItem>
                      ))}
                    </List>
                    
                    <Button
                      variant="outlined"
                      startIcon={<Add />}
                      sx={{ mt: 2 }}
                      onClick={() => {
                        const newSector = {
                          code: `CUSTOM_${Date.now()}`,
                          name: '새 섹터',
                          enabled: true,
                          weight: 1.0,
                          correlation: 0,
                          performance: 0
                        }
                        setConfig({
                          ...config,
                          sectors: {
                            ...config.sectors,
                            sectorIndices: [...config.sectors.sectorIndices, newSector]
                          }
                        })
                      }}
                    >
                      섹터 추가
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 포트폴리오 탭 */}
          <TabPanel value={currentTab} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      포지션 관리
                    </Typography>
                    
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={6}>
                        <TextField
                          fullWidth
                          type="number"
                          label="최대 보유 종목"
                          value={config.portfolio.maxPositions}
                          onChange={(e) => setConfig({
                            ...config,
                            portfolio: { ...config.portfolio, maxPositions: parseInt(e.target.value) }
                          })}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <TextField
                          fullWidth
                          type="number"
                          label="최소 보유 종목"
                          value={config.portfolio.minPositions}
                          onChange={(e) => setConfig({
                            ...config,
                            portfolio: { ...config.portfolio, minPositions: parseInt(e.target.value) }
                          })}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <TextField
                          fullWidth
                          type="number"
                          label="최대 종목 비중 (%)"
                          value={config.portfolio.maxPositionSize}
                          onChange={(e) => setConfig({
                            ...config,
                            portfolio: { ...config.portfolio, maxPositionSize: parseFloat(e.target.value) }
                          })}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <TextField
                          fullWidth
                          type="number"
                          label="최소 종목 비중 (%)"
                          value={config.portfolio.minPositionSize}
                          onChange={(e) => setConfig({
                            ...config,
                            portfolio: { ...config.portfolio, minPositionSize: parseFloat(e.target.value) }
                          })}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          type="number"
                          label="현금 보유 비율 (%)"
                          value={config.portfolio.cashBuffer}
                          onChange={(e) => setConfig({
                            ...config,
                            portfolio: { ...config.portfolio, cashBuffer: parseFloat(e.target.value) }
                          })}
                          helperText="항상 유지할 현금 비율"
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      리밸런싱 설정
                    </Typography>
                    
                    <FormControl fullWidth sx={{ mt: 2 }}>
                      <InputLabel>포지션 사이징 방법</InputLabel>
                      <Select
                        value={config.portfolio.positionSizeMethod}
                        onChange={(e) => setConfig({
                          ...config,
                          portfolio: { ...config.portfolio, positionSizeMethod: e.target.value as any }
                        })}
                        label="포지션 사이징 방법"
                      >
                        <MenuItem value="equal">동일 가중</MenuItem>
                        <MenuItem value="risk_parity">리스크 패리티</MenuItem>
                        <MenuItem value="kelly">켈리 기준</MenuItem>
                        <MenuItem value="market_cap">시가총액 가중</MenuItem>
                        <MenuItem value="custom">사용자 정의</MenuItem>
                      </Select>
                    </FormControl>
                    
                    <FormControl fullWidth sx={{ mt: 2 }}>
                      <InputLabel>리밸런싱 주기</InputLabel>
                      <Select
                        value={config.portfolio.rebalancePeriod}
                        onChange={(e) => setConfig({
                          ...config,
                          portfolio: { ...config.portfolio, rebalancePeriod: e.target.value as any }
                        })}
                        label="리밸런싱 주기"
                      >
                        <MenuItem value="daily">매일</MenuItem>
                        <MenuItem value="weekly">매주</MenuItem>
                        <MenuItem value="monthly">매월</MenuItem>
                        <MenuItem value="quarterly">분기별</MenuItem>
                      </Select>
                    </FormControl>
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="리밸런싱 임계값 (%)"
                      value={config.portfolio.rebalanceThreshold}
                      onChange={(e) => setConfig({
                        ...config,
                        portfolio: { ...config.portfolio, rebalanceThreshold: parseFloat(e.target.value) }
                      })}
                      sx={{ mt: 2 }}
                      helperText="목표 비중과 차이가 이 값을 초과하면 리밸런싱"
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      분산 투자 제약
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          type="number"
                          label="섹터별 최대 비중 (%)"
                          value={config.portfolio.diversification.maxSectorConcentration}
                          onChange={(e) => setConfig({
                            ...config,
                            portfolio: {
                              ...config.portfolio,
                              diversification: {
                                ...config.portfolio.diversification,
                                maxSectorConcentration: parseFloat(e.target.value)
                              }
                            }
                          })}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          type="number"
                          label="개별 종목 최대 비중 (%)"
                          value={config.portfolio.diversification.maxStockConcentration}
                          onChange={(e) => setConfig({
                            ...config,
                            portfolio: {
                              ...config.portfolio,
                              diversification: {
                                ...config.portfolio.diversification,
                                maxStockConcentration: parseFloat(e.target.value)
                              }
                            }
                          })}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          type="number"
                          label="최소 상관계수"
                          value={config.portfolio.diversification.minCorrelation}
                          onChange={(e) => setConfig({
                            ...config,
                            portfolio: {
                              ...config.portfolio,
                              diversification: {
                                ...config.portfolio.diversification,
                                minCorrelation: parseFloat(e.target.value)
                              }
                            }
                          })}
                          inputProps={{ min: 0, max: 1, step: 0.1 }}
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 리스크 관리 탭 */}
          <TabPanel value={currentTab} index={3}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Alert severity="warning" icon={<Warning />}>
                  리스크 관리는 투자의 핵심입니다. 신중하게 설정하세요.
                </Alert>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      손실 제한
                    </Typography>
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="최대 허용 손실 (MDD) %"
                      value={config.risk.maxDrawdown}
                      onChange={(e) => setConfig({
                        ...config,
                        risk: { ...config.risk, maxDrawdown: parseFloat(e.target.value) }
                      })}
                      sx={{ mt: 2 }}
                      helperText="포트폴리오 전체의 최대 허용 손실"
                    />
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="개별 종목 손절매 (%)"
                      value={config.risk.stopLoss}
                      onChange={(e) => setConfig({
                        ...config,
                        risk: { ...config.risk, stopLoss: parseFloat(e.target.value) }
                      })}
                      sx={{ mt: 2 }}
                    />
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="개별 종목 익절매 (%)"
                      value={config.risk.takeProfit}
                      onChange={(e) => setConfig({
                        ...config,
                        risk: { ...config.risk, takeProfit: parseFloat(e.target.value) }
                      })}
                      sx={{ mt: 2 }}
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.risk.trailingStop}
                          onChange={(e) => setConfig({
                            ...config,
                            risk: { ...config.risk, trailingStop: e.target.checked }
                          })}
                        />
                      }
                      label="추적 손절 사용"
                      sx={{ mt: 2 }}
                    />
                    
                    {config.risk.trailingStop && (
                      <TextField
                        fullWidth
                        type="number"
                        label="추적 손절 비율 (%)"
                        value={config.risk.trailingStopPercent}
                        onChange={(e) => setConfig({
                          ...config,
                          risk: { ...config.risk, trailingStopPercent: parseFloat(e.target.value) }
                        })}
                        sx={{ mt: 1 }}
                      />
                    )}
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.risk.timeStop}
                          onChange={(e) => setConfig({
                            ...config,
                            risk: { ...config.risk, timeStop: e.target.checked }
                          })}
                        />
                      }
                      label="시간 손절 사용"
                      sx={{ mt: 2 }}
                    />
                    
                    {config.risk.timeStop && (
                      <TextField
                        fullWidth
                        type="number"
                        label="시간 손절 일수"
                        value={config.risk.timeStopDays}
                        onChange={(e) => setConfig({
                          ...config,
                          risk: { ...config.risk, timeStopDays: parseInt(e.target.value) }
                        })}
                        sx={{ mt: 1 }}
                        helperText="보유 기간이 이 일수를 초과하면 청산"
                      />
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      고급 리스크 관리
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.risk.positionScaling}
                          onChange={(e) => setConfig({
                            ...config,
                            risk: { ...config.risk, positionScaling: e.target.checked }
                          })}
                        />
                      }
                      label="포지션 스케일링 사용"
                      sx={{ mb: 2 }}
                    />
                    
                    {config.risk.positionScaling && (
                      <>
                        <TextField
                          fullWidth
                          type="number"
                          label="추가 매수 기준 (%)"
                          value={config.risk.scaleInThreshold}
                          onChange={(e) => setConfig({
                            ...config,
                            risk: { ...config.risk, scaleInThreshold: parseFloat(e.target.value) }
                          })}
                          sx={{ mb: 2 }}
                          helperText="하락 시 추가 매수할 기준"
                        />
                        
                        <TextField
                          fullWidth
                          type="number"
                          label="부분 매도 기준 (%)"
                          value={config.risk.scaleOutThreshold}
                          onChange={(e) => setConfig({
                            ...config,
                            risk: { ...config.risk, scaleOutThreshold: parseFloat(e.target.value) }
                          })}
                          helperText="상승 시 부분 매도할 기준"
                        />
                      </>
                    )}
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.risk.volatilityFilter}
                          onChange={(e) => setConfig({
                            ...config,
                            risk: { ...config.risk, volatilityFilter: e.target.checked }
                          })}
                        />
                      }
                      label="변동성 필터 사용"
                      sx={{ mt: 2 }}
                    />
                    
                    {config.risk.volatilityFilter && (
                      <TextField
                        fullWidth
                        type="number"
                        label="최대 변동성 (%)"
                        value={config.risk.maxVolatility}
                        onChange={(e) => setConfig({
                          ...config,
                          risk: { ...config.risk, maxVolatility: parseFloat(e.target.value) }
                        })}
                        sx={{ mt: 1 }}
                        helperText="이 값을 초과하는 변동성에서는 거래 중지"
                      />
                    )}
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="subtitle1" gutterBottom>
                      헤징 전략
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.risk.hedging.enabled}
                          onChange={(e) => setConfig({
                            ...config,
                            risk: {
                              ...config.risk,
                              hedging: { ...config.risk.hedging, enabled: e.target.checked }
                            }
                          })}
                        />
                      }
                      label="헤징 사용"
                    />
                    
                    {config.risk.hedging.enabled && (
                      <>
                        <FormControl fullWidth sx={{ mt: 2 }}>
                          <InputLabel>헤징 방법</InputLabel>
                          <Select
                            value={config.risk.hedging.method}
                            onChange={(e) => setConfig({
                              ...config,
                              risk: {
                                ...config.risk,
                                hedging: { ...config.risk.hedging, method: e.target.value as any }
                              }
                            })}
                            label="헤징 방법"
                          >
                            <MenuItem value="futures">선물</MenuItem>
                            <MenuItem value="options">옵션</MenuItem>
                            <MenuItem value="inverse_etf">인버스 ETF</MenuItem>
                          </Select>
                        </FormControl>
                        
                        <TextField
                          fullWidth
                          type="number"
                          label="헤지 비율"
                          value={config.risk.hedging.hedgeRatio}
                          onChange={(e) => setConfig({
                            ...config,
                            risk: {
                              ...config.risk,
                              hedging: { ...config.risk.hedging, hedgeRatio: parseFloat(e.target.value) }
                            }
                          })}
                          sx={{ mt: 2 }}
                          inputProps={{ min: 0, max: 1, step: 0.1 }}
                        />
                      </>
                    )}
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="subtitle1" gutterBottom>
                      시스템 컷 설정
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.risk.systemCut.enabled}
                          onChange={(e) => setConfig({
                            ...config,
                            risk: {
                              ...config.risk,
                              systemCut: { ...config.risk.systemCut, enabled: e.target.checked }
                            }
                          })}
                        />
                      }
                      label="시스템 컷 사용"
                    />
                    
                    {config.risk.systemCut.enabled && (
                      <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="일일 최대 손실 (%)"
                            value={config.risk.systemCut.maxDailyLoss}
                            onChange={(e) => setConfig({
                              ...config,
                              risk: {
                                ...config.risk,
                                systemCut: { ...config.risk.systemCut, maxDailyLoss: parseFloat(e.target.value) }
                              }
                            })}
                          />
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="주간 최대 손실 (%)"
                            value={config.risk.systemCut.maxWeeklyLoss}
                            onChange={(e) => setConfig({
                              ...config,
                              risk: {
                                ...config.risk,
                                systemCut: { ...config.risk.systemCut, maxWeeklyLoss: parseFloat(e.target.value) }
                              }
                            })}
                          />
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="월간 최대 손실 (%)"
                            value={config.risk.systemCut.maxMonthlyLoss}
                            onChange={(e) => setConfig({
                              ...config,
                              risk: {
                                ...config.risk,
                                systemCut: { ...config.risk.systemCut, maxMonthlyLoss: parseFloat(e.target.value) }
                              }
                            })}
                          />
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            type="number"
                            label="연속 손실 횟수"
                            value={config.risk.systemCut.maxConsecutiveLosses}
                            onChange={(e) => setConfig({
                              ...config,
                              risk: {
                                ...config.risk,
                                systemCut: { ...config.risk.systemCut, maxConsecutiveLosses: parseInt(e.target.value) }
                              }
                            })}
                          />
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <FormControl fullWidth>
                            <InputLabel>컷 발생시 동작</InputLabel>
                            <Select
                              value={config.risk.systemCut.action}
                              onChange={(e) => setConfig({
                                ...config,
                                risk: {
                                  ...config.risk,
                                  systemCut: { ...config.risk.systemCut, action: e.target.value as any }
                                }
                              })}
                              label="컷 발생시 동작"
                            >
                              <MenuItem value="stop">완전 정지</MenuItem>
                              <MenuItem value="pause">일시 정지</MenuItem>
                              <MenuItem value="reduce">포지션 축소</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          {config.risk.systemCut.action === 'pause' && (
                            <TextField
                              fullWidth
                              type="number"
                              label="일시정지 기간 (분)"
                              value={config.risk.systemCut.pauseDuration}
                              onChange={(e) => setConfig({
                                ...config,
                                risk: {
                                  ...config.risk,
                                  systemCut: { ...config.risk.systemCut, pauseDuration: parseInt(e.target.value) }
                                }
                              })}
                            />
                          )}
                          {config.risk.systemCut.action === 'reduce' && (
                            <TextField
                              fullWidth
                              type="number"
                              label="포지션 축소 비율"
                              value={config.risk.systemCut.reducePositionRatio}
                              onChange={(e) => setConfig({
                                ...config,
                                risk: {
                                  ...config.risk,
                                  systemCut: { ...config.risk.systemCut, reducePositionRatio: parseFloat(e.target.value) }
                                }
                              })}
                              inputProps={{ min: 0, max: 1, step: 0.1 }}
                            />
                          )}
                        </Grid>
                      </Grid>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 업종 대비 탭 */}
          <TabPanel value={currentTab} index={4}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      업종 지수 대비 분석
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.sectorComparison.enabled}
                          onChange={(e) => setConfig({
                            ...config,
                            sectorComparison: { ...config.sectorComparison, enabled: e.target.checked }
                          })}
                        />
                      }
                      label="업종 대비 분석 사용"
                      sx={{ mb: 2 }}
                    />
                    
                    {config.sectorComparison.enabled && (
                      <>
                        <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                          비교 대상 지수
                        </Typography>
                        
                        <List>
                          {config.sectorComparison.mainIndices.map((index) => (
                            <ListItem key={index.code}>
                              <ListItemText
                                primary={index.name}
                                secondary={`시간프레임: ${index.timeframe}`}
                              />
                              <ListItemSecondaryAction>
                                <Switch
                                  edge="end"
                                  checked={index.enabled}
                                  onChange={(e) => {
                                    const updated = config.sectorComparison.mainIndices.map(i =>
                                      i.code === index.code ? { ...i, enabled: e.target.checked } : i
                                    )
                                    setConfig({
                                      ...config,
                                      sectorComparison: { ...config.sectorComparison, mainIndices: updated }
                                    })
                                  }}
                                />
                              </ListItemSecondaryAction>
                            </ListItem>
                          ))}
                        </List>
                        
                        <FormControl fullWidth sx={{ mt: 2 }}>
                          <InputLabel>비교 방법</InputLabel>
                          <Select
                            value={config.sectorComparison.comparison}
                            onChange={(e) => setConfig({
                              ...config,
                              sectorComparison: { ...config.sectorComparison, comparison: e.target.value as any }
                            })}
                            label="비교 방법"
                          >
                            <MenuItem value="outperform">상회 성과</MenuItem>
                            <MenuItem value="underperform">하회 성과</MenuItem>
                            <MenuItem value="correlation">상관관계</MenuItem>
                          </Select>
                        </FormControl>
                        
                        <TextField
                          fullWidth
                          type="number"
                          label="임계값 (%)"
                          value={config.sectorComparison.threshold}
                          onChange={(e) => setConfig({
                            ...config,
                            sectorComparison: { ...config.sectorComparison, threshold: parseFloat(e.target.value) }
                          })}
                          sx={{ mt: 2 }}
                          helperText="업종 대비 성과 차이 기준"
                        />
                      </>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 매매 설정 탭 */}
          <TabPanel value={currentTab} index={5}>
            <Grid container spacing={3}>
              {/* 분할매매 설정 */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      분할매매 설정
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.trading.splitTrading.enabled}
                          onChange={(e) => setConfig({
                            ...config,
                            trading: {
                              ...config.trading,
                              splitTrading: { ...config.trading.splitTrading, enabled: e.target.checked }
                            }
                          })}
                        />
                      }
                      label="분할매매 사용"
                      sx={{ mb: 2 }}
                    />
                    
                    {config.trading.splitTrading.enabled && (
                      <>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <Typography variant="subtitle2" gutterBottom>
                              매수 분할 레벨 (%)
                            </Typography>
                            <Stack spacing={2}>
                              {config.trading.splitTrading.buyLevels.map((level, index) => (
                                <Stack key={index} direction="row" spacing={2} alignItems="center">
                                  <TextField
                                    size="small"
                                    type="number"
                                    label={`${index + 1}차 매수`}
                                    value={level}
                                    onChange={(e) => {
                                      const newLevels = [...config.trading.splitTrading.buyLevels]
                                      newLevels[index] = parseFloat(e.target.value)
                                      setConfig({
                                        ...config,
                                        trading: {
                                          ...config.trading,
                                          splitTrading: { ...config.trading.splitTrading, buyLevels: newLevels }
                                        }
                                      })
                                    }}
                                    sx={{ flex: 1 }}
                                  />
                                  <TextField
                                    size="small"
                                    type="number"
                                    label="비율"
                                    value={config.trading.splitTrading.buyRatios[index]}
                                    onChange={(e) => {
                                      const newRatios = [...config.trading.splitTrading.buyRatios]
                                      newRatios[index] = parseFloat(e.target.value)
                                      setConfig({
                                        ...config,
                                        trading: {
                                          ...config.trading,
                                          splitTrading: { ...config.trading.splitTrading, buyRatios: newRatios }
                                        }
                                      })
                                    }}
                                    inputProps={{ min: 0, max: 1, step: 0.1 }}
                                    sx={{ width: 80 }}
                                  />
                                  {index === config.trading.splitTrading.buyLevels.length - 1 && (
                                    <IconButton
                                      size="small"
                                      onClick={() => {
                                        setConfig({
                                          ...config,
                                          trading: {
                                            ...config.trading,
                                            splitTrading: {
                                              ...config.trading.splitTrading,
                                              buyLevels: [...config.trading.splitTrading.buyLevels, -10],
                                              buyRatios: [...config.trading.splitTrading.buyRatios, 0.3]
                                            }
                                          }
                                        })
                                      }}
                                    >
                                      <Add />
                                    </IconButton>
                                  )}
                                  {config.trading.splitTrading.buyLevels.length > 1 && (
                                    <IconButton
                                      size="small"
                                      onClick={() => {
                                        const newLevels = config.trading.splitTrading.buyLevels.filter((_, i) => i !== index)
                                        const newRatios = config.trading.splitTrading.buyRatios.filter((_, i) => i !== index)
                                        setConfig({
                                          ...config,
                                          trading: {
                                            ...config.trading,
                                            splitTrading: {
                                              ...config.trading.splitTrading,
                                              buyLevels: newLevels,
                                              buyRatios: newRatios
                                            }
                                          }
                                        })
                                      }}
                                    >
                                      <Remove />
                                    </IconButton>
                                  )}
                                </Stack>
                              ))}
                            </Stack>
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <Typography variant="subtitle2" gutterBottom>
                              매도 분할 레벨 (%)
                            </Typography>
                            <Stack spacing={2}>
                              {config.trading.splitTrading.sellLevels.map((level, index) => (
                                <Stack key={index} direction="row" spacing={2} alignItems="center">
                                  <TextField
                                    size="small"
                                    type="number"
                                    label={`${index + 1}차 매도`}
                                    value={level}
                                    onChange={(e) => {
                                      const newLevels = [...config.trading.splitTrading.sellLevels]
                                      newLevels[index] = parseFloat(e.target.value)
                                      setConfig({
                                        ...config,
                                        trading: {
                                          ...config.trading,
                                          splitTrading: { ...config.trading.splitTrading, sellLevels: newLevels }
                                        }
                                      })
                                    }}
                                    sx={{ flex: 1 }}
                                  />
                                  <TextField
                                    size="small"
                                    type="number"
                                    label="비율"
                                    value={config.trading.splitTrading.sellRatios[index]}
                                    onChange={(e) => {
                                      const newRatios = [...config.trading.splitTrading.sellRatios]
                                      newRatios[index] = parseFloat(e.target.value)
                                      setConfig({
                                        ...config,
                                        trading: {
                                          ...config.trading,
                                          splitTrading: { ...config.trading.splitTrading, sellRatios: newRatios }
                                        }
                                      })
                                    }}
                                    inputProps={{ min: 0, max: 1, step: 0.1 }}
                                    sx={{ width: 80 }}
                                  />
                                  {index === config.trading.splitTrading.sellLevels.length - 1 && (
                                    <IconButton
                                      size="small"
                                      onClick={() => {
                                        setConfig({
                                          ...config,
                                          trading: {
                                            ...config.trading,
                                            splitTrading: {
                                              ...config.trading.splitTrading,
                                              sellLevels: [...config.trading.splitTrading.sellLevels, 15],
                                              sellRatios: [...config.trading.splitTrading.sellRatios, 0.3]
                                            }
                                          }
                                        })
                                      }}
                                    >
                                      <Add />
                                    </IconButton>
                                  )}
                                  {config.trading.splitTrading.sellLevels.length > 1 && (
                                    <IconButton
                                      size="small"
                                      onClick={() => {
                                        const newLevels = config.trading.splitTrading.sellLevels.filter((_, i) => i !== index)
                                        const newRatios = config.trading.splitTrading.sellRatios.filter((_, i) => i !== index)
                                        setConfig({
                                          ...config,
                                          trading: {
                                            ...config.trading,
                                            splitTrading: {
                                              ...config.trading.splitTrading,
                                              sellLevels: newLevels,
                                              sellRatios: newRatios
                                            }
                                          }
                                        })
                                      }}
                                    >
                                      <Remove />
                                    </IconButton>
                                  )}
                                </Stack>
                              ))}
                            </Stack>
                          </Grid>
                        </Grid>
                        
                        <Divider sx={{ my: 3 }} />
                        
                        <FormControlLabel
                          control={
                            <Switch
                              checked={config.trading.splitTrading.useTimeBasedSplit}
                              onChange={(e) => setConfig({
                                ...config,
                                trading: {
                                  ...config.trading,
                                  splitTrading: { ...config.trading.splitTrading, useTimeBasedSplit: e.target.checked }
                                }
                              })}
                            />
                          }
                          label="시간 기반 분할매매"
                          sx={{ mt: 2 }}
                        />
                        
                        {config.trading.splitTrading.useTimeBasedSplit && (
                          <Grid container spacing={2} sx={{ mt: 1 }}>
                            {config.trading.splitTrading.timeIntervals.map((interval, index) => (
                              <Grid item xs={12} sm={4} key={index}>
                                <TextField
                                  fullWidth
                                  type="number"
                                  label={`${index + 1}차 매매 간격 (분)`}
                                  value={interval}
                                  onChange={(e) => {
                                    const newIntervals = [...config.trading.splitTrading.timeIntervals]
                                    newIntervals[index] = parseInt(e.target.value)
                                    setConfig({
                                      ...config,
                                      trading: {
                                        ...config.trading,
                                        splitTrading: { ...config.trading.splitTrading, timeIntervals: newIntervals }
                                      }
                                    })
                                  }}
                                />
                              </Grid>
                            ))}
                          </Grid>
                        )}
                      </>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      주문 설정
                    </Typography>
                    
                    <FormControl fullWidth sx={{ mt: 2 }}>
                      <InputLabel>주문 유형</InputLabel>
                      <Select
                        value={config.trading.orderType}
                        onChange={(e) => setConfig({
                          ...config,
                          trading: { ...config.trading, orderType: e.target.value as any }
                        })}
                        label="주문 유형"
                      >
                        <MenuItem value="market">시장가</MenuItem>
                        <MenuItem value="limit">지정가</MenuItem>
                        <MenuItem value="stop">스톱</MenuItem>
                        <MenuItem value="stop_limit">스톱 리밋</MenuItem>
                      </Select>
                    </FormControl>
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="슬리피지 허용치 (%)"
                      value={config.trading.slippage}
                      onChange={(e) => setConfig({
                        ...config,
                        trading: { ...config.trading, slippage: parseFloat(e.target.value) }
                      })}
                      sx={{ mt: 2 }}
                    />
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="수수료율 (%)"
                      value={config.trading.commission}
                      onChange={(e) => setConfig({
                        ...config,
                        trading: { ...config.trading, commission: parseFloat(e.target.value) }
                      })}
                      sx={{ mt: 2 }}
                    />
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="세금율 (%)"
                      value={config.trading.tax}
                      onChange={(e) => setConfig({
                        ...config,
                        trading: { ...config.trading, tax: parseFloat(e.target.value) }
                      })}
                      sx={{ mt: 2 }}
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      거래 금액 제한
                    </Typography>
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="최소 거래 금액 (원)"
                      value={config.trading.minTradeAmount}
                      onChange={(e) => setConfig({
                        ...config,
                        trading: { ...config.trading, minTradeAmount: parseInt(e.target.value) }
                      })}
                      sx={{ mt: 2 }}
                    />
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="최대 거래 금액 (원)"
                      value={config.trading.maxTradeAmount}
                      onChange={(e) => setConfig({
                        ...config,
                        trading: { ...config.trading, maxTradeAmount: parseInt(e.target.value) }
                      })}
                      sx={{ mt: 2 }}
                    />
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="subtitle1" gutterBottom>
                      거래 시간
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <TextField
                          fullWidth
                          type="time"
                          label="시작 시간"
                          value={config.trading.tradingHours.start}
                          onChange={(e) => setConfig({
                            ...config,
                            trading: {
                              ...config.trading,
                              tradingHours: { ...config.trading.tradingHours, start: e.target.value }
                            }
                          })}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <TextField
                          fullWidth
                          type="time"
                          label="종료 시간"
                          value={config.trading.tradingHours.end}
                          onChange={(e) => setConfig({
                            ...config,
                            trading: {
                              ...config.trading,
                              tradingHours: { ...config.trading.tradingHours, end: e.target.value }
                            }
                          })}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                    </Grid>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.trading.tradingHours.preMarketTrading}
                          onChange={(e) => setConfig({
                            ...config,
                            trading: {
                              ...config.trading,
                              tradingHours: { ...config.trading.tradingHours, preMarketTrading: e.target.checked }
                            }
                          })}
                        />
                      }
                      label="시간외 거래 (장전)"
                      sx={{ mt: 2 }}
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.trading.tradingHours.afterHoursTrading}
                          onChange={(e) => setConfig({
                            ...config,
                            trading: {
                              ...config.trading,
                              tradingHours: { ...config.trading.tradingHours, afterHoursTrading: e.target.checked }
                            }
                          })}
                        />
                      }
                      label="시간외 거래 (장후)"
                    />
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 자동화 탭 */}
          <TabPanel value={currentTab} index={6}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      자동 실행 설정
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.automation.autoStart}
                          onChange={(e) => setConfig({
                            ...config,
                            automation: { ...config.automation, autoStart: e.target.checked }
                          })}
                        />
                      }
                      label="자동 시작"
                      sx={{ mb: 2 }}
                    />
                    
                    {config.automation.autoStart && (
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            type="time"
                            label="자동 시작 시간"
                            value={config.automation.autoStartTime}
                            onChange={(e) => setConfig({
                              ...config,
                              automation: { ...config.automation, autoStartTime: e.target.value }
                            })}
                            InputLabelProps={{ shrink: true }}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            type="time"
                            label="자동 종료 시간"
                            value={config.automation.autoStopTime}
                            onChange={(e) => setConfig({
                              ...config,
                              automation: { ...config.automation, autoStopTime: e.target.value }
                            })}
                            InputLabelProps={{ shrink: true }}
                          />
                        </Grid>
                      </Grid>
                    )}
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.automation.weekendTrading}
                          onChange={(e) => setConfig({
                            ...config,
                            automation: { ...config.automation, weekendTrading: e.target.checked }
                          })}
                        />
                      }
                      label="주말 거래"
                      sx={{ mt: 2 }}
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.automation.holidayTrading}
                          onChange={(e) => setConfig({
                            ...config,
                            automation: { ...config.automation, holidayTrading: e.target.checked }
                          })}
                        />
                      }
                      label="공휴일 거래"
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      비상 정지 설정
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.automation.emergencyStop.enabled}
                          onChange={(e) => setConfig({
                            ...config,
                            automation: {
                              ...config.automation,
                              emergencyStop: { ...config.automation.emergencyStop, enabled: e.target.checked }
                            }
                          })}
                        />
                      }
                      label="비상 정지 사용"
                      sx={{ mb: 2 }}
                    />
                    
                    {config.automation.emergencyStop.enabled && (
                      <>
                        <TextField
                          fullWidth
                          type="number"
                          label="일일 최대 손실 (%)"
                          value={config.automation.emergencyStop.maxDailyLoss}
                          onChange={(e) => setConfig({
                            ...config,
                            automation: {
                              ...config.automation,
                              emergencyStop: { ...config.automation.emergencyStop, maxDailyLoss: parseFloat(e.target.value) }
                            }
                          })}
                          sx={{ mb: 2 }}
                        />
                        
                        <TextField
                          fullWidth
                          type="number"
                          label="최대 연속 손실 횟수"
                          value={config.automation.emergencyStop.maxConsecutiveLosses}
                          onChange={(e) => setConfig({
                            ...config,
                            automation: {
                              ...config.automation,
                              emergencyStop: { ...config.automation.emergencyStop, maxConsecutiveLosses: parseInt(e.target.value) }
                            }
                          })}
                          sx={{ mb: 2 }}
                        />
                        
                        <FormControl fullWidth>
                          <InputLabel>시스템 오류 시 동작</InputLabel>
                          <Select
                            value={config.automation.emergencyStop.systemErrorAction}
                            onChange={(e) => setConfig({
                              ...config,
                              automation: {
                                ...config.automation,
                                emergencyStop: { ...config.automation.emergencyStop, systemErrorAction: e.target.value as any }
                              }
                            })}
                            label="시스템 오류 시 동작"
                          >
                            <MenuItem value="stop">정지</MenuItem>
                            <MenuItem value="pause">일시정지</MenuItem>
                            <MenuItem value="continue">계속</MenuItem>
                          </Select>
                        </FormControl>
                      </>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 알림 탭 */}
          <TabPanel value={currentTab} index={7}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      이메일 알림
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.notifications.email.enabled}
                          onChange={(e) => setConfig({
                            ...config,
                            notifications: {
                              ...config.notifications,
                              email: { ...config.notifications.email, enabled: e.target.checked }
                            }
                          })}
                        />
                      }
                      label="이메일 알림 사용"
                      sx={{ mb: 2 }}
                    />
                    
                    {config.notifications.email.enabled && (
                      <>
                        <TextField
                          fullWidth
                          label="이메일 주소"
                          value={config.notifications.email.address}
                          onChange={(e) => setConfig({
                            ...config,
                            notifications: {
                              ...config.notifications,
                              email: { ...config.notifications.email, address: e.target.value }
                            }
                          })}
                          sx={{ mb: 2 }}
                        />
                        
                        <Typography variant="subtitle2" gutterBottom>
                          알림 받을 이벤트
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {NOTIFICATION_EVENTS.map(event => (
                            <Chip
                              key={event}
                              label={event}
                              size="small"
                              color={config.notifications.email.events.includes(event) ? 'primary' : 'default'}
                              onClick={() => {
                                const events = config.notifications.email.events.includes(event)
                                  ? config.notifications.email.events.filter(e => e !== event)
                                  : [...config.notifications.email.events, event]
                                setConfig({
                                  ...config,
                                  notifications: {
                                    ...config.notifications,
                                    email: { ...config.notifications.email, events }
                                  }
                                })
                              }}
                            />
                          ))}
                        </Box>
                      </>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      카카오톡 알림
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.notifications.kakao.enabled}
                          onChange={(e) => setConfig({
                            ...config,
                            notifications: {
                              ...config.notifications,
                              kakao: { ...config.notifications.kakao, enabled: e.target.checked }
                            }
                          })}
                        />
                      }
                      label="카카오톡 알림 사용"
                      sx={{ mb: 2 }}
                    />
                    
                    {config.notifications.kakao.enabled && (
                      <>
                        <TextField
                          fullWidth
                          label="카카오톡 토큰"
                          value={config.notifications.kakao.token}
                          onChange={(e) => setConfig({
                            ...config,
                            notifications: {
                              ...config.notifications,
                              kakao: { ...config.notifications.kakao, token: e.target.value }
                            }
                          })}
                          sx={{ mb: 2 }}
                        />
                        
                        <Typography variant="subtitle2" gutterBottom>
                          알림 받을 이벤트
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {NOTIFICATION_EVENTS.map(event => (
                            <Chip
                              key={event}
                              label={event}
                              size="small"
                              color={config.notifications.kakao.events.includes(event) ? 'primary' : 'default'}
                              onClick={() => {
                                const events = config.notifications.kakao.events.includes(event)
                                  ? config.notifications.kakao.events.filter(e => e !== event)
                                  : [...config.notifications.kakao.events, event]
                                setConfig({
                                  ...config,
                                  notifications: {
                                    ...config.notifications,
                                    kakao: { ...config.notifications.kakao, events }
                                  }
                                })
                              }}
                            />
                          ))}
                        </Box>
                      </>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>
        </Paper>
        
        {/* 저장 완료 메시지와 메인으로 돌아가기 안내 */}
        {message && (
          <Alert 
            severity="success" 
            sx={{ mt: 2 }}
            action={
              <Button color="inherit" size="small" onClick={() => navigate('/')}>
                메인으로
              </Button>
            }
          >
            {message}
          </Alert>
        )}
      </Box>
      
      {/* 플로팅 액션 버튼 - 메인으로 돌아가기 */}
      <Tooltip title="메인 화면으로 돌아가기">
        <IconButton
          onClick={() => navigate('/')}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            bgcolor: 'primary.main',
            color: 'white',
            width: 56,
            height: 56,
            boxShadow: 3,
            '&:hover': {
              bgcolor: 'primary.dark',
              transform: 'scale(1.1)',
            },
            transition: 'all 0.3s',
            zIndex: 1000
          }}
        >
          <Home />
        </IconButton>
      </Tooltip>
    </Container>
  )
}

export default InvestmentSettingsComplete