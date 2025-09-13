import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Stack,
  Chip,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
  IconButton,
  Tooltip,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  Switch,
  FormControlLabel,
  LinearProgress,
  Tab,
  Tabs
} from '@mui/material'
import {
  ExpandMore,
  Info,
  CheckCircle,
  Warning,
  TrendingUp,
  TrendingDown,
  Assessment,
  Code,
  Psychology,
  Timeline,
  BubbleChart,
  ShowChart,
  Functions,
  CompareArrows,
  FilterAlt,
  Lightbulb,
  ErrorOutline,
  PlayCircle,
  StopCircle,
  ArrowUpward,
  ArrowDownward,
  SwapVert,
  Analytics,
  Speed,
  WbSunny,
  Cloud
} from '@mui/icons-material'

interface StrategyAnalyzerProps {
  strategy: any
  investmentConfig?: any
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
      id={`strategy-tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const StrategyAnalyzer: React.FC<StrategyAnalyzerProps> = ({ strategy: initialStrategy, investmentConfig }) => {
  const [selectedStrategy, setSelectedStrategy] = useState<any>(initialStrategy)
  const [savedStrategies, setSavedStrategies] = useState<any[]>([])
  const [tabValue, setTabValue] = useState(0)
  const [simulationMode, setSimulationMode] = useState(false)
  const [samplePrice, setSamplePrice] = useState(50000)
  const [sampleVolume, setSampleVolume] = useState(1000000)

  // 지표 시뮬레이션 값들
  const [indicatorValues, setIndicatorValues] = useState<any>({
    RSI_14: 50,
    SMA_5: 49000,
    SMA_20: 51000,
    MACD: 100,
    MACD_signal: 80,
    BB_upper: 52000,
    BB_lower: 48000,
    volume: 1000000,
    close: 50000
  })

  // Supabase에서 저장된 전략 불러오기
  useEffect(() => {
    loadSavedStrategies()
  }, [])

  const loadSavedStrategies = async () => {
    try {
      const { supabase } = await import('../lib/supabase')
      const { data, error } = await supabase
        .from('strategies')
        .select('*')
        .order('created_at', { ascending: false })

      if (!error && data) {
        setSavedStrategies(data)
      }
    } catch (err) {
      console.error('전략 로드 실패:', err)
    }
  }

  // 조건 평가 함수
  const evaluateCondition = (condition: any, values: any) => {
    const indicatorValue = values[condition.indicator] || 0
    let compareValue = condition.value

    // value가 다른 지표를 참조하는 경우
    if (typeof condition.value === 'string' && values[condition.value] !== undefined) {
      compareValue = values[condition.value]
    }

    switch (condition.operator) {
      case '>':
        return indicatorValue > compareValue
      case '<':
        return indicatorValue < compareValue
      case '=':
      case '==':
        return indicatorValue === compareValue
      case '>=':
        return indicatorValue >= compareValue
      case '<=':
        return indicatorValue <= compareValue
      case 'cross_above':
        // 교차는 시뮬레이션에서 간단히 표현
        return indicatorValue > compareValue && Math.random() > 0.7
      case 'cross_below':
        return indicatorValue < compareValue && Math.random() > 0.7
      default:
        return false
    }
  }

  // 전체 전략 평가
  const evaluateStrategy = () => {
    if (!selectedStrategy) return { buy: false, sell: false, buyReasons: [], sellReasons: [] }

    const buyReasons: string[] = []
    const sellReasons: string[] = []
    let shouldBuy = false
    let shouldSell = false

    // 매수 조건 평가
    if (selectedStrategy.buyConditions?.length > 0) {
      let buyResult = false
      let previousResult = false

      selectedStrategy.buyConditions.forEach((condition: any, index: number) => {
        const result = evaluateCondition(condition, indicatorValues)

        if (result) {
          buyReasons.push(`${condition.indicator} ${condition.operator} ${condition.value}`)
        }

        if (index === 0) {
          buyResult = result
          previousResult = result
        } else {
          if (condition.combineWith === 'AND') {
            buyResult = previousResult && result
          } else if (condition.combineWith === 'OR') {
            buyResult = previousResult || result
          }
          previousResult = buyResult
        }
      })

      shouldBuy = buyResult
    }

    // 매도 조건 평가
    if (selectedStrategy.sellConditions?.length > 0) {
      let sellResult = false
      let previousResult = false

      selectedStrategy.sellConditions.forEach((condition: any, index: number) => {
        const result = evaluateCondition(condition, indicatorValues)

        if (result) {
          sellReasons.push(`${condition.indicator} ${condition.operator} ${condition.value}`)
        }

        if (index === 0) {
          sellResult = result
          previousResult = result
        } else {
          if (condition.combineWith === 'AND') {
            sellResult = previousResult && result
          } else if (condition.combineWith === 'OR') {
            sellResult = previousResult || result
          }
          previousResult = sellResult
        }
      })

      shouldSell = sellResult
    }

    return { buy: shouldBuy, sell: shouldSell, buyReasons, sellReasons }
  }

  const evaluation = evaluateStrategy()

  return (
    <Box>
      {/* 전략 선택 */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <FormControl fullWidth size="small">
              <InputLabel>분석할 전략 선택</InputLabel>
              <Select
                value={selectedStrategy?.id || 'current'}
                onChange={(e) => {
                  const value = e.target.value
                  if (value === 'current' || (initialStrategy && value === initialStrategy.id)) {
                    console.log('Selected initial strategy:', initialStrategy)
                    setSelectedStrategy(initialStrategy)
                  } else {
                    const strategy = savedStrategies.find(s => s.id === value)
                    console.log('Selected saved strategy:', strategy)
                    // config 객체에서 실제 전략 데이터 추출 (parameters 대신 config 사용)
                    if (strategy?.config) {
                      const extractedStrategy = {
                        ...strategy,
                        buyConditions: strategy.config.buyConditions || strategy.entry_conditions?.buy || [],
                        sellConditions: strategy.config.sellConditions || strategy.exit_conditions?.sell || [],
                        indicators: strategy.config.indicators || strategy.indicators?.list || [],
                        riskManagement: strategy.risk_management || {
                          stopLoss: strategy.config.stopLoss,
                          takeProfit: strategy.config.takeProfit,
                          trailingStop: strategy.config.trailingStop,
                          trailingStopPercent: strategy.config.trailingStopPercent,
                          positionSize: strategy.config.positionSize,
                          maxPositions: strategy.config.maxPositions
                        }
                      }
                      console.log('Extracted strategy data:', extractedStrategy)
                      setSelectedStrategy(extractedStrategy)
                    } else if (strategy?.parameters) {
                      // 구버전 호환성 유지
                      const extractedStrategy = {
                        ...strategy,
                        buyConditions: strategy.parameters.buyConditions || [],
                        sellConditions: strategy.parameters.sellConditions || [],
                        indicators: strategy.parameters.indicators || [],
                        riskManagement: {
                          stopLoss: strategy.parameters.stopLoss,
                          takeProfit: strategy.parameters.takeProfit,
                          trailingStop: strategy.parameters.trailingStop,
                          trailingStopPercent: strategy.parameters.trailingStopPercent
                        }
                      }
                      console.log('Extracted strategy data (legacy):', extractedStrategy)
                      setSelectedStrategy(extractedStrategy)
                    } else {
                      setSelectedStrategy(strategy)
                    }
                  }
                  setTabValue(0) // 전략 로직 해석 탭으로 이동
                }}
                label="분석할 전략 선택"
              >
                {initialStrategy && (
                  <MenuItem value={initialStrategy.id || 'current'}>
                    현재 편집 중인 전략
                  </MenuItem>
                )}
                {savedStrategies.map((strat) => (
                  <MenuItem key={strat.id} value={strat.id}>
                    {strat.name} {strat.is_public ? '(공개)' : '(비공개)'}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={simulationMode}
                  onChange={(e) => setSimulationMode(e.target.checked)}
                  color="primary"
                />
              }
              label="실시간 시뮬레이션 모드"
            />
          </Grid>
        </Grid>
      </Paper>

      {selectedStrategy && (
        <>
          {/* 전략 개요 */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                <Psychology sx={{ mr: 1, verticalAlign: 'bottom' }} />
                전략 구조 분석: {selectedStrategy.name || '이름 없음'}
              </Typography>

              {selectedStrategy.description && (
                <Alert severity="info" sx={{ mt: 2, mb: 2 }}>
                  {selectedStrategy.description}
                </Alert>
              )}

              <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ mb: 2 }}>
                <Tab label="전략 로직 해석" />
                <Tab label="지표 설명" />
                <Tab label="시뮬레이션" />
                <Tab label="최적화 제안" />
              </Tabs>

              <TabPanel value={tabValue} index={0}>
                {/* 전략 로직 해석 */}
                <Grid container spacing={3}>
                  {/* 매수 로직 */}
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, bgcolor: 'success.light', color: 'success.contrastText' }}>
                      <Typography variant="h6" gutterBottom>
                        <TrendingUp sx={{ mr: 1 }} />
                        매수 신호 발생 조건
                      </Typography>
                      <Divider sx={{ my: 1, bgcolor: 'success.dark' }} />

                      {Array.isArray(selectedStrategy?.buyConditions) && selectedStrategy.buyConditions.length > 0 ? (
                        <Box>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            다음 조건들이 충족될 때 매수 신호가 발생합니다:
                          </Typography>
                          {selectedStrategy.buyConditions.map((condition: any, index: number) => (
                            <Box key={index} sx={{ mb: 1 }}>
                              <Chip
                                label={`조건 ${index + 1}`}
                                size="small"
                                sx={{ mr: 1, bgcolor: 'success.dark' }}
                              />
                              <Typography variant="body2" component="span">
                                {condition.indicator} {condition.operator} {condition.value}
                              </Typography>
                              {index < selectedStrategy.buyConditions.length - 1 && (
                                <Chip
                                  label={condition.combineWith || 'AND'}
                                  size="small"
                                  sx={{ ml: 1, bgcolor: 'warning.dark' }}
                                />
                              )}
                            </Box>
                          ))}

                          <Alert severity="success" sx={{ mt: 2 }}>
                            <Typography variant="caption">
                              <strong>해석:</strong>
                              {selectedStrategy.buyConditions.length === 1
                                ? ' 단일 조건으로 매수 결정'
                                : ' 복합 조건으로 신중한 매수 결정'}
                            </Typography>
                          </Alert>
                        </Box>
                      ) : (
                        <Box>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            매수 조건이 설정되지 않았습니다.
                          </Typography>
                          <Alert severity="info">
                            <Typography variant="caption">
                              전략 빌더에서 매수 조건을 추가해주세요.
                            </Typography>
                          </Alert>
                        </Box>
                      )}
                    </Paper>
                  </Grid>

                  {/* 매도 로직 */}
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, bgcolor: 'error.light', color: 'error.contrastText' }}>
                      <Typography variant="h6" gutterBottom>
                        <TrendingDown sx={{ mr: 1 }} />
                        매도 신호 발생 조건
                      </Typography>
                      <Divider sx={{ my: 1, bgcolor: 'error.dark' }} />

                      {Array.isArray(selectedStrategy?.sellConditions) && selectedStrategy.sellConditions.length > 0 ? (
                        <Box>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            다음 조건들이 충족될 때 매도 신호가 발생합니다:
                          </Typography>
                          {selectedStrategy.sellConditions.map((condition: any, index: number) => (
                            <Box key={index} sx={{ mb: 1 }}>
                              <Chip
                                label={`조건 ${index + 1}`}
                                size="small"
                                sx={{ mr: 1, bgcolor: 'error.dark' }}
                              />
                              <Typography variant="body2" component="span">
                                {condition.indicator} {condition.operator} {condition.value}
                              </Typography>
                              {index < selectedStrategy.sellConditions.length - 1 && (
                                <Chip
                                  label={condition.combineWith || 'AND'}
                                  size="small"
                                  sx={{ ml: 1, bgcolor: 'warning.dark' }}
                                />
                              )}
                            </Box>
                          ))}

                          <Alert severity="error" sx={{ mt: 2 }}>
                            <Typography variant="caption">
                              <strong>해석:</strong>
                              {selectedStrategy.sellConditions.length === 1
                                ? ' 단일 조건으로 매도 결정'
                                : ' 복합 조건으로 신중한 매도 결정'}
                            </Typography>
                          </Alert>
                        </Box>
                      ) : (
                        <Box>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            매도 조건이 설정되지 않았습니다.
                          </Typography>
                          <Alert severity="info">
                            <Typography variant="caption">
                              전략 빌더에서 매도 조건을 추가해주세요.
                            </Typography>
                          </Alert>
                        </Box>
                      )}
                    </Paper>
                  </Grid>
                </Grid>

                {/* 전략 특성 분석 */}
                <Paper sx={{ p: 2, mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    <Analytics sx={{ mr: 1 }} />
                    전략 특성 분석
                  </Typography>
                  <Grid container spacing={2} sx={{ mt: 1 }}>
                    <Grid item xs={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography variant="caption" color="text.secondary">
                            전략 유형
                          </Typography>
                          <Typography variant="h6">
                            {determineStrategyType(selectedStrategy)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography variant="caption" color="text.secondary">
                            복잡도
                          </Typography>
                          <Typography variant="h6">
                            {calculateComplexity(selectedStrategy)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography variant="caption" color="text.secondary">
                            리스크 수준
                          </Typography>
                          <Typography variant="h6">
                            {assessRiskLevel(selectedStrategy)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography variant="caption" color="text.secondary">
                            시장 적합성
                          </Typography>
                          <Typography variant="h6">
                            {determineMarketFit(selectedStrategy)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Paper>
              </TabPanel>

              <TabPanel value={tabValue} index={1}>
                {/* 지표 설명 */}
                <Typography variant="h6" gutterBottom>
                  <Functions sx={{ mr: 1 }} />
                  사용된 지표 상세 설명
                </Typography>

                {/* 조건에서 사용된 지표 추출 */}
                {(() => {
                  const indicatorsFromConditions = new Set<string>()

                  // 매수 조건에서 지표 추출
                  if (Array.isArray(selectedStrategy?.buyConditions)) {
                    selectedStrategy.buyConditions.forEach((cond: any) => {
                      if (cond.indicator) indicatorsFromConditions.add(cond.indicator)
                    })
                  }

                  // 매도 조건에서 지표 추출
                  if (Array.isArray(selectedStrategy?.sellConditions)) {
                    selectedStrategy.sellConditions.forEach((cond: any) => {
                      if (cond.indicator) indicatorsFromConditions.add(cond.indicator)
                    })
                  }

                  // indicators 배열에서 지표 추가
                  if (Array.isArray(selectedStrategy?.indicators)) {
                    selectedStrategy.indicators.forEach((ind: any) => {
                      if (ind.type) indicatorsFromConditions.add(ind.type)
                      if (ind.id) indicatorsFromConditions.add(ind.id)
                      if (ind.name) indicatorsFromConditions.add(ind.name)
                    })
                  }

                  const uniqueIndicators = Array.from(indicatorsFromConditions)

                  if (uniqueIndicators.length === 0) {
                    return (
                      <Alert severity="info">
                        <Typography variant="body2">
                          이 전략에서 사용된 지표가 없거나 아직 설정되지 않았습니다.
                        </Typography>
                      </Alert>
                    )
                  }

                  return (
                    <Grid container spacing={3}>
                      {uniqueIndicators.map((indicatorName: string, index: number) => {
                        // 지표 정보 찾기
                        const indicatorInfo = selectedStrategy?.indicators?.find((ind: any) =>
                          ind.type === indicatorName || ind.id === indicatorName || ind.name === indicatorName
                        )

                        const { koreanName, description, formula, interpretation, visualExample, tips } = getDetailedIndicatorInfo(indicatorName)

                        return (
                          <Grid item xs={12} key={index}>
                            <Paper sx={{ p: 3, bgcolor: 'background.default' }}>
                              {/* 지표 헤더 */}
                              <Box sx={{ mb: 2 }}>
                                <Stack direction="row" alignItems="center" spacing={2} mb={1}>
                                  <ShowChart color="primary" />
                                  <Typography variant="h6" fontWeight="bold">
                                    {koreanName || getIndicatorKoreanName(indicatorName)}
                                  </Typography>
                                  <Chip
                                    label={indicatorName}
                                    size="small"
                                    variant="outlined"
                                  />
                                  {indicatorInfo?.params && (
                                    <Chip
                                      label={Object.entries(indicatorInfo.params).map(([k, v]) => `${k}: ${v}`).join(', ')}
                                      size="small"
                                      color="primary"
                                    />
                                  )}
                                </Stack>
                                <Divider />
                              </Box>

                              <Grid container spacing={2}>
                                {/* 기본 설명 */}
                                <Grid item xs={12} md={6}>
                                  <Box sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2" color="primary" gutterBottom>
                                      📖 기본 설명
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" paragraph>
                                      {description}
                                    </Typography>
                                  </Box>

                                  {/* 계산식 */}
                                  {formula && (
                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="subtitle2" color="primary" gutterBottom>
                                        🧮 계산 방법
                                      </Typography>
                                      <Paper sx={{ p: 1.5, bgcolor: 'grey.900', color: 'grey.100' }}>
                                        <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                                          {formula}
                                        </Typography>
                                      </Paper>
                                    </Box>
                                  )}
                                </Grid>

                                {/* 해석 방법 */}
                                <Grid item xs={12} md={6}>
                                  <Box sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2" color="primary" gutterBottom>
                                      📊 해석 방법
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" paragraph>
                                      {interpretation}
                                    </Typography>
                                  </Box>

                                  {/* 시각적 예시 */}
                                  {visualExample && (
                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="subtitle2" color="primary" gutterBottom>
                                        📈 시각적 표현
                                      </Typography>
                                      <Paper sx={{ p: 1.5, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider' }}>
                                        <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', fontSize: '0.75rem', lineHeight: 1.2 }}>
                                          {visualExample}
                                        </Typography>
                                      </Paper>
                                    </Box>
                                  )}
                                </Grid>

                                {/* 매매 신호 */}
                                <Grid item xs={12}>
                                  <Alert severity="success" icon={<TrendingUp />}>
                                    <Typography variant="subtitle2" gutterBottom>
                                      <strong>매매 신호</strong>
                                    </Typography>
                                    <Typography variant="body2">
                                      {getIndicatorSignal(indicatorName)}
                                    </Typography>
                                  </Alert>
                                </Grid>

                                {/* 활용 팁 */}
                                {tips && (
                                  <Grid item xs={12}>
                                    <Alert severity="info" icon={<Lightbulb />}>
                                      <Typography variant="subtitle2" gutterBottom>
                                        <strong>활용 팁</strong>
                                      </Typography>
                                      <Typography variant="body2">
                                        {tips}
                                      </Typography>
                                    </Alert>
                                  </Grid>
                                )}
                              </Grid>
                            </Paper>
                          </Grid>
                        )
                      })}
                    </Grid>
                  )
                })()}
              </TabPanel>

              <TabPanel value={tabValue} index={2}>
                {/* 시뮬레이션 */}
                <Typography variant="h6" gutterBottom>
                  <PlayCircle sx={{ mr: 1 }} />
                  실시간 조건 시뮬레이션
                </Typography>

                <Alert severity="info" sx={{ mb: 2 }}>
                  지표 값을 조절하여 매수/매도 신호가 언제 발생하는지 실시간으로 확인하세요.
                </Alert>

                <Grid container spacing={2}>
                  {/* 지표 값 조절 */}
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        지표 값 조절
                      </Typography>

                      {Object.keys(indicatorValues).map((key) => (
                        <Box key={key} sx={{ mb: 2 }}>
                          <Typography variant="caption">{key}: {indicatorValues[key]}</Typography>
                          <TextField
                            fullWidth
                            type="number"
                            size="small"
                            value={indicatorValues[key]}
                            onChange={(e) => setIndicatorValues({
                              ...indicatorValues,
                              [key]: parseFloat(e.target.value) || 0
                            })}
                          />
                        </Box>
                      ))}
                    </Paper>
                  </Grid>

                  {/* 시뮬레이션 결과 */}
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        신호 발생 여부
                      </Typography>

                      <Box sx={{ mt: 2 }}>
                        {evaluation.buy && (
                          <Alert severity="success" sx={{ mb: 2 }}>
                            <Typography variant="subtitle2">
                              <TrendingUp sx={{ mr: 1 }} />
                              매수 신호 발생!
                            </Typography>
                            <Typography variant="caption">
                              충족된 조건: {evaluation.buyReasons.join(', ')}
                            </Typography>
                          </Alert>
                        )}

                        {evaluation.sell && (
                          <Alert severity="error" sx={{ mb: 2 }}>
                            <Typography variant="subtitle2">
                              <TrendingDown sx={{ mr: 1 }} />
                              매도 신호 발생!
                            </Typography>
                            <Typography variant="caption">
                              충족된 조건: {evaluation.sellReasons.join(', ')}
                            </Typography>
                          </Alert>
                        )}

                        {!evaluation.buy && !evaluation.sell && (
                          <Alert severity="warning">
                            <Typography variant="subtitle2">
                              <SwapVert sx={{ mr: 1 }} />
                              대기 상태
                            </Typography>
                            <Typography variant="caption">
                              현재 조건으로는 매수/매도 신호가 발생하지 않습니다.
                            </Typography>
                          </Alert>
                        )}
                      </Box>

                      {/* 개별 조건 상태 */}
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          개별 조건 충족 상태
                        </Typography>

                        <Typography variant="caption" color="success.main">매수 조건:</Typography>
                        {Array.isArray(selectedStrategy?.buyConditions) && selectedStrategy.buyConditions.map((condition: any, index: number) => (
                          <Box key={index} sx={{ ml: 2, mb: 1 }}>
                            <Chip
                              size="small"
                              label={`${condition.indicator} ${condition.operator} ${condition.value}`}
                              color={evaluateCondition(condition, indicatorValues) ? "success" : "default"}
                              icon={evaluateCondition(condition, indicatorValues) ? <CheckCircle /> : <ErrorOutline />}
                            />
                          </Box>
                        ))}

                        <Typography variant="caption" color="error.main" sx={{ mt: 2, display: 'block' }}>매도 조건:</Typography>
                        {Array.isArray(selectedStrategy?.sellConditions) && selectedStrategy.sellConditions.map((condition: any, index: number) => (
                          <Box key={index} sx={{ ml: 2, mb: 1 }}>
                            <Chip
                              size="small"
                              label={`${condition.indicator} ${condition.operator} ${condition.value}`}
                              color={evaluateCondition(condition, indicatorValues) ? "error" : "default"}
                              icon={evaluateCondition(condition, indicatorValues) ? <CheckCircle /> : <ErrorOutline />}
                            />
                          </Box>
                        ))}
                      </Box>
                    </Paper>
                  </Grid>
                </Grid>
              </TabPanel>

              <TabPanel value={tabValue} index={3}>
                {/* 최적화 제안 */}
                <Typography variant="h6" gutterBottom>
                  <Lightbulb sx={{ mr: 1 }} />
                  전략 최적화 제안
                </Typography>

                {generateOptimizationSuggestions(selectedStrategy).map((suggestion, index) => (
                  <Alert
                    key={index}
                    severity={suggestion.severity as any}
                    sx={{ mb: 2 }}
                    icon={suggestion.icon}
                  >
                    <Typography variant="subtitle2">{suggestion.title}</Typography>
                    <Typography variant="caption">{suggestion.description}</Typography>
                  </Alert>
                ))}
              </TabPanel>
            </CardContent>
          </Card>
        </>
      )}

      {!selectedStrategy && (
        <Alert severity="info">
          분석할 전략을 선택해주세요.
        </Alert>
      )}
    </Box>
  )
}

// 헬퍼 함수들
function determineStrategyType(strategy: any): string {
  const indicators = Array.isArray(strategy?.indicators) ? strategy.indicators : []
  const hasMA = indicators.some((i: any) => i.type?.includes('MA') || i.type?.includes('EMA'))
  const hasRSI = indicators.some((i: any) => i.type === 'RSI')
  const hasMACD = indicators.some((i: any) => i.type === 'MACD')

  if (hasMA && !hasRSI && !hasMACD) return '추세 추종'
  if (hasRSI && !hasMA) return '모멘텀'
  if (hasMA && hasRSI) return '복합 전략'
  if (hasMACD) return '시그널 기반'
  return '커스텀'
}

function calculateComplexity(strategy: any): string {
  const total = (Array.isArray(strategy?.indicators) ? strategy.indicators.length : 0) +
                (Array.isArray(strategy?.buyConditions) ? strategy.buyConditions.length : 0) +
                (Array.isArray(strategy?.sellConditions) ? strategy.sellConditions.length : 0)

  if (total <= 3) return '단순'
  if (total <= 6) return '보통'
  if (total <= 10) return '복잡'
  return '매우 복잡'
}

function assessRiskLevel(strategy: any): string {
  const hasStopLoss = strategy?.riskManagement?.stopLoss
  const conditions = (Array.isArray(strategy?.buyConditions) ? strategy.buyConditions.length : 0) +
                     (Array.isArray(strategy?.sellConditions) ? strategy.sellConditions.length : 0)

  if (hasStopLoss && conditions > 3) return '낮음'
  if (hasStopLoss || conditions > 3) return '보통'
  return '높음'
}

function determineMarketFit(strategy: any): string {
  const indicators = Array.isArray(strategy?.indicators) ? strategy.indicators : []
  const hasVolume = indicators.some((i: any) => i.type?.includes('Volume'))
  const hasTrend = indicators.some((i: any) => i.type?.includes('MA'))

  if (hasTrend && hasVolume) return '모든 시장'
  if (hasTrend) return '추세 시장'
  if (hasVolume) return '변동성 시장'
  return '횡보 시장'
}

// 지표 한글 이름 변환
function getIndicatorKoreanName(type: string): string {
  const names: any = {
    'RSI': 'RSI (상대강도지수)',
    'RSI_14': 'RSI-14 (상대강도지수)',
    'RSI_9': 'RSI-9 (단기 상대강도지수)',
    'SMA': '단순 이동평균선',
    'MA_5': '5일 이동평균선',
    'MA_20': '20일 이동평균선',
    'MA_60': '60일 이동평균선',
    'MA_120': '120일 이동평균선',
    'EMA': '지수 이동평균선',
    'MACD': 'MACD',
    'MACD_SIGNAL': 'MACD 시그널',
    'BB': '볼린저 밴드',
    'BB_UPPER': '볼린저 밴드 상단',
    'BB_LOWER': '볼린저 밴드 하단',
    'BB_MIDDLE': '볼린저 밴드 중심',
    'Stochastic': '스토캐스틱',
    'Volume': '거래량',
    'VOLUME': '거래량',
    'VOLUME_MA_20': '20일 평균 거래량',
    'PRICE': '현재가',
    'close': '종가'
  }

  return names[type] || type
}

// 상세한 지표 정보 반환
function getDetailedIndicatorInfo(type: string): {
  koreanName?: string
  description: string
  formula?: string
  interpretation: string
  visualExample?: string
  tips?: string
} {
  const indicators: any = {
    'RSI': {
      koreanName: 'RSI (상대강도지수)',
      description: 'RSI는 일정 기간 동안의 가격 상승폭과 하락폭의 비율을 계산하여 0~100 사이의 값으로 표현하는 모멘텀 지표입니다. 주가의 과매수/과매도 상태를 판단하는 데 효과적입니다.',
      formula: 'RSI = 100 - (100 / (1 + RS))\nRS = 평균 상승폭 / 평균 하락폭',
      interpretation: '• 70 이상: 과매수 구간 (하락 가능성)\n• 30 이하: 과매도 구간 (상승 가능성)\n• 50 기준: 상승/하락 추세 판단\n• 다이버전스: 가격과 RSI의 방향이 다른 경우',
      visualExample: '100 │\n    │  과매수 영역\n 70 ├─────────────\n    │     ╭─╮\n 50 ├────╯  ╰────\n    │           ╰╮\n 30 ├────────────╯\n    │  과매도 영역\n  0 └──────────────→',
      tips: 'RSI는 횡보장에서는 50을 중심으로 오르락을 반복합니다. 강한 상승추세에서는 70 이상에서도 계속 상승할 수 있으므로 다른 지표와 함께 사용하세요.'
    },
    'MACD': {
      koreanName: 'MACD (이동평균수렴확산)',
      description: 'MACD는 단기 지수이동평균(12일)과 장기 지수이동평균(26일)의 차이를 나타내는 추세 추종 지표입니다. MACD선과 시그널선(9일)의 교차를 통해 매매 시점을 포착합니다.',
      formula: 'MACD = EMA(12) - EMA(26)\n시그널 = EMA(MACD, 9)\n히스토그램 = MACD - 시그널',
      interpretation: '• MACD > 시그널: 상승 추세\n• MACD < 시그널: 하락 추세\n• 골든크로스: MACD가 시그널을 상향 돌파\n• 데드크로스: MACD가 시그널을 하향 돌파\n• 0선 상향/하향: 추세 전환',
      visualExample: '  +  │     MACD\n     │    ╭───╮\n  0  ├───╯────╰── 시그널\n     │         ╰─╮\n  -  │           ╰─\n     └────────────→\n     ↑ 골든크로스  ↑ 데드크로스',
      tips: 'MACD는 추세가 강한 시장에서 효과적이며, 횡보장에서는 거짓 신호가 많습니다. 히스토그램의 크기와 방향도 함께 확인하세요.'
    },
    'BB': {
      koreanName: '볼린저 밴드',
      description: '볼린저밴드는 이동평균선을 중심으로 표준편차의 2배 거리에 상하한선을 그려 가격의 변동성과 추세를 파악하는 지표입니다. 밴드의 폭이 좁으면 변동성이 낮고, 넓으면 변동성이 높습니다.',
      formula: '중심선 = SMA(20)\n상단밴드 = 중심선 + (2 × 표준편차)\n하단밴드 = 중심선 - (2 × 표준편차)',
      interpretation: '• 상단밴드 터치: 매도 신호\n• 하단밴드 터치: 매수 신호\n• 밴드 폭 축소: 변동성 감소 (돌파 대기)\n• 밴드 폭 확대: 변동성 증가\n• 밴드 외부 이탈: 추세 가속',
      visualExample: '     ┌───────────┐ 상단밴드\n     │    ╭─╮    │\n     │   ╭╯  ╰╮   │\n─────├──╯────╰──├──── 중심선\n     │          │\n     └───────────┘ 하단밴드\n      ↑ 스퀘즈 구간',
      tips: '밴드 폭이 좁아지는 "스퀘즈" 후 강한 방향성 움직임이 나타날 가능성이 높습니다. 밴드 외부에서 다시 내부로 돌아오는 패턴도 주의 깊게 관찰하세요.'
    },
    'SMA': {
      koreanName: '단순이동평균선',
      description: '단순이동평균선은 일정 기간 동안의 종가를 단순 평균하여 계산하는 가장 기본적인 추세 지표입니다. 가격의 노이즈를 제거하고 추세를 파악하는 데 사용됩니다.',
      formula: 'SMA(n) = (최근 n일간의 종가 합) / n',
      interpretation: '• 가격 > SMA: 상승 추세\n• 가격 < SMA: 하락 추세\n• 단기 MA > 장기 MA: 골든크로스 (매수)\n• 단기 MA < 장기 MA: 데드크로스 (매도)\n• 지지/저항선 역할',
      visualExample: '가격  ╭─────╮\n     │      ╰─╮\n─────╯────────╰── MA20\n             ╰─── MA60\n     ↑ 골든크로스',
      tips: '이동평균선은 후행성 지표이므로 추세 전환 시점을 빨리 포착하지 못합니다. 여러 기간의 이동평균선을 함께 사용하여 추세의 강도를 판단하세요.'
    },
    'Volume': {
      koreanName: '거래량',
      description: '거래량은 일정 기간 동안 거래된 주식의 수량을 나타내며, 가격 움직임의 강도와 신뢰성을 확인하는 중요한 지표입니다.',
      interpretation: '• 가격 상승 + 거래량 증가: 강세 지속\n• 가격 상승 + 거래량 감소: 상승 한계\n• 가격 하락 + 거래량 증가: 바닥 확인\n• 평균 거래량 대비 2배 이상: 주목',
      visualExample: '거래량\n│██\n│██    ██\n│██ ██ ██    ██\n│██ ██ ██ ██ ██\n└─────────────→\n ↑가격상승  ↑돌파',
      tips: '거래량은 가격보다 선행하는 경향이 있습니다. 거래량이 먼저 증가하면 가격 변동을 예상할 수 있습니다.'
    },
    'Stochastic': {
      koreanName: '스토캐스틱',
      description: '스토캐스틱은 일정 기간 동안의 최고가와 최저가 범위에서 현재 가격의 상대적 위치를 0~100으로 표현하는 모멘텀 지표입니다.',
      formula: '%K = ((C - L14) / (H14 - L14)) × 100\n%D = MA(%K, 3)\nC: 현재가, L14: 14일 최저가, H14: 14일 최고가',
      interpretation: '• 80 이상: 과매수 구간\n• 20 이하: 과매도 구간\n• %K > %D: 매수 신호\n• %K < %D: 매도 신호',
      visualExample: '100 │\n 80 ├──────────\n    │  %K ╭─╮\n    │ %D ╭╯  ╰╮\n 20 ├───╯────╰─\n  0 └──────────→',
      tips: '스토캐스틱은 횡보장에서 효과적이며, 추세장에서는 과매수/과매도 상태가 지속될 수 있습니다.'
    }
  }

  // 기본 지표 찾기
  for (const [key, value] of Object.entries(indicators)) {
    if (type.toUpperCase().includes(key.toUpperCase())) {
      return value as any
    }
  }

  // 기본값 반환
  return {
    description: '이 지표는 시장의 특정 패턴을 분석하여 매매 시점을 포착하는 데 사용됩니다.',
    interpretation: '지표의 값과 방향성을 통해 매수/매도 시점을 판단합니다.',
    tips: '단일 지표만으로 판단하지 말고 여러 지표를 조합하여 사용하세요.'
  }
}

function getIndicatorDescription(type: string): string {
  const info = getDetailedIndicatorInfo(type)
  return info.description
}

function getIndicatorSignal(type: string): string {
  const signals: any = {
    'RSI': 'RSI < 30 매수, RSI > 70 매도',
    'RSI_14': 'RSI < 30 과매도 구간 매수, RSI > 70 과매수 구간 매도',
    'RSI_9': 'RSI < 30 단기 과매도 매수, RSI > 70 단기 과매수 매도',
    'SMA': '단기 MA > 장기 MA 매수, 단기 MA < 장기 MA 매도',
    'MA': '가격 > MA 상승 추세, 가격 < MA 하락 추세',
    'EMA': 'EMA 상향돌파 매수, 하향돌파 매도',
    'MACD': 'MACD가 시그널선 상향돌파 매수, 하향돌파 매도',
    'BB': '하단 밴드 터치 매수, 상단 밴드 터치 매도',
    'Stochastic': '%K가 %D 상향돌파 매수, 하향돌파 매도',
    'Volume': '거래량 급증 시 추세 전환 가능성',
    'PRICE': '설정된 가격 조건에 따라 매매 결정'
  }

  // 정확한 매칭 먼저 시도
  if (signals[type]) {
    return signals[type]
  }

  // 부분 매칭 시도
  for (const [key, value] of Object.entries(signals)) {
    if (type.toUpperCase().includes(key.toUpperCase())) return value as string
  }
  return '지표 값에 따라 매매 시점을 결정합니다.'
}

function generateOptimizationSuggestions(strategy: any): any[] {
  const suggestions = []

  // 전체 사용된 지표 수집 (indicators 배열 + 조건에서 사용된 지표)
  const usedIndicators = new Set<string>()

  // indicators 배열에서 지표 수집
  if (Array.isArray(strategy?.indicators)) {
    strategy.indicators.forEach((ind: any) => {
      if (ind.type) usedIndicators.add(ind.type)
      if (ind.id) usedIndicators.add(ind.id)
      if (ind.name) usedIndicators.add(ind.name)
    })
  }

  // 매수 조건에서 지표 수집
  if (Array.isArray(strategy?.buyConditions)) {
    strategy.buyConditions.forEach((cond: any) => {
      if (cond.indicator) usedIndicators.add(cond.indicator)
    })
  }

  // 매도 조건에서 지표 수집
  if (Array.isArray(strategy?.sellConditions)) {
    strategy.sellConditions.forEach((cond: any) => {
      if (cond.indicator) usedIndicators.add(cond.indicator)
    })
  }

  const indicatorCount = usedIndicators.size
  const buyCount = Array.isArray(strategy?.buyConditions) ? strategy.buyConditions.length : 0
  const sellCount = Array.isArray(strategy?.sellConditions) ? strategy.sellConditions.length : 0

  // 조건 체크
  if (buyCount === 0 && sellCount === 0) {
    suggestions.push({
      severity: 'error',
      icon: <ErrorOutline />,
      title: '매매 조건 없음',
      description: '매수 또는 매도 조건을 최소 1개 이상 설정해야 합니다.'
    })
  }

  // 매수 조건 체크
  if (buyCount === 0) {
    suggestions.push({
      severity: 'error',
      icon: <ErrorOutline />,
      title: '매수 조건 없음',
      description: '언제 매수할지 결정하는 조건을 추가하세요.'
    })
  } else if (buyCount > 5) {
    suggestions.push({
      severity: 'warning',
      icon: <Warning />,
      title: '과도한 매수 조건',
      description: `${buyCount}개의 매수 조건은 너무 복잡합니다. 3-4개로 간소화를 고려하세요.`
    })
  }

  // 매도 조건 체크
  if (sellCount === 0) {
    suggestions.push({
      severity: 'error',
      icon: <ErrorOutline />,
      title: '매도 조건 없음',
      description: '언제 매도할지 결정하는 조건을 추가하세요.'
    })
  } else if (sellCount > 5) {
    suggestions.push({
      severity: 'warning',
      icon: <Warning />,
      title: '과도한 매도 조건',
      description: `${sellCount}개의 매도 조건은 너무 복잡합니다. 3-4개로 간소화를 고려하세요.`
    })
  }

  // 매수/매도 조건 균형
  if (buyCount > 0 && sellCount > 0 && Math.abs(buyCount - sellCount) > 3) {
    suggestions.push({
      severity: 'warning',
      icon: <Warning />,
      title: '조건 불균형',
      description: `매수 조건(${buyCount}개)과 매도 조건(${sellCount}개)의 균형을 맞추는 것이 좋습니다.`
    })
  }

  // 리스크 관리
  const stopLoss = strategy?.riskManagement?.stopLoss
  const takeProfit = strategy?.riskManagement?.takeProfit

  if (!stopLoss || stopLoss === 0) {
    suggestions.push({
      severity: 'error',
      icon: <ErrorOutline />,
      title: '손절매 미설정',
      description: '큰 손실을 방지하기 위해 손절매 비율을 설정하세요. (권장: -3% ~ -10%)'
    })
  } else if (Math.abs(stopLoss) > 20) {
    suggestions.push({
      severity: 'warning',
      icon: <Warning />,
      title: '과도한 손절매 비율',
      description: `손절매 ${stopLoss}%는 너무 큽니다. -5% ~ -10% 사이를 권장합니다.`
    })
  }

  if (!takeProfit || takeProfit === 0) {
    suggestions.push({
      severity: 'info',
      icon: <Info />,
      title: '익절매 미설정',
      description: '목표 수익률을 설정하면 수익을 안정적으로 확보할 수 있습니다.'
    })
  } else if (takeProfit > 50) {
    suggestions.push({
      severity: 'warning',
      icon: <Warning />,
      title: '비현실적인 익절매 목표',
      description: `익절매 ${takeProfit}%는 달성하기 어려울 수 있습니다. 10% ~ 30% 사이를 권장합니다.`
    })
  }

  // 트레일링 스탑 권장
  if (!strategy?.riskManagement?.trailingStop && takeProfit > 10) {
    suggestions.push({
      severity: 'info',
      icon: <Lightbulb />,
      title: '트레일링 스탑 활용',
      description: '수익이 발생했을 때 트레일링 스탑을 사용하면 수익을 보호하면서 추가 상승 여력을 남길 수 있습니다.'
    })
  }

  // 포지션 크기 체크
  const positionSize = strategy?.riskManagement?.positionSize
  if (positionSize > 30) {
    suggestions.push({
      severity: 'warning',
      icon: <Warning />,
      title: '과도한 포지션 크기',
      description: `한 종목에 ${positionSize}%는 위험합니다. 10% ~ 20% 사이를 권장합니다.`
    })
  }

  // 지표별 특별 제안
  const indicatorArray = Array.from(usedIndicators)

  // RSI 사용 시
  if (indicatorArray.some(ind => ind.toUpperCase().includes('RSI'))) {
    const hasRSIBuy = strategy?.buyConditions?.some((c: any) =>
      c.indicator?.toUpperCase().includes('RSI') && c.value < 40
    )
    const hasRSISell = strategy?.sellConditions?.some((c: any) =>
      c.indicator?.toUpperCase().includes('RSI') && c.value > 60
    )

    if (!hasRSIBuy || !hasRSISell) {
      suggestions.push({
        severity: 'info',
        icon: <Lightbulb />,
        title: 'RSI 활용 팁',
        description: 'RSI는 30 이하에서 매수, 70 이상에서 매도가 일반적입니다. 시장 상황에 따라 조정하세요.'
      })
    }
  }

  // 이동평균선 사용 시
  if (indicatorArray.some(ind => ind.toUpperCase().includes('MA') || ind.toUpperCase().includes('SMA') || ind.toUpperCase().includes('EMA'))) {
    suggestions.push({
      severity: 'info',
      icon: <Lightbulb />,
      title: '이동평균선 교차 전략',
      description: '단기/장기 이동평균선의 골든크로스(상향돌파)와 데드크로스(하향돌파)를 활용해보세요.'
    })
  }

  // MACD 사용 시
  if (indicatorArray.some(ind => ind.toUpperCase().includes('MACD'))) {
    suggestions.push({
      severity: 'info',
      icon: <Lightbulb />,
      title: 'MACD 다이버전스',
      description: 'MACD와 가격의 다이버전스는 강력한 전환 신호입니다. 히스토그램도 함께 확인하세요.'
    })
  }

  // 볼린저밴드 사용 시
  if (indicatorArray.some(ind => ind.toUpperCase().includes('BB'))) {
    suggestions.push({
      severity: 'info',
      icon: <Lightbulb />,
      title: '볼린저밴드 스퀴즈',
      description: '밴드 폭이 좁아지는 스퀴즈 후 방향성 돌파는 강한 추세의 시작을 알립니다.'
    })
  }

  // 거래량 지표가 없는 경우
  if (!indicatorArray.some(ind => ind.toUpperCase().includes('VOLUME'))) {
    suggestions.push({
      severity: 'info',
      icon: <Info />,
      title: '거래량 지표 추가 고려',
      description: '거래량은 가격 움직임의 신뢰도를 확인하는 중요한 지표입니다. 거래량 조건 추가를 고려하세요.'
    })
  }

  // 긍정적 피드백
  if (suggestions.length === 0 || (suggestions.length === 1 && suggestions[0].severity === 'info')) {
    suggestions.push({
      severity: 'success',
      icon: <CheckCircle />,
      title: '잘 구성된 전략',
      description: '전략이 균형잡혀 있습니다. 백테스트를 통해 성과를 검증해보세요.'
    })
  }

  // 종합 점수 계산
  let score = 100
  suggestions.forEach(s => {
    if (s.severity === 'error') score -= 20
    else if (s.severity === 'warning') score -= 10
  })

  suggestions.unshift({
    severity: score >= 80 ? 'success' : score >= 60 ? 'warning' : 'error',
    icon: <Assessment />,
    title: `전략 완성도: ${Math.max(0, score)}%`,
    description: score >= 80 ? '훌륭한 전략입니다!' :
                 score >= 60 ? '개선의 여지가 있습니다.' :
                 '중요한 요소들을 보완해주세요.'
  })

  return suggestions
}

export default StrategyAnalyzer