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
  CardContent
} from '@mui/material'
import {
  Settings,
  AccountBalance,
  Warning,
  Info,
  Save,
  RestartAlt,
  Analytics,
  Security,
  Business,
  FilterList,
  TrendingUp
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

const TradingSettingsSimplified: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const [savedAlert, setSavedAlert] = useState(false)
  
  // 투자유니버스 설정 - 키움 API 지원 재무지표
  const [universe, setUniverse] = useState({
    // 기본 가치평가 지표
    marketCap: [10, 1000], // 억원
    per: [5, 30],          // 주가수익비율
    pbr: [0.5, 5],         // 주가순자산비율
    eps: [0, 10000],       // 주당순이익 (원)
    bps: [0, 100000],      // 주당순자산 (원)
    
    // 수익성 지표
    roe: [5, 50],          // 자기자본이익률 %
    roa: [0, 30],          // 총자산이익률 %
    operatingMargin: [0, 30],  // 영업이익률 %
    netMargin: [0, 20],    // 순이익률 %
    
    // 안정성 지표
    debtRatio: [0, 100],   // 부채비율 %
    currentRatio: [50, 300], // 유동비율 %
    
    // 배당
    dividendYield: [0, 10], // 배당수익률 %
    
    // 섹터 필터 (선택된 섹터만 포함)
    sectors: ['IT', '바이오', '2차전지', '반도체']
  })
  
  // 포트폴리오 관리 설정
  const [portfolio, setPortfolio] = useState({
    totalCapital: 10000000,
    maxPositions: 10,
    positionSize: 'equal', // equal, proportional, fixed
    rebalanceFrequency: 'monthly',
    riskManagement: {
      maxDrawdown: 20,
      maxPositionSize: 10,
      sectorDiversification: true,
      correlationLimit: 0.7
    }
  })
  
  // 업종/지표 설정
  const [sectorSettings, setSectorSettings] = useState({
    trackSectorIndex: true,
    sectorWeighting: {
      IT: 30,
      바이오: 20,
      '2차전지': 25,
      반도체: 25
    },
    sectorRotation: {
      enabled: false,
      frequency: 'quarterly',
      method: 'momentum' // momentum, meanReversion
    }
  })

  // Load saved settings
  useEffect(() => {
    const saved = localStorage.getItem('investmentConfig')
    if (saved) {
      const config = JSON.parse(saved)
      if (config.universe) setUniverse(config.universe)
      if (config.portfolio) setPortfolio(config.portfolio)
      if (config.sectors) setSectorSettings(config.sectors)
    }
  }, [])

  const handleSaveSettings = () => {
    const config = {
      universe,
      portfolio,
      sectors: sectorSettings,
      lastUpdated: new Date().toISOString()
    }
    
    localStorage.setItem('investmentConfig', JSON.stringify(config))
    setSavedAlert(true)
    setTimeout(() => setSavedAlert(false), 3000)
    
    // Trigger storage event for other components
    window.dispatchEvent(new Event('storage'))
  }

  const handleResetSettings = () => {
    setUniverse({
      // 기본 가치평가 지표
      marketCap: [10, 1000],
      per: [5, 30],
      pbr: [0.5, 5],
      eps: [0, 10000],
      bps: [0, 100000],
      
      // 수익성 지표
      roe: [5, 50],
      roa: [0, 30],
      operatingMargin: [0, 30],
      netMargin: [0, 20],
      
      // 안정성 지표
      debtRatio: [0, 100],
      currentRatio: [50, 300],
      
      // 배당
      dividendYield: [0, 10],
      
      // 섹터 필터
      sectors: ['IT', '바이오', '2차전지', '반도체']
    })
    setPortfolio({
      totalCapital: 10000000,
      maxPositions: 10,
      positionSize: 'equal',
      rebalanceFrequency: 'monthly',
      riskManagement: {
        maxDrawdown: 20,
        maxPositionSize: 10,
        sectorDiversification: true,
        correlationLimit: 0.7
      }
    })
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Settings />
            투자 설정
          </Typography>
          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              startIcon={<RestartAlt />}
              onClick={handleResetSettings}
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
        </Stack>
        
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab icon={<FilterList />} label="투자유니버스" />
          <Tab icon={<AccountBalance />} label="포트폴리오 관리" />
          <Tab icon={<Business />} label="업종/지표" />
        </Tabs>
      </Box>

      {savedAlert && (
        <Alert severity="success" sx={{ mb: 2 }}>
          설정이 저장되었습니다.
        </Alert>
      )}

      {/* 투자유니버스 탭 */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="info" icon={<Info />}>
              키움증권 API에서 제공하는 재무지표를 기반으로 투자 유니버스를 설정합니다. 
              총 12개의 재무지표로 종목을 필터링할 수 있습니다.
            </Alert>
          </Grid>

          {/* 가치평가 지표 */}
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" color="primary">
                    <Analytics sx={{ mr: 1, verticalAlign: 'middle' }} />
                    가치평가 지표
                  </Typography>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => {
                      const event = new CustomEvent('applyFilter', { 
                        detail: { 
                          filterType: 'valuation',
                          filters: {
                            marketCap: universe.marketCap,
                            per: universe.per,
                            pbr: universe.pbr,
                            eps: universe.eps,
                            bps: universe.bps
                          }
                        } 
                      })
                      window.dispatchEvent(event)
                    }}
                  >
                    적용
                  </Button>
                </Box>
                
                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>시가총액 (억원)</Typography>
                  <Slider
                    value={universe.marketCap}
                    onChange={(e, v) => setUniverse({...universe, marketCap: v as number[]})}
                    valueLabelDisplay="auto"
                    min={0}
                    max={10000}
                    marks={[
                      { value: 0, label: '0' },
                      { value: 1000, label: '1천억' },
                      { value: 5000, label: '5천억' },
                      { value: 10000, label: '1조' }
                    ]}
                  />
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>PER (배)</Typography>
                  <Slider
                    value={universe.per}
                    onChange={(e, v) => setUniverse({...universe, per: v as number[]})}
                    valueLabelDisplay="auto"
                    min={0}
                    max={100}
                  />
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>PBR (배)</Typography>
                  <Slider
                    value={universe.pbr}
                    onChange={(e, v) => setUniverse({...universe, pbr: v as number[]})}
                    valueLabelDisplay="auto"
                    min={0}
                    max={10}
                    step={0.1}
                  />
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>ROE (%)</Typography>
                  <Slider
                    value={universe.roe}
                    onChange={(e, v) => setUniverse({...universe, roe: v as number[]})}
                    valueLabelDisplay="auto"
                    min={-50}
                    max={100}
                  />
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>EPS (주당순이익, 원)</Typography>
                  <Slider
                    value={universe.eps}
                    onChange={(e, v) => setUniverse({...universe, eps: v as number[]})}
                    valueLabelDisplay="auto"
                    min={0}
                    max={50000}
                    step={100}
                    marks={[
                      { value: 0, label: '0' },
                      { value: 10000, label: '1만' },
                      { value: 30000, label: '3만' },
                      { value: 50000, label: '5만' }
                    ]}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* 수익성 지표 */}
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" color="primary">
                    <TrendingUp sx={{ mr: 1, verticalAlign: 'middle' }} />
                    수익성 및 안정성 지표
                  </Typography>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => {
                      const event = new CustomEvent('applyFilter', { 
                        detail: { 
                          filterType: 'financial',
                          filters: {
                            roe: universe.roe,
                            roa: universe.roa,
                            operatingMargin: universe.operatingMargin,
                            netMargin: universe.netMargin,
                            debtRatio: universe.debtRatio,
                            currentRatio: universe.currentRatio,
                            dividendYield: universe.dividendYield
                          }
                        } 
                      })
                      window.dispatchEvent(event)
                    }}
                  >
                    적용
                  </Button>
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>ROA (총자산이익률, %)</Typography>
                  <Slider
                    value={universe.roa}
                    onChange={(e, v) => setUniverse({...universe, roa: v as number[]})}
                    valueLabelDisplay="auto"
                    min={-20}
                    max={50}
                  />
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>영업이익률 (%)</Typography>
                  <Slider
                    value={universe.operatingMargin}
                    onChange={(e, v) => setUniverse({...universe, operatingMargin: v as number[]})}
                    valueLabelDisplay="auto"
                    min={-50}
                    max={50}
                  />
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>순이익률 (%)</Typography>
                  <Slider
                    value={universe.netMargin}
                    onChange={(e, v) => setUniverse({...universe, netMargin: v as number[]})}
                    valueLabelDisplay="auto"
                    min={-30}
                    max={30}
                  />
                </Box>

                <Divider sx={{ my: 3 }} />
                
                <Typography variant="subtitle1" gutterBottom>
                  안정성 지표
                </Typography>

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>부채비율 (%)</Typography>
                  <Slider
                    value={universe.debtRatio}
                    onChange={(e, v) => setUniverse({...universe, debtRatio: v as number[]})}
                    valueLabelDisplay="auto"
                    min={0}
                    max={500}
                    marks={[
                      { value: 0, label: '0%' },
                      { value: 100, label: '100%' },
                      { value: 200, label: '200%' },
                      { value: 500, label: '500%' }
                    ]}
                  />
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>유동비율 (%)</Typography>
                  <Slider
                    value={universe.currentRatio}
                    onChange={(e, v) => setUniverse({...universe, currentRatio: v as number[]})}
                    valueLabelDisplay="auto"
                    min={0}
                    max={500}
                    marks={[
                      { value: 50, label: '50%' },
                      { value: 100, label: '100%' },
                      { value: 200, label: '200%' },
                      { value: 300, label: '300%' }
                    ]}
                  />
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>배당수익률 (%)</Typography>
                  <Slider
                    value={universe.dividendYield}
                    onChange={(e, v) => setUniverse({...universe, dividendYield: v as number[]})}
                    valueLabelDisplay="auto"
                    min={0}
                    max={10}
                    step={0.1}
                    marks={[
                      { value: 0, label: '0%' },
                      { value: 2, label: '2%' },
                      { value: 5, label: '5%' },
                      { value: 10, label: '10%' }
                    ]}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* 섹터 필터 */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" color="primary">
                    <Business sx={{ mr: 1, verticalAlign: 'middle' }} />
                    섹터 필터
                  </Typography>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => {
                      const event = new CustomEvent('applyFilter', { 
                        detail: { 
                          filterType: 'sector',
                          filters: {
                            sectors: universe.sectors
                          }
                        } 
                      })
                      window.dispatchEvent(event)
                    }}
                  >
                    적용
                  </Button>
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  투자하고 싶은 섹터를 선택하세요. 선택된 섹터의 종목만 투자 대상에 포함됩니다.
                </Typography>
                
                <FormControl component="fieldset" sx={{ width: '100%' }}>
                  <FormGroup row sx={{ gap: 1 }}>
                    {[
                      'IT', '바이오', '2차전지', '반도체', '화학', '자동차', '금융', '유통',
                      '전기전자', '의료정비', '기계', '철강', '건설', '조선', '항공', '통신',
                      '은행', '증권', '보험', '의약품', '화장품', '음식료', '섬유의복', '종이목재'
                    ].map((sector) => (
                      <FormControlLabel
                        key={sector}
                        control={
                          <Checkbox
                            checked={universe.sectors.includes(sector)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setUniverse({
                                  ...universe,
                                  sectors: [...universe.sectors, sector]
                                })
                              } else {
                                setUniverse({
                                  ...universe,
                                  sectors: universe.sectors.filter(s => s !== sector)
                                })
                              }
                            }}
                            sx={{
                              color: universe.sectors.includes(sector) ? 'primary.main' : 'text.secondary'
                            }}
                          />
                        }
                        label={
                          <Chip
                            label={sector}
                            size="small"
                            variant={universe.sectors.includes(sector) ? "filled" : "outlined"}
                            color={universe.sectors.includes(sector) ? "primary" : "default"}
                            sx={{ cursor: 'pointer' }}
                          />
                        }
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                  </FormGroup>
                </FormControl>
                
                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    {universe.sectors.length}개 섹터 선택됨
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Button
                      size="small"
                      onClick={() => setUniverse({
                        ...universe,
                        sectors: [
                          'IT', '바이오', '2차전지', '반도체', '화학', '자동차', '금융', '유통',
                          '전기전자', '의료정비', '기계', '철강', '건설', '조선', '항공', '통신',
                          '은행', '증권', '보험', '의약품', '화장품', '음식료', '섬유의복', '종이목재'
                        ]
                      })}
                    >
                      전체 선택
                    </Button>
                    <Button
                      size="small"
                      onClick={() => setUniverse({...universe, sectors: []})}
                    >
                      전체 해제
                    </Button>
                  </Stack>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* 포트폴리오 관리 탭 */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="info" icon={<Info />}>
              포트폴리오 관리 설정은 자금 배분과 리스크 관리 규칙을 정의합니다.
            </Alert>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <AccountBalance sx={{ mr: 1, verticalAlign: 'middle' }} />
                  자금 관리
                </Typography>

                <TextField
                  fullWidth
                  label="총 투자금"
                  value={portfolio.totalCapital}
                  onChange={(e) => setPortfolio({
                    ...portfolio,
                    totalCapital: parseInt(e.target.value) || 0
                  })}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">원</InputAdornment>
                  }}
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="최대 보유 종목 수"
                  value={portfolio.maxPositions}
                  onChange={(e) => setPortfolio({
                    ...portfolio,
                    maxPositions: parseInt(e.target.value) || 0
                  })}
                  type="number"
                  sx={{ mt: 2 }}
                />

                <FormControl fullWidth sx={{ mt: 2 }}>
                  <FormLabel>포지션 크기 결정 방식</FormLabel>
                  <RadioGroup
                    value={portfolio.positionSize}
                    onChange={(e) => setPortfolio({
                      ...portfolio,
                      positionSize: e.target.value
                    })}
                  >
                    <FormControlLabel value="equal" control={<Radio />} label="균등 배분" />
                    <FormControlLabel value="proportional" control={<Radio />} label="시가총액 비례" />
                    <FormControlLabel value="fixed" control={<Radio />} label="고정 금액" />
                  </RadioGroup>
                </FormControl>

                <FormControl fullWidth sx={{ mt: 2 }}>
                  <FormLabel>리밸런싱 주기</FormLabel>
                  <Select
                    value={portfolio.rebalanceFrequency}
                    onChange={(e) => setPortfolio({
                      ...portfolio,
                      rebalanceFrequency: e.target.value
                    })}
                  >
                    <MenuItem value="daily">매일</MenuItem>
                    <MenuItem value="weekly">매주</MenuItem>
                    <MenuItem value="monthly">매월</MenuItem>
                    <MenuItem value="quarterly">분기</MenuItem>
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Security sx={{ mr: 1, verticalAlign: 'middle' }} />
                  리스크 관리
                </Typography>

                <Box sx={{ mt: 2 }}>
                  <Typography gutterBottom>최대 손실 한도 (MDD)</Typography>
                  <Slider
                    value={portfolio.riskManagement.maxDrawdown}
                    onChange={(e, v) => setPortfolio({
                      ...portfolio,
                      riskManagement: {
                        ...portfolio.riskManagement,
                        maxDrawdown: v as number
                      }
                    })}
                    valueLabelDisplay="auto"
                    valueLabelFormat={(v) => `${v}%`}
                    min={5}
                    max={50}
                  />
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>최대 포지션 크기 (%)</Typography>
                  <Slider
                    value={portfolio.riskManagement.maxPositionSize}
                    onChange={(e, v) => setPortfolio({
                      ...portfolio,
                      riskManagement: {
                        ...portfolio.riskManagement,
                        maxPositionSize: v as number
                      }
                    })}
                    valueLabelDisplay="auto"
                    valueLabelFormat={(v) => `${v}%`}
                    min={1}
                    max={30}
                  />
                </Box>

                <FormControlLabel
                  control={
                    <Switch
                      checked={portfolio.riskManagement.sectorDiversification}
                      onChange={(e) => setPortfolio({
                        ...portfolio,
                        riskManagement: {
                          ...portfolio.riskManagement,
                          sectorDiversification: e.target.checked
                        }
                      })}
                    />
                  }
                  label="섹터 분산 투자 적용"
                  sx={{ mt: 2 }}
                />

                <Box sx={{ mt: 3 }}>
                  <Typography gutterBottom>상관관계 한도</Typography>
                  <Slider
                    value={portfolio.riskManagement.correlationLimit}
                    onChange={(e, v) => setPortfolio({
                      ...portfolio,
                      riskManagement: {
                        ...portfolio.riskManagement,
                        correlationLimit: v as number
                      }
                    })}
                    valueLabelDisplay="auto"
                    min={0}
                    max={1}
                    step={0.05}
                    disabled={!portfolio.riskManagement.sectorDiversification}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* 업종/지표 탭 */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="info" icon={<Info />}>
              업종별 가중치와 로테이션 전략을 설정합니다.
            </Alert>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Business sx={{ mr: 1, verticalAlign: 'middle' }} />
                  업종별 가중치 설정
                </Typography>

                <FormControlLabel
                  control={
                    <Switch
                      checked={sectorSettings.trackSectorIndex}
                      onChange={(e) => setSectorSettings({
                        ...sectorSettings,
                        trackSectorIndex: e.target.checked
                      })}
                    />
                  }
                  label="업종 지수 추적"
                  sx={{ mb: 2 }}
                />

                {Object.entries(sectorSettings.sectorWeighting).map(([sector, weight]) => (
                  <Box key={sector} sx={{ mt: 2 }}>
                    <Typography gutterBottom>{sector} 가중치 (%)</Typography>
                    <Slider
                      value={weight}
                      onChange={(e, v) => setSectorSettings({
                        ...sectorSettings,
                        sectorWeighting: {
                          ...sectorSettings.sectorWeighting,
                          [sector]: v as number
                        }
                      })}
                      valueLabelDisplay="auto"
                      valueLabelFormat={(v) => `${v}%`}
                      min={0}
                      max={100}
                    />
                  </Box>
                ))}

                <Divider sx={{ my: 3 }} />

                <Typography variant="h6" gutterBottom>
                  섹터 로테이션
                </Typography>

                <FormControlLabel
                  control={
                    <Switch
                      checked={sectorSettings.sectorRotation.enabled}
                      onChange={(e) => setSectorSettings({
                        ...sectorSettings,
                        sectorRotation: {
                          ...sectorSettings.sectorRotation,
                          enabled: e.target.checked
                        }
                      })}
                    />
                  }
                  label="섹터 로테이션 활성화"
                  sx={{ mb: 2 }}
                />

                <FormControl fullWidth sx={{ mt: 2 }} disabled={!sectorSettings.sectorRotation.enabled}>
                  <FormLabel>로테이션 주기</FormLabel>
                  <Select
                    value={sectorSettings.sectorRotation.frequency}
                    onChange={(e) => setSectorSettings({
                      ...sectorSettings,
                      sectorRotation: {
                        ...sectorSettings.sectorRotation,
                        frequency: e.target.value
                      }
                    })}
                  >
                    <MenuItem value="monthly">매월</MenuItem>
                    <MenuItem value="quarterly">분기</MenuItem>
                    <MenuItem value="semiannually">반기</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth sx={{ mt: 2 }} disabled={!sectorSettings.sectorRotation.enabled}>
                  <FormLabel>로테이션 방식</FormLabel>
                  <RadioGroup
                    value={sectorSettings.sectorRotation.method}
                    onChange={(e) => setSectorSettings({
                      ...sectorSettings,
                      sectorRotation: {
                        ...sectorSettings.sectorRotation,
                        method: e.target.value
                      }
                    })}
                  >
                    <FormControlLabel value="momentum" control={<Radio />} label="모멘텀 기반" />
                    <FormControlLabel value="meanReversion" control={<Radio />} label="평균 회귀" />
                  </RadioGroup>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Paper>
  )
}

export default TradingSettingsSimplified