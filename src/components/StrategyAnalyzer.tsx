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
                                    {koreanName || getIndicatorKoreanName(indicatorName)} ({indicatorName})
                                  </Typography>
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
    'MA': '이동평균선',
    'MA_5': '5일 이동평균선',
    'MA_20': '20일 이동평균선',
    'MA_60': '60일 이동평균선',
    'MA_120': '120일 이동평균선',
    'EMA': '지수 이동평균선',
    'MACD': 'MACD (이동평균수렴확산)',
    'MACD_SIGNAL': 'MACD 시그널',
    'BB': '볼린저 밴드',
    'BB_UPPER': '볼린저 밴드 상단',
    'BB_LOWER': '볼린저 밴드 하단',
    'BB_MIDDLE': '볼린저 밴드 중심',
    'Stochastic': '스토캐스틱',
    'STOCH': '스토캐스틱',
    'Volume': '거래량',
    'VOLUME': '거래량',
    'VOLUME_MA_20': '20일 평균 거래량',
    'PRICE': '현재가',
    'close': '종가',
    'open': '시가',
    'high': '고가',
    'low': '저가',
    'Ichimoku': '일목균형표',
    'ICHIMOKU': '일목균형표',
    'ICHIMOKU_CONVERSION': '일목균형표 전환선',
    'ICHIMOKU_BASE': '일목균형표 기준선',
    'ICHIMOKU_SPAN_A': '일목균형표 선행스팬A',
    'ICHIMOKU_SPAN_B': '일목균형표 선행스팬B',
    'ICHIMOKU_LAGGING': '일목균형표 후행스팬',
    'ATR': 'ATR (평균진폭지표)',
    'CCI': 'CCI (상품채널지수)',
    'Williams': '윌리엄스 %R',
    'WilliamsR': '윌리엄스 %R',
    'ADX': 'ADX (평균방향성지표)',
    'OBV': 'OBV (거래량균형지표)',
    'ROC': 'ROC (변화율)',
    'MFI': 'MFI (자금흐름지표)',
    'VWAP': 'VWAP (거래량가중평균가격)',
    'Parabolic': '파라볼릭 SAR',
    'ParabolicSAR': '파라볼릭 SAR',
    'ZigZag': '지그재그',
    'Envelope': '엔벨로프',
    'Pivot': '피벗포인트',
    'Fibonacci': '피보나치',
    'TRIX': 'TRIX',
    'DMI': 'DMI (방향성지표)'
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
    },
    'Ichimoku': {
      koreanName: '일목균형표',
      description: '일목균형표는 일본에서 개발된 종합적인 추세 지표로, 5개의 선을 이용하여 지지/저항선, 추세 방향, 매매 시점을 한눈에 파악할 수 있습니다.',
      formula: '전환선 = (9일 최고가 + 9일 최저가) / 2\n기준선 = (26일 최고가 + 26일 최저가) / 2\n선행스팬A = (전환선 + 기준선) / 2 (26일 선행)\n선행스팬B = (52일 최고가 + 52일 최저가) / 2 (26일 선행)\n후행스팬 = 현재 종가 (26일 후행)',
      interpretation: '• 전환선 > 기준선: 상승 추세\n• 가격 > 구름대: 강세\n• 가격 < 구름대: 약세\n• 구름대 내부: 보합/전환 구간\n• 구름대 두께: 지지/저항 강도',
      visualExample: '     ╱───── 선행스팬A\n    ╱ 구름대\n───────────── 기준선\n  ╱ ╲   ╱─── 전환선\n ╱   ╲ ╱\n╱─────╲───── 선행스팬B',
      tips: '일목균형표는 모든 시장 상황을 종합적으로 보여주는 강력한 지표입니다. 구름대의 색깔 변화와 두께를 주의 깊게 관찰하세요.'
    },
    'ATR': {
      koreanName: 'ATR (평균진폭지표)',
      description: 'ATR은 가격의 변동성을 측정하는 지표로, 일정 기간 동안의 실질 변동폭(True Range)의 평균을 계산합니다.',
      formula: 'TR = Max(고가-저가, |고가-전일종가|, |저가-전일종가|)\nATR = MA(TR, 14)',
      interpretation: '• ATR 상승: 변동성 증가\n• ATR 하락: 변동성 감소\n• 손절/익절 설정 기준\n• 포지션 크기 결정',
      tips: 'ATR은 가격의 방향이 아닌 변동성만을 측정합니다. 추세 지표와 함께 사용하여 진입/청산 수준을 결정하세요.'
    },
    'EMA': {
      koreanName: '지수이동평균선',
      description: 'EMA는 최근 가격에 더 많은 가중치를 부여하는 이동평균선으로, SMA보다 가격 변화에 민감하게 반응합니다.',
      formula: 'EMA = (현재가 × K) + (전일 EMA × (1-K))\nK = 2 / (N + 1), N은 기간',
      interpretation: '• 가격 > EMA: 상승 추세\n• 가격 < EMA: 하락 추세\n• 단기 EMA > 장기 EMA: 상승 신호\n• EMA의 기울기: 추세 강도',
      visualExample: '가격 ╭──╮\n    ╱    ╰─╮\n───╯ EMA12 ╰──\n──────EMA26───',
      tips: 'EMA는 SMA보다 빠르게 반응하지만 거짓 신호도 많을 수 있습니다. 다른 지표와 함께 사용하세요.'
    },
    'CCI': {
      koreanName: 'CCI (상품채널지수)',
      description: 'CCI는 현재 가격이 평균 가격으로부터 얼마나 떨어져 있는지를 측정하는 모멘텀 지표입니다.',
      formula: 'CCI = (TP - MA) / (0.015 × MD)\nTP = (고가+저가+종가)/3\nMA = TP의 이동평균\nMD = 평균편차',
      interpretation: '• CCI > 100: 과매수 (매도 고려)\n• CCI < -100: 과매도 (매수 고려)\n• 0선 상향돌파: 상승 추세\n• 0선 하향돌파: 하락 추세',
      visualExample: '+200│\n+100├─────────\n   0├─╱───╲───\n-100├─────────\n-200│',
      tips: 'CCI는 -100과 +100을 벗어날 때 강한 추세를 나타냅니다. 횡보장에서는 ±100 내에서 움직입니다.'
    },
    'Williams': {
      koreanName: '윌리엄스 %R',
      description: '윌리엄스 %R은 일정 기간의 최고가와 최저가 대비 현재 가격의 위치를 나타내는 모멘텀 지표입니다.',
      formula: '%R = (최고가 - 현재가) / (최고가 - 최저가) × -100',
      interpretation: '• %R > -20: 과매수 구간\n• %R < -80: 과매도 구간\n• -50 기준: 추세 방향\n• 다이버전스: 추세 전환 신호',
      visualExample: '  0│\n-20├─────과매수\n-50├───╱╲────\n-80├─────과매도\n-100│',
      tips: '스토캐스틱과 유사하지만 역방향으로 표시됩니다. 단기 매매 타이밍 포착에 유용합니다.'
    },
    'ADX': {
      koreanName: 'ADX (평균방향성지표)',
      description: 'ADX는 추세의 강도를 측정하는 지표로, 방향과 관계없이 추세가 얼마나 강한지를 나타냅니다.',
      formula: 'ADX = MA(DX, 14)\nDX = |+DI - -DI| / (+DI + -DI) × 100',
      interpretation: '• ADX > 40: 매우 강한 추세\n• ADX 25-40: 강한 추세\n• ADX 20-25: 추세 존재\n• ADX < 20: 추세 없음 (횡보)',
      visualExample: '50│    ╭─╮\n40├───╯  ╰\n25├────────\n20├────────\n 0└────────→',
      tips: 'ADX는 추세의 방향이 아닌 강도만 측정합니다. +DI와 -DI의 교차로 방향을 판단하세요.'
    },
    'OBV': {
      koreanName: 'OBV (거래량균형지표)',
      description: 'OBV는 거래량을 누적하여 가격 움직임을 예측하는 선행 지표입니다. 가격 상승일에는 거래량을 더하고 하락일에는 뺍니다.',
      formula: '가격 상승시: OBV = 전일 OBV + 거래량\n가격 하락시: OBV = 전일 OBV - 거래량',
      interpretation: '• OBV 상승 + 가격 상승: 상승 지속\n• OBV 하락 + 가격 하락: 하락 지속\n• OBV↑ 가격↓: 매수 신호\n• OBV↓ 가격↑: 매도 신호',
      visualExample: 'OBV  ╱───╮\n    ╱    ╰─\n───╯\n가격 ╱╲╱╲',
      tips: 'OBV의 다이버전스는 중요한 전환 신호입니다. 거래량이 가격을 선행한다는 원리를 활용하세요.'
    },
    'ROC': {
      koreanName: 'ROC (변화율)',
      description: 'ROC는 현재 가격과 N일 전 가격의 변화율을 백분율로 나타내는 모멘텀 지표입니다.',
      formula: 'ROC = ((현재가 - N일전가) / N일전가) × 100',
      interpretation: '• ROC > 0: 상승 모멘텀\n• ROC < 0: 하락 모멘텀\n• ROC 상승: 모멘텀 강화\n• 0선 교차: 추세 전환',
      visualExample: '+10│  ╱╲\n  0├─╯──╲──\n-10│     ╲╱',
      tips: 'ROC는 과매수/과매도 수준이 고정되어 있지 않습니다. 종목별 특성을 파악하여 사용하세요.'
    },
    'MFI': {
      koreanName: 'MFI (자금흐름지표)',
      description: 'MFI는 가격과 거래량을 함께 고려하는 모멘텀 지표로, RSI에 거래량을 추가한 개념입니다.',
      formula: 'MFI = 100 - (100 / (1 + MR))\nMR = 양의 자금흐름 / 음의 자금흐름',
      interpretation: '• MFI > 80: 과매수\n• MFI < 20: 과매도\n• 50 기준: 강세/약세\n• 다이버전스: 추세 전환',
      visualExample: '100│\n 80├────────\n 50├──╱╲╱───\n 20├────────\n  0│',
      tips: 'MFI는 거래량을 포함하므로 RSI보다 더 신뢰할 수 있는 신호를 제공합니다.'
    },
    'VWAP': {
      koreanName: 'VWAP (거래량가중평균가격)',
      description: 'VWAP은 거래량으로 가중평균한 평균 가격으로, 기관의 평균 매수가격을 추정하는 데 사용됩니다.',
      formula: 'VWAP = Σ(가격 × 거래량) / Σ거래량',
      interpretation: '• 가격 > VWAP: 매수세 우위\n• 가격 < VWAP: 매도세 우위\n• VWAP 상향돌파: 매수 신호\n• VWAP 하향돌파: 매도 신호',
      visualExample: '가격 ╱╲╱╲\n────VWAP───\n    ╲╱╲╱',
      tips: 'VWAP은 일중 매매에서 중요한 지지/저항선 역할을 합니다. 기관의 평균 매수가 추정에 유용합니다.'
    },
    'Parabolic': {
      koreanName: '파라볼릭 SAR',
      description: '파라볼릭 SAR은 추세 전환점을 포착하는 지표로, 가격 위나 아래에 점으로 표시됩니다.',
      formula: 'SAR = 전일SAR + AF × (EP - 전일SAR)\nAF: 가속계수(0.02~0.2)\nEP: 극점(최고/최저가)',
      interpretation: '• SAR이 가격 아래: 상승 추세\n• SAR이 가격 위: 하락 추세\n• SAR 전환: 추세 전환\n• AF 증가: 추세 가속',
      visualExample: '가격 ╱─╲\n    •  •╲\n   •     •\n  •       •',
      tips: '파라볼릭 SAR은 추세장에서 효과적이며, 횡보장에서는 거짓 신호가 많습니다.'
    },
    'DMI': {
      koreanName: 'DMI (방향성지표)',
      description: 'DMI는 추세의 방향과 강도를 나타내는 지표로, +DI와 -DI의 교차로 매매 신호를 포착합니다.',
      formula: '+DI = (+DM / TR) × 100\n-DI = (-DM / TR) × 100',
      interpretation: '• +DI > -DI: 상승 추세\n• -DI > +DI: 하락 추세\n• 교차점: 매매 신호\n• ADX와 함께 사용',
      visualExample: '  ╱+DI╲\n ╱    ╲\n╱ -DI  ╲',
      tips: 'DMI는 ADX와 함께 사용하여 추세의 방향과 강도를 동시에 파악할 수 있습니다.'
    },
    'TRIX': {
      koreanName: 'TRIX',
      description: 'TRIX는 3중 지수이동평균의 변화율을 나타내는 모멘텀 지표로, 노이즈를 제거한 깨끗한 신호를 제공합니다.',
      formula: 'TRIX = (EMA3 - 전일EMA3) / 전일EMA3 × 10000\nEMA3 = EMA(EMA(EMA(종가)))',
      interpretation: '• TRIX > 0: 상승 모멘텀\n• TRIX < 0: 하락 모멘텀\n• 0선 상향돌파: 매수\n• 0선 하향돌파: 매도',
      tips: 'TRIX는 3중 평활화로 거짓 신호를 줄이지만, 신호가 늦을 수 있습니다.'
    },
    'Pivot': {
      koreanName: '피벗포인트',
      description: '피벗포인트는 전일 가격을 기준으로 당일의 지지/저항선을 계산하는 선행 지표입니다.',
      formula: 'PP = (전일고가 + 전일저가 + 전일종가) / 3\nR1 = 2×PP - 전일저가\nS1 = 2×PP - 전일고가',
      interpretation: '• PP 상향돌파: 상승 추세\n• PP 하향돌파: 하락 추세\n• R1, R2: 저항선\n• S1, S2: 지지선',
      visualExample: 'R2────────\nR1────────\nPP════════\nS1────────\nS2────────',
      tips: '피벗포인트는 일중 매매에서 중요한 가격대를 미리 파악할 수 있게 해줍니다.'
    },
    'Fibonacci': {
      koreanName: '피보나치',
      description: '피보나치 되돌림은 추세의 조정 수준을 예측하는 도구로, 주요 비율(23.6%, 38.2%, 50%, 61.8%)을 사용합니다.',
      formula: '되돌림 = 고점 - (고점-저점) × 비율',
      interpretation: '• 23.6%: 약한 조정\n• 38.2%: 일반 조정\n• 50%: 중간 조정\n• 61.8%: 깊은 조정',
      visualExample: '100%────\n61.8%───\n50%─────\n38.2%───\n23.6%───\n0%──────',
      tips: '피보나치 수준은 자연스러운 지지/저항선으로 작용합니다. 다른 기술적 지표와 함께 사용하세요.'
    },
    'ZigZag': {
      koreanName: '지그재그',
      description: '지그재그는 일정 비율 이상의 가격 변동만을 연결하여 추세를 명확하게 보여주는 지표입니다.',
      formula: '변동률 > 설정값(보통 5~10%)일 때만 전환점 표시',
      interpretation: '• 고점/저점 확인\n• 추세선 작도\n• 패턴 인식\n• 엘리엇 파동 분석',
      visualExample: '  ╱╲\n ╱  ╲\n╱    ╲╱╲',
      tips: '지그재그는 과거 데이터를 정리하는 도구로, 실시간 매매 신호로는 부적합합니다.'
    },
    'Envelope': {
      koreanName: '엔벨로프',
      description: '엔벨로프는 이동평균선을 중심으로 일정 비율의 상하한선을 그려 가격의 과매수/과매도를 판단합니다.',
      formula: '상한선 = MA × (1 + 비율)\n하한선 = MA × (1 - 비율)',
      interpretation: '• 상한선 터치: 매도 고려\n• 하한선 터치: 매수 고려\n• 밴드 이탈: 강한 추세\n• 밴드 내 복귀: 조정',
      visualExample: '┌─────────┐\n│  ╱╲╱╲  │\n├─────────┤\n│         │\n└─────────┘',
      tips: '엔벨로프는 볼린저밴드와 달리 고정 비율을 사용하므로 변동성 변화를 반영하지 못합니다.'
    },
    // 가격 데이터 지표들
    'PRICE': {
      koreanName: '현재가',
      description: '현재가는 실시간으로 거래되는 주식의 현재 가격을 나타냅니다.',
      interpretation: '• 지지선 돌파: 하락 신호\n• 저항선 돌파: 상승 신호\n• 전일 종가 대비: 등락률\n• 52주 신고가/신저가',
      tips: '가격 자체보다는 지지/저항선과의 관계, 거래량과의 연관성을 함께 분석하세요.'
    },
    'close': {
      koreanName: '종가',
      description: '종가는 거래일의 마지막 거래 가격으로, 대부분의 기술적 지표 계산의 기준이 됩니다.',
      interpretation: '• 전일 종가 돌파: 상승 추세\n• 전일 종가 하향: 하락 추세\n• 갭 상승/하락: 강한 신호',
      tips: '종가는 가장 중요한 가격 데이터로, 대부분의 차트 분석의 기준점이 됩니다.'
    },
    'open': {
      koreanName: '시가',
      description: '시가는 거래일의 첫 거래 가격으로, 당일 시장 심리를 반영합니다.',
      interpretation: '• 갭 상승: 강세 시작\n• 갭 하락: 약세 시작\n• 시가=종가: 도지 캔들',
      tips: '시가와 종가의 관계로 캔들 패턴을 파악할 수 있습니다.'
    },
    'high': {
      koreanName: '고가',
      description: '고가는 거래일 중 최고 거래 가격으로, 당일 매수세의 최대 강도를 나타냅니다.',
      interpretation: '• 전일 고가 돌파: 상승 추세 강화\n• 고가 = 종가: 강한 상승세\n• 고가 갱신 실패: 저항',
      tips: '고가는 저항선으로 작용할 수 있으며, 돌파 시 추가 상승 가능성이 높습니다.'
    },
    'low': {
      koreanName: '저가',
      description: '저가는 거래일 중 최저 거래 가격으로, 당일 매도세의 최대 강도를 나타냅니다.',
      interpretation: '• 전일 저가 하향: 하락 추세 강화\n• 저가 = 종가: 강한 하락세\n• 저가 지지: 반등 가능',
      tips: '저가는 지지선으로 작용할 수 있으며, 하향 돌파 시 추가 하락 가능성이 높습니다.'
    },
    // 이동평균 변형들
    'MA': {
      koreanName: '이동평균선',
      description: '이동평균선은 일정 기간의 평균 가격을 연결한 선으로, 추세를 파악하는 기본 지표입니다.',
      interpretation: '• 가격 > MA: 상승 추세\n• 가격 < MA: 하락 추세\n• MA 기울기: 추세 강도',
      tips: '기간이 짧을수록 민감하고, 길수록 안정적입니다. 여러 기간을 함께 사용하세요.'
    },
    'MA_5': {
      koreanName: '5일 이동평균선',
      description: '5일 이동평균선은 초단기 추세를 나타내며, 단기 매매에 활용됩니다.',
      interpretation: '• 가격 > MA5: 초단기 상승\n• MA5 > MA20: 단기 상승 추세\n• 급격한 기울기 변화: 추세 전환',
      tips: '5일선은 노이즈가 많으므로 다른 지표와 함께 사용하세요.'
    },
    'MA_20': {
      koreanName: '20일 이동평균선',
      description: '20일 이동평균선은 단기 추세를 나타내며, 볼린저밴드의 중심선으로도 사용됩니다.',
      interpretation: '• 가격 > MA20: 단기 상승 추세\n• MA20 기울기: 추세 방향\n• 지지/저항선 역할',
      tips: '20일선은 단기 추세의 기준선으로 가장 많이 사용됩니다.'
    },
    'MA_60': {
      koreanName: '60일 이동평균선',
      description: '60일 이동평균선은 중기 추세를 나타내며, 계절적 변동을 반영합니다.',
      interpretation: '• 가격 > MA60: 중기 상승 추세\n• MA20 > MA60: 중기 강세\n• 강력한 지지/저항',
      tips: '60일선은 3개월 추세를 나타내며, 중요한 지지/저항선입니다.'
    },
    'MA_120': {
      koreanName: '120일 이동평균선',
      description: '120일 이동평균선은 중장기 추세를 나타내며, 반년간의 평균 가격을 반영합니다.',
      interpretation: '• 가격 > MA120: 중장기 상승 추세\n• MA60 > MA120: 장기 강세\n• 주요 추세선',
      tips: '120일선은 6개월 추세를 나타내며, 장기 투자의 기준선입니다.'
    },
    // RSI 변형들
    'RSI_14': {
      koreanName: 'RSI-14',
      description: 'RSI-14는 14일 기간의 상대강도지수로, 가장 표준적인 RSI 설정입니다.',
      interpretation: '• 70 이상: 과매수\n• 30 이하: 과매도\n• 50 기준: 강세/약세',
      tips: '14일 RSI는 가장 널리 사용되는 표준 설정입니다.'
    },
    'RSI_9': {
      koreanName: 'RSI-9',
      description: 'RSI-9는 9일 기간의 상대강도지수로, 더 민감한 단기 신호를 제공합니다.',
      interpretation: '• 더 빠른 신호 생성\n• 더 많은 거래 기회\n• 거짓 신호 증가 가능',
      tips: '단기 매매에 적합하지만, 거짓 신호에 주의하세요.'
    },
    // MACD 관련
    'MACD_SIGNAL': {
      koreanName: 'MACD 시그널',
      description: 'MACD 시그널선은 MACD의 9일 지수이동평균으로, MACD와의 교차로 매매 신호를 생성합니다.',
      interpretation: '• MACD > 시그널: 매수\n• MACD < 시그널: 매도\n• 교차점: 매매 시점',
      tips: 'MACD와 시그널선의 간격(히스토그램)도 함께 관찰하세요.'
    },
    // 볼린저밴드 구성요소
    'BB_UPPER': {
      koreanName: '볼린저밴드 상단',
      description: '볼린저밴드 상단선은 중심선 + (2×표준편차)로, 과매수 구간을 나타냅니다.',
      interpretation: '• 가격 터치: 매도 고려\n• 돌파 후 복귀: 강한 매도\n• 밴드 확장: 변동성 증가',
      tips: '상단선 돌파 후 재진입하는 패턴을 주목하세요.'
    },
    'BB_LOWER': {
      koreanName: '볼린저밴드 하단',
      description: '볼린저밴드 하단선은 중심선 - (2×표준편차)로, 과매도 구간을 나타냅니다.',
      interpretation: '• 가격 터치: 매수 고려\n• 돌파 후 복귀: 강한 매수\n• 밴드 축소: 변동성 감소',
      tips: '하단선 돌파 후 재진입하는 패턴은 강한 매수 신호입니다.'
    },
    'BB_MIDDLE': {
      koreanName: '볼린저밴드 중심',
      description: '볼린저밴드 중심선은 20일 이동평균선으로, 중기 추세를 나타냅니다.',
      interpretation: '• 가격 > 중심: 상승 추세\n• 가격 < 중심: 하락 추세\n• 지지/저항 역할',
      tips: '중심선은 20일 이동평균과 동일하며, 추세의 기준선입니다.'
    },
    // 거래량 관련
    'VOLUME': {
      koreanName: '거래량',
      description: '거래량은 일정 기간 동안 거래된 주식 수량으로, 가격 움직임의 신뢰도를 나타냅니다.',
      interpretation: '• 가격↑ 거래량↑: 상승 지속\n• 가격↑ 거래량↓: 상승 한계\n• 평균 대비 급증: 주목',
      tips: '거래량은 가격을 확인하는 지표입니다. 항상 함께 분석하세요.'
    },
    'VOLUME_MA_20': {
      koreanName: '20일 평균거래량',
      description: '20일 평균거래량은 최근 20일간의 평균 거래량으로, 거래량 급증/급감을 판단하는 기준입니다.',
      interpretation: '• 현재 > 평균: 관심 증가\n• 2배 이상: 이상 급등\n• 평균 미달: 관심 감소',
      tips: '평균거래량 대비 현재 거래량의 비율로 시장 관심도를 파악하세요.'
    },
    // 일목균형표 구성요소들
    'ICHIMOKU_CONVERSION': {
      koreanName: '일목균형표 전환선',
      description: '전환선은 9일간의 중간값으로, 단기 추세를 나타냅니다.',
      interpretation: '• 전환선 > 기준선: 단기 상승\n• 가격 > 전환선: 단기 강세',
      tips: '전환선과 기준선의 교차는 중요한 매매 신호입니다.'
    },
    'ICHIMOKU_BASE': {
      koreanName: '일목균형표 기준선',
      description: '기준선은 26일간의 중간값으로, 중기 추세를 나타냅니다.',
      interpretation: '• 기준선 상승: 중기 상승 추세\n• 주요 지지/저항선',
      tips: '기준선은 중요한 지지/저항선으로 작용합니다.'
    },
    'ICHIMOKU_SPAN_A': {
      koreanName: '일목균형표 선행스팬A',
      description: '선행스팬A는 전환선과 기준선의 중간값을 26일 앞에 표시한 선입니다.',
      interpretation: '• 구름대 상단/하단 형성\n• 미래 지지/저항 예측',
      tips: '선행스팬A와 B가 만드는 구름대의 두께가 중요합니다.'
    },
    'ICHIMOKU_SPAN_B': {
      koreanName: '일목균형표 선행스팬B',
      description: '선행스팬B는 52일간의 중간값을 26일 앞에 표시한 선입니다.',
      interpretation: '• 장기 추세 반영\n• 구름대 형성',
      tips: '선행스팬B는 장기 추세를 반영하여 강력한 지지/저항이 됩니다.'
    },
    'ICHIMOKU_LAGGING': {
      koreanName: '일목균형표 후행스팬',
      description: '후행스팬은 현재 종가를 26일 뒤에 표시한 선으로, 추세를 확인합니다.',
      interpretation: '• 가격 > 후행스팬: 상승 확인\n• 가격 < 후행스팬: 하락 확인',
      tips: '후행스팬은 추세를 최종 확인하는 지표입니다.'
    },
    // 스토캐스틱 변형
    'STOCH': {
      koreanName: '스토캐스틱',
      description: '스토캐스틱은 일정 기간의 가격 범위에서 현재 가격의 위치를 0-100으로 표시합니다.',
      interpretation: '• 80 이상: 과매수\n• 20 이하: 과매도\n• %K와 %D 교차: 매매 신호',
      tips: '횡보장에서 효과적이며, 추세장에서는 한쪽에 치우칠 수 있습니다.'
    },
    // 윌리엄스 변형
    'WilliamsR': {
      koreanName: '윌리엄스 %R',
      description: '윌리엄스 %R은 스토캐스틱과 유사하지만 음수로 표시되는 모멘텀 지표입니다.',
      interpretation: '• -20 이상: 과매수\n• -80 이하: 과매도',
      tips: '빠른 신호를 제공하지만 거짓 신호도 많으니 주의하세요.'
    },
    // 파라볼릭 변형
    'ParabolicSAR': {
      koreanName: '파라볼릭 SAR',
      description: '파라볼릭 SAR은 추세 전환점을 점으로 표시하는 추세 추종 지표입니다.',
      interpretation: '• 가격 위 SAR: 하락 추세\n• 가격 아래 SAR: 상승 추세',
      tips: '추세장에서 효과적이지만, 횡보장에서는 whipsaw가 발생합니다.'
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
    'PRICE': '설정된 가격 조건에 따라 매매 결정',
    'Ichimoku': '전환선 > 기준선 매수, 가격 > 구름대 강세',
    'ICHIMOKU': '전환선 > 기준선 매수, 가격 > 구름대 강세',
    'ATR': '변동성 기준 손절/익절 설정',
    'CCI': 'CCI < -100 매수, CCI > 100 매도',
    'Williams': '%R < -80 매수, %R > -20 매도',
    'ADX': 'ADX > 25 추세 강화, ADX < 20 추세 약화',
    'OBV': 'OBV 상승 + 가격 상승 = 상승 지속',
    'MFI': 'MFI < 20 매수, MFI > 80 매도'
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