import React, { useState } from 'react'
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
  CardContent
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
  CompareArrows
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
    marketCap: [10, 1000], // 억원
    per: [5, 30],
    pbr: [0.5, 5],
    roe: [5, 50], // %
    debtRatio: [0, 100], // %
    sectors: ['IT', '바이오', '2차전지', '반도체'],
    excludeSectors: ['건설', '조선']
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
      { code: 'CONSTRUCT', name: '건설', enabled: false, weight: 0.5 },
      { code: 'SHIP', name: '조선', enabled: false, weight: 0.7 },
      { code: 'CHEM', name: '화학', enabled: false, weight: 0.9 },
      { code: 'STEEL', name: '철강', enabled: false, weight: 0.6 },
      { code: 'FINANCE', name: '금융', enabled: false, weight: 1.0 },
      { code: 'RETAIL', name: '유통', enabled: false, weight: 0.8 },
      { code: 'FOOD', name: '음식료', enabled: false, weight: 0.7 },
      { code: 'ENTERTAINMENT', name: '엔터테인먼트', enabled: true, weight: 1.1 },
      { code: 'GAME', name: '게임', enabled: true, weight: 1.2 }
    ],
    correlationPeriod: 20, // days
    useRelativeStrength: true,
    strengthPeriod: 60 // days
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
    maxPositionSize: 20, // %
    maxDailyLoss: 5, // %
    maxDrawdown: 10, // %
    systemCut: {
      enabled: true,
      consecutiveLosses: 3,
      dailyLossLimit: 5,
      action: 'pause' // pause, stop, reduce
    },
    positionSizing: 'fixed', // fixed, kelly, volatility
    leverage: 1
  })

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const handleSaveSettings = () => {
    // 설정 저장 로직
    console.log('Settings saved:', {
      universe,
      tradingConditions,
      splitTrading,
      riskManagement
    })
  }

  return (
    <Box>
      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
            <Tab icon={<AccountBalance />} label="투자유니버스" />
            <Tab icon={<TrendingUp />} label="매매조건" />
            <Tab icon={<ShowChart />} label="업종지표" />
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
                    max={5000}
                    marks={[
                      { value: 0, label: '0' },
                      { value: 1000, label: '1000억' },
                      { value: 5000, label: '5000억+' }
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

        {/* 매매조건 탭 */}
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
                    <Divider sx={{ my: 2 }} />
                    <FormControlLabel
                      control={
                        <Switch 
                          checked={tradingConditions.buyConditions.sectorIndex.enabled}
                          onChange={(e) => setTradingConditions({
                            ...tradingConditions,
                            buyConditions: {
                              ...tradingConditions.buyConditions,
                              sectorIndex: { 
                                ...tradingConditions.buyConditions.sectorIndex, 
                                enabled: e.target.checked 
                              }
                            }
                          })}
                        />
                      }
                      label="업종지표 대비 조건"
                    />
                    {tradingConditions.buyConditions.sectorIndex.enabled && (
                      <Stack spacing={2} sx={{ mt: 2, ml: 3 }}>
                        <FormControl size="small">
                          <Select
                            value={tradingConditions.buyConditions.sectorIndex.comparison}
                            onChange={(e) => setTradingConditions({
                              ...tradingConditions,
                              buyConditions: {
                                ...tradingConditions.buyConditions,
                                sectorIndex: { 
                                  ...tradingConditions.buyConditions.sectorIndex, 
                                  comparison: e.target.value as string
                                }
                              }
                            })}
                          >
                            <MenuItem value="outperform">업종지수 상회</MenuItem>
                            <MenuItem value="underperform">업종지수 하회</MenuItem>
                            <MenuItem value="correlation">업종지수 동조</MenuItem>
                          </Select>
                        </FormControl>
                        <TextField
                          size="small"
                          label="임계값"
                          value={tradingConditions.buyConditions.sectorIndex.threshold}
                          InputProps={{
                            endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          }}
                        />
                      </Stack>
                    )}
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
                    <Divider sx={{ my: 2 }} />
                    <FormControlLabel
                      control={
                        <Switch 
                          checked={tradingConditions.sellConditions.sectorIndex.enabled}
                          onChange={(e) => setTradingConditions({
                            ...tradingConditions,
                            sellConditions: {
                              ...tradingConditions.sellConditions,
                              sectorIndex: { 
                                ...tradingConditions.sellConditions.sectorIndex, 
                                enabled: e.target.checked 
                              }
                            }
                          })}
                        />
                      }
                      label="업종지표 기반 매도"
                    />
                    {tradingConditions.sellConditions.sectorIndex.enabled && (
                      <Stack spacing={2} sx={{ mt: 2, ml: 3 }}>
                        <FormControl size="small">
                          <Select
                            value={tradingConditions.sellConditions.sectorIndex.comparison}
                            onChange={(e) => setTradingConditions({
                              ...tradingConditions,
                              sellConditions: {
                                ...tradingConditions.sellConditions,
                                sectorIndex: { 
                                  ...tradingConditions.sellConditions.sectorIndex, 
                                  comparison: e.target.value as string
                                }
                              }
                            })}
                          >
                            <MenuItem value="underperform">업종지수 하회 시</MenuItem>
                            <MenuItem value="divergence">업종과 괴리 시</MenuItem>
                            <MenuItem value="breakdown">업종 하락 전환 시</MenuItem>
                          </Select>
                        </FormControl>
                        <TextField
                          size="small"
                          label="임계값"
                          value={tradingConditions.sellConditions.sectorIndex.threshold}
                          InputProps={{
                            endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          }}
                        />
                      </Stack>
                    )}
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
                    주요 지수
                  </Typography>
                  <Stack spacing={3}>
                    {sectorIndices.mainIndices.map(index => (
                      <Box key={index.code}>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={index.enabled}
                              onChange={(e) => {
                                const updated = sectorIndices.mainIndices.map(i => 
                                  i.code === index.code ? {...i, enabled: e.target.checked} : i
                                )
                                setSectorIndices({...sectorIndices, mainIndices: updated})
                              }}
                            />
                          }
                          label={
                            <Stack direction="row" spacing={2} alignItems="center">
                              <Typography>{index.name}</Typography>
                              <Chip label={index.code} size="small" />
                            </Stack>
                          }
                        />
                        {index.enabled && (
                          <Box sx={{ ml: 4, mt: 1 }}>
                            <FormLabel component="legend">시간대 선택</FormLabel>
                            <RadioGroup
                              row
                              value={index.timeframe}
                              onChange={(e) => {
                                const updated = sectorIndices.mainIndices.map(i => 
                                  i.code === index.code ? {...i, timeframe: e.target.value} : i
                                )
                                setSectorIndices({...sectorIndices, mainIndices: updated})
                              }}
                            >
                              {sectorIndices.indexTimeframes.map(tf => (
                                <FormControlLabel 
                                  key={tf}
                                  value={tf} 
                                  control={<Radio size="small" />} 
                                  label={tf} 
                                />
                              ))}
                            </RadioGroup>
                          </Box>
                        )}
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            
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
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    상관관계 분석 설정
                  </Typography>
                  <Stack spacing={2}>
                    <TextField
                      label="상관관계 분석 기간"
                      value={sectorIndices.correlationPeriod}
                      onChange={(e) => setSectorIndices({
                        ...sectorIndices,
                        correlationPeriod: Number(e.target.value)
                      })}
                      InputProps={{
                        endAdornment: <InputAdornment position="end">일</InputAdornment>,
                      }}
                      fullWidth
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          checked={sectorIndices.useRelativeStrength}
                          onChange={(e) => setSectorIndices({
                            ...sectorIndices,
                            useRelativeStrength: e.target.checked
                          })}
                        />
                      }
                      label="상대강도 지수 (RS) 활용"
                    />
                    {sectorIndices.useRelativeStrength && (
                      <TextField
                        label="상대강도 계산 기간"
                        value={sectorIndices.strengthPeriod}
                        onChange={(e) => setSectorIndices({
                          ...sectorIndices,
                          strengthPeriod: Number(e.target.value)
                        })}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">일</InputAdornment>,
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
                    업종 모멘텀 전략
                  </Typography>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    업종 지수가 상승 모멘텀을 보일 때 해당 업종 종목에 가중치를 부여합니다.
                  </Alert>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    지수 시간대 설정:
                  </Typography>
                  <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                    {sectorIndices.mainIndices.filter(i => i.enabled).map(idx => (
                      <Chip 
                        key={idx.code}
                        label={`${idx.name}: ${idx.timeframe}`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Stack>
                  <Stack spacing={2}>
                    <Typography variant="body2" color="text.secondary">
                      활성화된 업종:
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {sectorIndices.sectorIndices
                        .filter(s => s.enabled)
                        .map(s => (
                          <Chip 
                            key={s.code}
                            label={`${s.name} (×${s.weight})`}
                            color="primary"
                            size="small"
                            icon={s.weight > 1 ? <TrendingUp /> : <TrendingDown />}
                          />
                        ))}
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 분할매매 탭 */}
        <TabPanel value={tabValue} index={3}>
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
                          InputProps={{
                            endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          }}
                          size="small"
                          sx={{ width: 100 }}
                        />
                        <TextField
                          label="트리거"
                          value={level.trigger}
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
                          InputProps={{
                            endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          }}
                          size="small"
                          sx={{ width: 100 }}
                        />
                        <TextField
                          label="트리거"
                          value={level.trigger}
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
        <TabPanel value={tabValue} index={4}>
          <Typography variant="h6" gutterBottom>
            위험관리 시스템
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    포지션 관리
                  </Typography>
                  <Stack spacing={2}>
                    <TextField
                      label="최대 포지션 크기"
                      value={riskManagement.maxPositionSize}
                      onChange={(e) => setRiskManagement({
                        ...riskManagement,
                        maxPositionSize: Number(e.target.value)
                      })}
                      InputProps={{
                        endAdornment: <InputAdornment position="end">%</InputAdornment>,
                      }}
                      fullWidth
                    />
                    <TextField
                      label="최대 일일 손실"
                      value={riskManagement.maxDailyLoss}
                      onChange={(e) => setRiskManagement({
                        ...riskManagement,
                        maxDailyLoss: Number(e.target.value)
                      })}
                      InputProps={{
                        endAdornment: <InputAdornment position="end">%</InputAdornment>,
                      }}
                      fullWidth
                    />
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
                        <FormLabel>CUT 발동 시 액션</FormLabel>
                        <Select
                          value={riskManagement.systemCut.action}
                          onChange={(e) => setRiskManagement({
                            ...riskManagement,
                            systemCut: { 
                              ...riskManagement.systemCut, 
                              action: e.target.value as 'pause' | 'stop' | 'reduce'
                            }
                          })}
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

        {/* 저장 버튼 */}
        <Box sx={{ p: 3, borderTop: 1, borderColor: 'divider' }}>
          <Stack direction="row" spacing={2} justifyContent="flex-end">
            <Button
              variant="outlined"
              startIcon={<RestartAlt />}
              onClick={() => window.location.reload()}
            >
              초기화
            </Button>
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSaveSettings}
            >
              설정 저장
            </Button>
          </Stack>
        </Box>
      </Paper>
    </Box>
  )
}

export default TradingSettings