import React, { useState, useEffect } from 'react'
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
  Tooltip
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
      id={`investment-tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

interface InvestmentConfig {
  universe: {
    marketCap: [number, number]
    per: [number, number]
    pbr: [number, number]
    roe: [number, number]
    debtRatio: [number, number]
    tradingVolume: [number, number] // 거래량 (백만원)
  }
  sectors: {
    include: string[]
    exclude: string[]
    sectorWeights: { [key: string]: number }
  }
  portfolio: {
    maxPositions: number
    minPositions: number
    positionSizeMethod: 'equal' | 'risk_parity' | 'kelly' | 'custom'
    maxPositionSize: number // 최대 종목당 비중 (%)
    minPositionSize: number // 최소 종목당 비중 (%)
    cashBuffer: number // 현금 보유 비율 (%)
    rebalancePeriod: 'daily' | 'weekly' | 'monthly' | 'quarterly'
    rebalanceThreshold: number // 리밸런싱 임계값 (%)
  }
  risk: {
    maxDrawdown: number // 최대 허용 손실 (%)
    stopLoss: number // 개별 종목 손절매 (%)
    takeProfit: number // 개별 종목 익절매 (%)
    trailingStop: boolean
    trailingStopPercent: number
    positionScaling: boolean // 포지션 스케일링 사용
    scaleInThreshold: number // 추가 매수 기준 (%)
    scaleOutThreshold: number // 부분 매도 기준 (%)
    correlationLimit: number // 종목간 상관계수 한계
  }
}

const SECTORS = [
  'IT/소프트웨어', '반도체', '2차전지', '바이오/헬스케어', 
  '자동차', '화학', '철강/소재', '금융', '건설/부동산',
  '유통/소비재', '엔터테인먼트', '조선/기계', '에너지',
  '통신', '운송', '게임', '화장품', '식품/음료'
]

const InvestmentSettings: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0)
  const [config, setConfig] = useState<InvestmentConfig>({
    universe: {
      marketCap: [100, 50000], // 100억 ~ 5조
      per: [5, 25],
      pbr: [0.5, 3],
      roe: [5, 30],
      debtRatio: [0, 100],
      tradingVolume: [100, 10000]
    },
    sectors: {
      include: ['IT/소프트웨어', '반도체', '2차전지', '바이오/헬스케어'],
      exclude: ['건설/부동산', '조선/기계'],
      sectorWeights: {}
    },
    portfolio: {
      maxPositions: 20,
      minPositions: 5,
      positionSizeMethod: 'equal',
      maxPositionSize: 20,
      minPositionSize: 3,
      cashBuffer: 10,
      rebalancePeriod: 'monthly',
      rebalanceThreshold: 5
    },
    risk: {
      maxDrawdown: 20,
      stopLoss: -7,
      takeProfit: 15,
      trailingStop: false,
      trailingStopPercent: 5,
      positionScaling: false,
      scaleInThreshold: -3,
      scaleOutThreshold: 10,
      correlationLimit: 0.7
    }
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = () => {
    const saved = localStorage.getItem('investmentConfig')
    if (saved) {
      setConfig(JSON.parse(saved))
    }
  }

  const saveSettings = () => {
    setSaving(true)
    localStorage.setItem('investmentConfig', JSON.stringify(config))
    setTimeout(() => {
      setSaving(false)
      setMessage('투자 설정이 저장되었습니다')
      setTimeout(() => setMessage(''), 3000)
    }, 500)
  }

  const resetSettings = () => {
    if (confirm('모든 설정을 초기값으로 되돌리시겠습니까?')) {
      localStorage.removeItem('investmentConfig')
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
    <Box>
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingUp sx={{ fontSize: 30 }} />
            투자 설정 상세
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
              onClick={saveSettings}
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
            <Tabs value={currentTab} onChange={handleTabChange}>
              <Tab icon={<FilterList />} iconPosition="start" label="투자 유니버스" />
              <Tab icon={<Business />} iconPosition="start" label="섹터 설정" />
              <Tab icon={<AccountBalance />} iconPosition="start" label="포트폴리오" />
              <Tab icon={<Shield />} iconPosition="start" label="리스크 관리" />
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
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      수익성 및 안정성
                    </Typography>
                    
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
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      포지션 스케일링
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
                    
                    <TextField
                      fullWidth
                      type="number"
                      label="종목간 상관계수 한계"
                      value={config.risk.correlationLimit}
                      onChange={(e) => setConfig({
                        ...config,
                        risk: { ...config.risk, correlationLimit: parseFloat(e.target.value) }
                      })}
                      sx={{ mt: 2 }}
                      helperText="포트폴리오 분산을 위한 상관계수 제한 (0~1)"
                    />
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

export default InvestmentSettings