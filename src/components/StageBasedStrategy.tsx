import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  IconButton,
  Chip,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Switch,
  FormControlLabel,
  Alert,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Badge,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material'
import {
  ExpandMore,
  Add,
  Delete,
  Warning,
  CheckCircle,
  Info,
  TrendingUp,
  TrendingDown,
  ShowChart,
  FilterAlt,
  Lock,
  LockOpen,
  Layers,
  ArrowDownward,
  ArrowUpward
} from '@mui/icons-material'

interface StageIndicator {
  id: string
  indicatorId: string
  name: string
  operator: string
  value: number | string
  params?: { [key: string]: any }
  combineWith: 'AND' | 'OR'
}

interface Stage {
  stage: number
  enabled: boolean
  indicators: StageIndicator[]
  passAllRequired: boolean // true: 모든 지표 통과 필요, false: 하나만 통과
}

interface StageStrategy {
  type: 'buy' | 'sell'
  stages: Stage[]
  usedIndicators: Set<string> // 이미 사용된 지표 추적
}

interface StageBasedStrategyProps {
  type: 'buy' | 'sell'
  availableIndicators: any[]
  onStrategyChange?: (strategy: StageStrategy) => void
}

const StageBasedStrategy: React.FC<StageBasedStrategyProps> = ({
  type,
  availableIndicators,
  onStrategyChange
}) => {
  const [strategy, setStrategy] = useState<StageStrategy>({
    type,
    stages: [
      { stage: 1, enabled: true, indicators: [], passAllRequired: true },
      { stage: 2, enabled: false, indicators: [], passAllRequired: true },
      { stage: 3, enabled: false, indicators: [], passAllRequired: true }
    ],
    usedIndicators: new Set()
  })

  const [dialogOpen, setDialogOpen] = useState(false)
  const [currentStage, setCurrentStage] = useState(1)
  const [tempIndicator, setTempIndicator] = useState<StageIndicator>({
    id: '',
    indicatorId: '',
    name: '',
    operator: type === 'buy' ? '<' : '>',
    value: 30,
    combineWith: 'AND'
  })

  useEffect(() => {
    if (onStrategyChange) {
      onStrategyChange(strategy)
    }
  }, [strategy])

  // 사용 가능한 지표 필터링 (이미 사용된 지표 제외)
  const getAvailableIndicatorsForStage = (stageNum: number) => {
    const usedInOtherStages = new Set<string>()
    
    strategy.stages.forEach((stage, index) => {
      if (index + 1 !== stageNum) {
        stage.indicators.forEach(ind => {
          usedInOtherStages.add(ind.indicatorId)
        })
      }
    })

    return availableIndicators.filter(ind => !usedInOtherStages.has(ind.id))
  }

  // 단계 활성화/비활성화
  const toggleStage = (stageNum: number) => {
    const newStages = [...strategy.stages]
    newStages[stageNum - 1].enabled = !newStages[stageNum - 1].enabled
    
    // 이전 단계가 비활성화되면 이후 단계도 자동 비활성화
    if (!newStages[stageNum - 1].enabled) {
      for (let i = stageNum; i < newStages.length; i++) {
        newStages[i].enabled = false
        newStages[i].indicators = []
      }
    }

    setStrategy({ ...strategy, stages: newStages })
  }

  // 지표 추가 다이얼로그 열기
  const openAddIndicatorDialog = (stageNum: number) => {
    setCurrentStage(stageNum)
    setTempIndicator({
      id: `ind_${Date.now()}`,
      indicatorId: '',
      name: '',
      operator: type === 'buy' ? '<' : '>',
      value: type === 'buy' ? 30 : 70,
      combineWith: strategy.stages[stageNum - 1].indicators.length > 0 ? 'AND' : 'AND'
    })
    setDialogOpen(true)
  }

  // 지표 저장
  const saveIndicator = () => {
    if (!tempIndicator.indicatorId) return

    const indicator = availableIndicators.find(i => i.id === tempIndicator.indicatorId)
    if (!indicator) return

    const newIndicator: StageIndicator = {
      ...tempIndicator,
      id: `ind_${Date.now()}`,
      name: indicator.name,
      params: indicator.defaultParams
    }

    const newStages = [...strategy.stages]
    const stageIndex = currentStage - 1
    
    // 최대 5개까지만 추가 가능
    if (newStages[stageIndex].indicators.length >= 5) {
      alert('각 단계당 최대 5개의 지표만 추가할 수 있습니다.')
      return
    }

    newStages[stageIndex].indicators.push(newIndicator)
    
    // 사용된 지표 업데이트
    const newUsedIndicators = new Set(strategy.usedIndicators)
    newUsedIndicators.add(tempIndicator.indicatorId)

    setStrategy({ 
      ...strategy, 
      stages: newStages,
      usedIndicators: newUsedIndicators
    })
    setDialogOpen(false)
  }

  // 지표 제거
  const removeIndicator = (stageNum: number, indicatorId: string) => {
    const newStages = [...strategy.stages]
    const stageIndex = stageNum - 1
    const indicator = newStages[stageIndex].indicators.find(i => i.id === indicatorId)
    
    newStages[stageIndex].indicators = newStages[stageIndex].indicators.filter(
      i => i.id !== indicatorId
    )

    // 사용된 지표에서 제거 (다른 단계에서 사용 중이 아닌 경우)
    const stillUsed = newStages.some(stage => 
      stage.indicators.some(i => i.indicatorId === indicator?.indicatorId)
    )
    
    const newUsedIndicators = new Set(strategy.usedIndicators)
    if (!stillUsed && indicator) {
      newUsedIndicators.delete(indicator.indicatorId)
    }

    setStrategy({ 
      ...strategy, 
      stages: newStages,
      usedIndicators: newUsedIndicators
    })
  }

  // 통과 조건 변경 (AND/OR)
  const togglePassAllRequired = (stageNum: number) => {
    const newStages = [...strategy.stages]
    newStages[stageNum - 1].passAllRequired = !newStages[stageNum - 1].passAllRequired
    setStrategy({ ...strategy, stages: newStages })
  }

  // 연산자 옵션
  const getOperatorOptions = () => {
    return [
      { value: '>', label: '초과 (>)' },
      { value: '<', label: '미만 (<)' },
      { value: '>=', label: '이상 (≥)' },
      { value: '<=', label: '이하 (≤)' },
      { value: '=', label: '같음 (=)' },
      { value: 'cross_above', label: '상향돌파' },
      { value: 'cross_below', label: '하향돌파' }
    ]
  }

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Layers />
          {type === 'buy' ? '매수' : '매도'} 조건 - 3단계 전략
        </Typography>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            각 단계별로 최대 5개의 지표를 설정할 수 있으며, 1단계를 통과해야 2단계가 평가됩니다.
            이미 사용된 지표는 다른 단계에서 선택할 수 없습니다.
          </Typography>
        </Alert>

        {/* 3개 단계 표시 */}
        {strategy.stages.map((stage, index) => {
          const stageNum = index + 1
          const canEnable = stageNum === 1 || strategy.stages[stageNum - 2].enabled
          const availableForStage = getAvailableIndicatorsForStage(stageNum)

          return (
            <Accordion 
              key={stageNum}
              expanded={stage.enabled}
              disabled={!canEnable}
              sx={{ mb: 2 }}
            >
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
                  <Badge 
                    badgeContent={stage.indicators.length} 
                    color={stage.indicators.length > 0 ? 'primary' : 'default'}
                  >
                    <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {stageNum === 1 && <FilterAlt color="primary" />}
                      {stageNum === 2 && <ShowChart color="warning" />}
                      {stageNum === 3 && <CheckCircle color="success" />}
                      {stageNum}단계
                    </Typography>
                  </Badge>
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={stage.enabled}
                        onChange={() => toggleStage(stageNum)}
                        disabled={!canEnable}
                        onClick={(e) => e.stopPropagation()}
                      />
                    }
                    label={stage.enabled ? '활성' : '비활성'}
                    onClick={(e) => e.stopPropagation()}
                  />

                  {stage.indicators.length > 0 && (
                    <Chip
                      label={stage.passAllRequired ? 'AND 조건' : 'OR 조건'}
                      size="small"
                      color={stage.passAllRequired ? 'primary' : 'secondary'}
                      variant="outlined"
                    />
                  )}

                  {!canEnable && (
                    <Tooltip title="이전 단계를 먼저 활성화하세요">
                      <Lock fontSize="small" color="disabled" />
                    </Tooltip>
                  )}
                </Box>
              </AccordionSummary>

              <AccordionDetails>
                {stage.enabled && (
                  <Box>
                    {/* 통과 조건 설정 */}
                    {stage.indicators.length > 1 && (
                      <FormControlLabel
                        control={
                          <Switch
                            checked={stage.passAllRequired}
                            onChange={() => togglePassAllRequired(stageNum)}
                          />
                        }
                        label={
                          <Typography variant="body2">
                            {stage.passAllRequired 
                              ? '모든 지표 조건을 만족해야 통과 (AND)' 
                              : '하나의 지표 조건만 만족하면 통과 (OR)'}
                          </Typography>
                        }
                        sx={{ mb: 2 }}
                      />
                    )}

                    {/* 지표 목록 */}
                    <List>
                      {stage.indicators.map((indicator, idx) => (
                        <ListItem key={indicator.id} divider>
                          <ListItemText
                            primary={
                              <Stack direction="row" spacing={1} alignItems="center">
                                {idx > 0 && (
                                  <Chip 
                                    label={indicator.combineWith} 
                                    size="small" 
                                    variant="outlined"
                                  />
                                )}
                                <Typography variant="subtitle2">
                                  {indicator.name}
                                </Typography>
                                <Chip
                                  label={`${indicator.operator} ${indicator.value}`}
                                  size="small"
                                  color={type === 'buy' ? 'success' : 'error'}
                                />
                              </Stack>
                            }
                            secondary={
                              indicator.params && (
                                <Typography variant="caption" color="textSecondary">
                                  파라미터: {JSON.stringify(indicator.params)}
                                </Typography>
                              )
                            }
                          />
                          <ListItemSecondaryAction>
                            <IconButton
                              edge="end"
                              onClick={() => removeIndicator(stageNum, indicator.id)}
                              size="small"
                            >
                              <Delete />
                            </IconButton>
                          </ListItemSecondaryAction>
                        </ListItem>
                      ))}
                    </List>

                    {/* 지표 추가 버튼 */}
                    <Box sx={{ mt: 2 }}>
                      <Button
                        variant="outlined"
                        startIcon={<Add />}
                        onClick={() => openAddIndicatorDialog(stageNum)}
                        disabled={stage.indicators.length >= 5 || availableForStage.length === 0}
                        fullWidth
                      >
                        {stage.indicators.length >= 5 
                          ? '최대 5개 지표 도달'
                          : availableForStage.length === 0
                          ? '사용 가능한 지표 없음'
                          : `지표 추가 (${5 - stage.indicators.length}개 가능)`}
                      </Button>
                    </Box>

                    {/* 사용 가능한 지표 안내 */}
                    {availableForStage.length > 0 && stage.indicators.length < 5 && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="caption" color="textSecondary">
                          사용 가능: {availableForStage.slice(0, 3).map(i => i.name).join(', ')}
                          {availableForStage.length > 3 && ` 외 ${availableForStage.length - 3}개`}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>
          )
        })}

        {/* 전략 요약 */}
        <Card sx={{ mt: 3, bgcolor: 'background.default' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              전략 요약
            </Typography>
            <Stack spacing={1}>
              {strategy.stages.filter(s => s.enabled && s.indicators.length > 0).map((stage, idx) => (
                <Box key={stage.stage} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2">
                    {stage.stage}단계:
                  </Typography>
                  <Stack direction="row" spacing={0.5}>
                    {stage.indicators.map(ind => (
                      <Chip 
                        key={ind.id}
                        label={`${ind.name} ${ind.operator} ${ind.value}`}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Stack>
                  {idx < strategy.stages.filter(s => s.enabled && s.indicators.length > 0).length - 1 && (
                    <ArrowDownward fontSize="small" color="action" />
                  )}
                </Box>
              ))}
              {strategy.stages.every(s => !s.enabled || s.indicators.length === 0) && (
                <Typography variant="body2" color="textSecondary">
                  조건이 설정되지 않았습니다
                </Typography>
              )}
            </Stack>
          </CardContent>
        </Card>
      </Paper>

      {/* 지표 추가 다이얼로그 */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {currentStage}단계 지표 추가
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {/* 조건 연결 */}
            {strategy.stages[currentStage - 1]?.indicators.length > 0 && (
              <Grid item xs={12}>
                <FormControl fullWidth size="small">
                  <InputLabel>조건 연결</InputLabel>
                  <Select
                    value={tempIndicator.combineWith}
                    onChange={(e) => setTempIndicator({ 
                      ...tempIndicator, 
                      combineWith: e.target.value as 'AND' | 'OR' 
                    })}
                    label="조건 연결"
                  >
                    <MenuItem value="AND">AND (그리고)</MenuItem>
                    <MenuItem value="OR">OR (또는)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            )}

            {/* 지표 선택 */}
            <Grid item xs={12}>
              <FormControl fullWidth size="small">
                <InputLabel>지표 선택</InputLabel>
                <Select
                  value={tempIndicator.indicatorId}
                  onChange={(e) => {
                    const indicator = availableIndicators.find(i => i.id === e.target.value)
                    setTempIndicator({ 
                      ...tempIndicator, 
                      indicatorId: e.target.value,
                      name: indicator?.name || ''
                    })
                  }}
                  label="지표 선택"
                >
                  {getAvailableIndicatorsForStage(currentStage).map(ind => (
                    <MenuItem key={ind.id} value={ind.id}>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Typography>{ind.name}</Typography>
                        <Chip label={ind.type} size="small" />
                      </Stack>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* 연산자 */}
            <Grid item xs={6}>
              <FormControl fullWidth size="small">
                <InputLabel>조건</InputLabel>
                <Select
                  value={tempIndicator.operator}
                  onChange={(e) => setTempIndicator({ 
                    ...tempIndicator, 
                    operator: e.target.value 
                  })}
                  label="조건"
                >
                  {getOperatorOptions().map(op => (
                    <MenuItem key={op.value} value={op.value}>
                      {op.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* 값 */}
            <Grid item xs={6}>
              <TextField
                fullWidth
                size="small"
                type="number"
                label="값"
                value={tempIndicator.value}
                onChange={(e) => setTempIndicator({ 
                  ...tempIndicator, 
                  value: parseFloat(e.target.value) 
                })}
              />
            </Grid>

            {/* 지표별 추가 파라미터 (필요시) */}
            {tempIndicator.indicatorId && (
              <Grid item xs={12}>
                <Alert severity="info">
                  <Typography variant="caption">
                    {tempIndicator.indicatorId === 'rsi' && 'RSI 30 미만은 과매도, 70 초과는 과매수'}
                    {tempIndicator.indicatorId === 'macd' && 'MACD와 시그널선 교차 확인'}
                    {tempIndicator.indicatorId === 'bb' && '볼린저밴드 상/하단 돌파 확인'}
                    {tempIndicator.indicatorId === 'sma' && '이동평균선 대비 위치 확인'}
                  </Typography>
                </Alert>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>취소</Button>
          <Button 
            onClick={saveIndicator} 
            variant="contained"
            disabled={!tempIndicator.indicatorId}
          >
            추가
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default StageBasedStrategy