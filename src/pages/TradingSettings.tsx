import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Grid,
  FormControl,
  FormLabel,
  FormGroup,
  FormControlLabel,
  Checkbox,
  RadioGroup,
  Radio,
  Select,
  MenuItem,
  Slider,
  TextField,
  Button,
  Divider,
  Chip,
  Stack,
  Alert,
  Switch,
  InputAdornment,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  InputLabel
} from '@mui/material'
import {
  Settings,
  TrendingUp,
  AccountBalance,
  Warning,
  Info,
  Save,
  RestartAlt,
  Analytics,
  Security,
  ShowChart,
  TrendingDown,
  CompareArrows,
  FilterList,
  Business,
  Shield
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
      id={`trading-tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const TradingSettings: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  
  // 투자유니버스 설정
  const [universe, setUniverse] = useState({
    marketCap: [100, 50000], // 억원
    per: [5, 25],
    pbr: [0.5, 3],
    roe: [5, 30], // %
    debtRatio: [0, 100], // %
    tradingVolume: [100, 10000], // 백만원
    sectors: ['IT/소프트웨어', '반도체', '2차전지', '바이오/헬스케어'],
    excludeSectors: ['건설/부동산', '조선/기계']
  })
  
  // 매매 조건 설정
  const [tradingConditions, setTradingConditions] = useState({
    timeframe: '일봉',
    indicators: ['RSI', 'MACD', '일목균형표'],
    buyConditions: {
      rsi: { enabled: true, value: 30, operator: '<' },
      macd: { enabled: true, crossover: true },
      ichimoku: { enabled: true, condition: '구름대 상단 돌파' },
      volume: { enabled: true, multiplier: 1.5 },
      sectorIndex: { 
        enabled: false, 
        comparison: 'outperform', // outperform, underperform, correlation
        threshold: 5, // %
        sectors: ['KOSPI', 'KOSDAQ']
      }
    },
    sellConditions: {
      profitTarget: { enabled: true, value: 10 },
      stopLoss: { enabled: true, value: -3 },
      trailingStop: { enabled: false, value: 5 },
      timeStop: { enabled: false, days: 30 },
      sectorIndex: {
        enabled: false,
        comparison: 'underperform',
        threshold: -3
      }
    }
  })
  
  // 업종 지표 설정
  const [sectorIndices, setSectorIndices] = useState({
    mainIndices: [
      { code: 'KOSPI', name: 'KOSPI', enabled: true, timeframe: '일봉' },
      { code: 'KOSDAQ', name: 'KOSDAQ', enabled: true, timeframe: '일봉' }
    ],
    indexTimeframes: ['일봉', '주봉', '월봉'],
    sectorIndices: [
      { code: 'IT', name: 'IT/소프트웨어', enabled: true, weight: 1.0 },
      { code: 'BIO', name: '바이오/헬스케어', enabled: true, weight: 1.2 },
      { code: 'SEMI', name: '반도체', enabled: true, weight: 1.5 },
      { code: 'BATTERY', name: '2차전지', enabled: true, weight: 1.3 },
      { code: 'AUTO', name: '자동차', enabled: false, weight: 0.8 },
      { code: 'CONSTRUCT', name: '건설/부동산', enabled: false, weight: 0.5 },
      { code: 'SHIP', name: '조선/기계', enabled: false, weight: 0.7 },
      { code: 'CHEM', name: '화학', enabled: false, weight: 0.9 },
      { code: 'STEEL', name: '철강/소재', enabled: false, weight: 0.6 },
      { code: 'FINANCE', name: '금융', enabled: false, weight: 1.0 },
      { code: 'RETAIL', name: '유통/소비재', enabled: false, weight: 0.8 },
      { code: 'FOOD', name: '식품/음료', enabled: false, weight: 0.7 },
      { code: 'ENTERTAINMENT', name: '엔터테인먼트', enabled: true, weight: 1.1 },
      { code: 'GAME', name: '게임', enabled: true, weight: 1.2 }
    ],
    correlationPeriod: 20, // days
    useRelativeStrength: true,
    strengthPeriod: 60 // days
  })
  
  // 포트폴리오 설정
  const [portfolio, setPortfolio] = useState({
    maxPositions: 20,
    minPositions: 5,
    positionSizeMethod: 'equal', // equal, risk_parity, kelly, custom
    maxPositionSize: 20, // %
    minPositionSize: 3, // %
    cashBuffer: 10, // %
    rebalancePeriod: 'monthly', // daily, weekly, monthly, quarterly
    rebalanceThreshold: 5 // %
  })
  
  // 분할매매 설정
  const [splitTrading, setSplitTrading] = useState({
    enabled: true,
    buyLevels: [
      { level: 1, percentage: 40, trigger: 0 },
      { level: 2, percentage: 30, trigger: -2 },
      { level: 3, percentage: 30, trigger: -5 }
    ],
    sellLevels: [
      { level: 1, percentage: 30, trigger: 3 },
      { level: 2, percentage: 40, trigger: 7 },
      { level: 3, percentage: 30, trigger: 10 }
    ]
  })
  
  // 위험관리 설정
  const [riskManagement, setRiskManagement] = useState({
    maxDrawdown: 20, // %
    stopLoss: -7, // %
    takeProfit: 15, // %
    trailingStop: false,
    trailingStopPercent: 5, // %
    positionScaling: false,
    scaleInThreshold: -3, // %
    scaleOutThreshold: 10, // %
    correlationLimit: 0.7,
    maxDailyLoss: 5, // %
    systemCut: {
      enabled: true,
      consecutiveLosses: 3,
      dailyLossLimit: 5,
      action: 'pause' // pause, stop, reduce
    },
    positionSizing: 'fixed', // fixed, kelly, volatility
    leverage: 1
  })

  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = () => {
    const saved = localStorage.getItem('tradingConfig')
    if (saved) {
      const config = JSON.parse(saved)
      if (config.universe) setUniverse(config.universe)
      if (config.tradingConditions) setTradingConditions(config.tradingConditions)
      if (config.sectorIndices) setSectorIndices(config.sectorIndices)
      if (config.portfolio) setPortfolio(config.portfolio)
      if (config.splitTrading) setSplitTrading(config.splitTrading)
      if (config.riskManagement) setRiskManagement(config.riskManagement)
    }
  }

  const handleSaveSettings = () => {
    setSaving(true)
    const config = {
      universe,
      tradingConditions,
      sectorIndices,
      portfolio,
      splitTrading,
      riskManagement
    }
    localStorage.setItem('tradingConfig', JSON.stringify(config))
    setTimeout(() => {
      setSaving(false)
      setMessage('투자 설정이 저장되었습니다')
      setTimeout(() => setMessage(''), 3000)
    }, 500)
  }

  const resetSettings = () => {
    if (confirm('모든 설정을 초기값으로 되돌리시겠습니까?')) {
      localStorage.removeItem('tradingConfig')
      window.location.reload()
    }
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingUp sx={{ fontSize: 30 }} />
            투자 설정
          </Typography>
          <Stack direction="row" spacing={2}>
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
              onClick={handleSaveSettings}
              disabled={saving}
            >
              저장
            </Button>
          </Stack>
        </Box>

        {message && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setMessage('')}>
            {message}
          </Alert>
        )}

        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
              <Tab icon={<AccountBalance />} label="투자유니버스" />
              <Tab icon={<TrendingUp />} label="매매조건" />
              <Tab icon={<ShowChart />} label="업종지표" />
              <Tab icon={<Business />} label="포트폴리오" />
              <Tab icon={<Analytics />} label="분할매매" />
              <Tab icon={<Security />} label="위험관리" />
            </Tabs>
          </Box>

          {/* 투자유니버스 탭 */}
          <TabPanel value={tabValue} index={0}>
            <Typography variant="h6" gutterBottom>
              투자유니버스 선정 기준
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      시가총액 (억원)
                    </Typography>
                    <Slider
                      value={universe.marketCap}
                      onChange={(e, v) => setUniverse({...universe, marketCap: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100000}
                      marks={[
                        { value: 0, label: '0' },
                        { value: 10000, label: '1조' },
                        { value: 50000, label: '5조' },
                        { value: 100000, label: '10조+' }
                      ]}
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      PER (주가수익비율)
                    </Typography>
                    <Slider
                      value={universe.per}
                      onChange={(e, v) => setUniverse({...universe, per: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={50}
                      marks={[
                        { value: 0, label: '0' },
                        { value: 15, label: '15' },
                        { value: 30, label: '30' },
                        { value: 50, label: '50' }
                      ]}
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      PBR (주가순자산비율)
                    </Typography>
                    <Slider
                      value={universe.pbr}
                      onChange={(e, v) => setUniverse({...universe, pbr: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={10}
                      step={0.1}
                      marks={[
                        { value: 0, label: '0' },
                        { value: 1, label: '1' },
                        { value: 3, label: '3' },
                        { value: 10, label: '10' }
                      ]}
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      ROE (자기자본이익률) %
                    </Typography>
                    <Slider
                      value={universe.roe}
                      onChange={(e, v) => setUniverse({...universe, roe: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                      marks={[
                        { value: 0, label: '0%' },
                        { value: 20, label: '20%' },
                        { value: 50, label: '50%' },
                        { value: 100, label: '100%' }
                      ]}
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      부채비율 %
                    </Typography>
                    <Slider
                      value={universe.debtRatio}
                      onChange={(e, v) => setUniverse({...universe, debtRatio: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={200}
                      marks={[
                        { value: 0, label: '0%' },
                        { value: 50, label: '50%' },
                        { value: 100, label: '100%' },
                        { value: 200, label: '200%' }
                      ]}
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      거래량 (백만원)
                    </Typography>
                    <Slider
                      value={universe.tradingVolume}
                      onChange={(e, v) => setUniverse({...universe, tradingVolume: v as number[]})}
                      valueLabelDisplay="auto"
                      min={0}
                      max={50000}
                      marks={[
                        { value: 0, label: '0' },
                        { value: 1000, label: '10억' },
                        { value: 10000, label: '100억' },
                        { value: 50000, label: '500억' }
                      ]}
                    />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      섹터 필터링
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                      <Typography variant="body2">포함 섹터:</Typography>
                      {universe.sectors.map(sector => (
                        <Chip key={sector} label={sector} color="primary" size="small" />
                      ))}
                    </Stack>
                    <Stack direction="row" spacing={1}>
                      <Typography variant="body2">제외 섹터:</Typography>
                      {universe.excludeSectors.map(sector => (
                        <Chip key={sector} label={sector} color="error" size="small" />
                      ))}
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 매매조건 탭 - 계속 */}
          <TabPanel value={tabValue} index={1}>
            <Typography variant="h6" gutterBottom>
              매매 조건 설정
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControl component="fieldset">
                  <FormLabel component="legend">차트 시간대</FormLabel>
                  <RadioGroup
                    row
                    value={tradingConditions.timeframe}
                    onChange={(e) => setTradingConditions({
                      ...tradingConditions,
                      timeframe: e.target.value
                    })}
                  >
                    <FormControlLabel value="일봉" control={<Radio />} label="일봉" />
                    <FormControlLabel value="주봉" control={<Radio />} label="주봉" />
                    <FormControlLabel value="월봉" control={<Radio />} label="월봉" />
                    <FormControlLabel value="60분" control={<Radio />} label="60분" />
                    <FormControlLabel value="30분" control={<Radio />} label="30분" />
                  </RadioGroup>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      매수 조건
                    </Typography>
                    <FormGroup>
                      <FormControlLabel
                        control={
                          <Checkbox 
                            checked={tradingConditions.buyConditions.rsi.enabled}
                            onChange={(e) => setTradingConditions({
                              ...tradingConditions,
                              buyConditions: {
                                ...tradingConditions.buyConditions,
                                rsi: { ...tradingConditions.buyConditions.rsi, enabled: e.target.checked }
                              }
                            })}
                          />
                        }
                        label={`RSI < ${tradingConditions.buyConditions.rsi.value}`}
                      />
                      <FormControlLabel
                        control={
                          <Checkbox 
                            checked={tradingConditions.buyConditions.macd.enabled}
                          />
                        }
                        label="MACD 골든크로스"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox 
                            checked={tradingConditions.buyConditions.ichimoku.enabled}
                          />
                        }
                        label="일목균형표 구름대 상단 돌파"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox 
                            checked={tradingConditions.buyConditions.volume.enabled}
                          />
                        }
                        label={`거래량 ${tradingConditions.buyConditions.volume.multiplier}배 이상`}
                      />
                    </FormGroup>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      매도 조건
                    </Typography>
                    <Stack spacing={2}>
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={tradingConditions.sellConditions.profitTarget.enabled}
                          />
                        }
                        label={`목표 수익률: ${tradingConditions.sellConditions.profitTarget.value}%`}
                      />
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={tradingConditions.sellConditions.stopLoss.enabled}
                          />
                        }
                        label={`손절 라인: ${tradingConditions.sellConditions.stopLoss.value}%`}
                      />
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={tradingConditions.sellConditions.trailingStop.enabled}
                          />
                        }
                        label={`추적 손절: ${tradingConditions.sellConditions.trailingStop.value}%`}
                      />
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={tradingConditions.sellConditions.timeStop.enabled}
                          />
                        }
                        label={`시간 손절: ${tradingConditions.sellConditions.timeStop.days}일`}
                      />
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 업종지표 탭 */}
          <TabPanel value={tabValue} index={2}>
            <Typography variant="h6" gutterBottom>
              업종지표 활용 설정
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      업종별 지수 설정
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      활성화된 업종 지수를 기준으로 개별 종목의 상대 강도를 평가합니다.
                    </Typography>
                    
                    <Grid container spacing={2}>
                      {sectorIndices.sectorIndices.map(sector => (
                        <Grid item xs={12} sm={6} md={4} key={sector.code}>
                          <Paper variant="outlined" sx={{ p: 2 }}>
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={sector.enabled}
                                  onChange={(e) => {
                                    const updated = sectorIndices.sectorIndices.map(s => 
                                      s.code === sector.code ? {...s, enabled: e.target.checked} : s
                                    )
                                    setSectorIndices({...sectorIndices, sectorIndices: updated})
                                  }}
                                  color={sector.enabled ? 'primary' : 'default'}
                                />
                              }
                              label={sector.name}
                            />
                            {sector.enabled && (
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="caption" color="text.secondary">
                                  가중치
                                </Typography>
                                <Slider
                                  value={sector.weight}
                                  onChange={(e, value) => {
                                    const updated = sectorIndices.sectorIndices.map(s => 
                                      s.code === sector.code ? {...s, weight: value as number} : s
                                    )
                                    setSectorIndices({...sectorIndices, sectorIndices: updated})
                                  }}
                                  min={0.1}
                                  max={2.0}
                                  step={0.1}
                                  valueLabelDisplay="auto"
                                  size="small"
                                />
                              </Box>
                            )}
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 포트폴리오 탭 */}
          <TabPanel value={tabValue} index={3}>
            <Typography variant="h6" gutterBottom>
              포트폴리오 관리
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      포지션 설정
                    </Typography>
                    <Stack spacing={2}>
                      <TextField
                        label="최대 보유 종목수"
                        type="number"
                        value={portfolio.maxPositions}
                        onChange={(e) => setPortfolio({...portfolio, maxPositions: Number(e.target.value)})}
                        fullWidth
                      />
                      <TextField
                        label="최소 보유 종목수"
                        type="number"
                        value={portfolio.minPositions}
                        onChange={(e) => setPortfolio({...portfolio, minPositions: Number(e.target.value)})}
                        fullWidth
                      />
                      <TextField
                        label="최대 종목당 비중"
                        value={portfolio.maxPositionSize}
                        onChange={(e) => setPortfolio({...portfolio, maxPositionSize: Number(e.target.value)})}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                        }}
                        fullWidth
                      />
                      <TextField
                        label="최소 종목당 비중"
                        value={portfolio.minPositionSize}
                        onChange={(e) => setPortfolio({...portfolio, minPositionSize: Number(e.target.value)})}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                        }}
                        fullWidth
                      />
                      <TextField
                        label="현금 보유 비율"
                        value={portfolio.cashBuffer}
                        onChange={(e) => setPortfolio({...portfolio, cashBuffer: Number(e.target.value)})}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                        }}
                        fullWidth
                      />
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      리밸런싱 설정
                    </Typography>
                    <Stack spacing={2}>
                      <FormControl fullWidth>
                        <InputLabel>포지션 사이징 방법</InputLabel>
                        <Select
                          value={portfolio.positionSizeMethod}
                          onChange={(e) => setPortfolio({...portfolio, positionSizeMethod: e.target.value as any})}
                          label="포지션 사이징 방법"
                        >
                          <MenuItem value="equal">동일 가중</MenuItem>
                          <MenuItem value="risk_parity">리스크 패리티</MenuItem>
                          <MenuItem value="kelly">켈리 공식</MenuItem>
                          <MenuItem value="custom">사용자 정의</MenuItem>
                        </Select>
                      </FormControl>
                      <FormControl fullWidth>
                        <InputLabel>리밸런싱 주기</InputLabel>
                        <Select
                          value={portfolio.rebalancePeriod}
                          onChange={(e) => setPortfolio({...portfolio, rebalancePeriod: e.target.value as any})}
                          label="리밸런싱 주기"
                        >
                          <MenuItem value="daily">일별</MenuItem>
                          <MenuItem value="weekly">주별</MenuItem>
                          <MenuItem value="monthly">월별</MenuItem>
                          <MenuItem value="quarterly">분기별</MenuItem>
                        </Select>
                      </FormControl>
                      <TextField
                        label="리밸런싱 임계값"
                        value={portfolio.rebalanceThreshold}
                        onChange={(e) => setPortfolio({...portfolio, rebalanceThreshold: Number(e.target.value)})}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                        }}
                        fullWidth
                        helperText="목표 비중과 현재 비중의 차이가 임계값을 초과하면 리밸런싱"
                      />
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 분할매매 탭 */}
          <TabPanel value={tabValue} index={4}>
            <Typography variant="h6" gutterBottom>
              분할매매 전략
            </Typography>
            
            <FormControlLabel
              control={
                <Switch 
                  checked={splitTrading.enabled}
                  onChange={(e) => setSplitTrading({...splitTrading, enabled: e.target.checked})}
                />
              }
              label="분할매매 활성화"
              sx={{ mb: 3 }}
            />
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      분할 매수 설정
                    </Typography>
                    {splitTrading.buyLevels.map((level, index) => (
                      <Box key={level.level} sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          {level.level}차 매수
                        </Typography>
                        <Stack direction="row" spacing={2} alignItems="center">
                          <TextField
                            label="비중"
                            value={level.percentage}
                            onChange={(e) => {
                              const updated = [...splitTrading.buyLevels]
                              updated[index].percentage = Number(e.target.value)
                              setSplitTrading({...splitTrading, buyLevels: updated})
                            }}
                            InputProps={{
                              endAdornment: <InputAdornment position="end">%</InputAdornment>,
                            }}
                            size="small"
                            sx={{ width: 100 }}
                          />
                          <TextField
                            label="트리거"
                            value={level.trigger}
                            onChange={(e) => {
                              const updated = [...splitTrading.buyLevels]
                              updated[index].trigger = Number(e.target.value)
                              setSplitTrading({...splitTrading, buyLevels: updated})
                            }}
                            InputProps={{
                              endAdornment: <InputAdornment position="end">%</InputAdornment>,
                            }}
                            size="small"
                            sx={{ width: 100 }}
                          />
                        </Stack>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      분할 매도 설정
                    </Typography>
                    {splitTrading.sellLevels.map((level, index) => (
                      <Box key={level.level} sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          {level.level}차 매도
                        </Typography>
                        <Stack direction="row" spacing={2} alignItems="center">
                          <TextField
                            label="비중"
                            value={level.percentage}
                            onChange={(e) => {
                              const updated = [...splitTrading.sellLevels]
                              updated[index].percentage = Number(e.target.value)
                              setSplitTrading({...splitTrading, sellLevels: updated})
                            }}
                            InputProps={{
                              endAdornment: <InputAdornment position="end">%</InputAdornment>,
                            }}
                            size="small"
                            sx={{ width: 100 }}
                          />
                          <TextField
                            label="트리거"
                            value={level.trigger}
                            onChange={(e) => {
                              const updated = [...splitTrading.sellLevels]
                              updated[index].trigger = Number(e.target.value)
                              setSplitTrading({...splitTrading, sellLevels: updated})
                            }}
                            InputProps={{
                              endAdornment: <InputAdornment position="end">%</InputAdornment>,
                            }}
                            size="small"
                            sx={{ width: 100 }}
                          />
                        </Stack>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* 위험관리 탭 */}
          <TabPanel value={tabValue} index={5}>
            <Typography variant="h6" gutterBottom>
              위험관리 시스템
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      손익 관리
                    </Typography>
                    <Stack spacing={2}>
                      <TextField
                        label="최대 낙폭 (Drawdown)"
                        value={riskManagement.maxDrawdown}
                        onChange={(e) => setRiskManagement({
                          ...riskManagement,
                          maxDrawdown: Number(e.target.value)
                        })}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                        }}
                        fullWidth
                      />
                      <TextField
                        label="손절매"
                        value={riskManagement.stopLoss}
                        onChange={(e) => setRiskManagement({
                          ...riskManagement,
                          stopLoss: Number(e.target.value)
                        })}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                        }}
                        fullWidth
                      />
                      <TextField
                        label="익절매"
                        value={riskManagement.takeProfit}
                        onChange={(e) => setRiskManagement({
                          ...riskManagement,
                          takeProfit: Number(e.target.value)
                        })}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">%</InputAdornment>,
                        }}
                        fullWidth
                      />
                      <FormControlLabel
                        control={
                          <Switch
                            checked={riskManagement.trailingStop}
                            onChange={(e) => setRiskManagement({
                              ...riskManagement,
                              trailingStop: e.target.checked
                            })}
                          />
                        }
                        label="추적 손절 사용"
                      />
                      {riskManagement.trailingStop && (
                        <TextField
                          label="추적 손절"
                          value={riskManagement.trailingStopPercent}
                          onChange={(e) => setRiskManagement({
                            ...riskManagement,
                            trailingStopPercent: Number(e.target.value)
                          })}
                          InputProps={{
                            endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          }}
                          fullWidth
                        />
                      )}
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      시스템 CUT 설정
                    </Typography>
                    <FormControlLabel
                      control={
                        <Switch 
                          checked={riskManagement.systemCut.enabled}
                          onChange={(e) => setRiskManagement({
                            ...riskManagement,
                            systemCut: { ...riskManagement.systemCut, enabled: e.target.checked }
                          })}
                        />
                      }
                      label="시스템 CUT 활성화"
                      sx={{ mb: 2 }}
                    />
                    
                    {riskManagement.systemCut.enabled && (
                      <Stack spacing={2}>
                        <TextField
                          label="연속 손실 횟수"
                          value={riskManagement.systemCut.consecutiveLosses}
                          onChange={(e) => setRiskManagement({
                            ...riskManagement,
                            systemCut: { 
                              ...riskManagement.systemCut, 
                              consecutiveLosses: Number(e.target.value)
                            }
                          })}
                          type="number"
                          fullWidth
                        />
                        <TextField
                          label="일일 손실 한도"
                          value={riskManagement.systemCut.dailyLossLimit}
                          onChange={(e) => setRiskManagement({
                            ...riskManagement,
                            systemCut: { 
                              ...riskManagement.systemCut, 
                              dailyLossLimit: Number(e.target.value)
                            }
                          })}
                          InputProps={{
                            endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          }}
                          fullWidth
                        />
                        <FormControl fullWidth>
                          <InputLabel>CUT 발동 시 액션</InputLabel>
                          <Select
                            value={riskManagement.systemCut.action}
                            onChange={(e) => setRiskManagement({
                              ...riskManagement,
                              systemCut: { 
                                ...riskManagement.systemCut, 
                                action: e.target.value as 'pause' | 'stop' | 'reduce'
                              }
                            })}
                            label="CUT 발동 시 액션"
                          >
                            <MenuItem value="pause">일시정지</MenuItem>
                            <MenuItem value="stop">완전정지</MenuItem>
                            <MenuItem value="reduce">포지션 축소</MenuItem>
                          </Select>
                        </FormControl>
                      </Stack>
                    )}
                    
                    <Alert severity="warning" sx={{ mt: 2 }}>
                      시스템 CUT이 발동되면 설정된 액션에 따라 자동으로 매매가 제한됩니다.
                    </Alert>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>
        </Paper>
      </Box>
    </Box>
  )
}

export default TradingSettings