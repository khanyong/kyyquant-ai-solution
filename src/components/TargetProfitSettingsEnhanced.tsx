import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  FormControlLabel,
  Switch,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Chip,
  Tooltip,
  Alert,
  Divider,
  ToggleButton,
  ToggleButtonGroup,
  Slider,
  Collapse,
  IconButton
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  Info,
  ExpandMore,
  ExpandLess,
  ShowChart,
  Timeline,
  Speed,
  Shield,
  Lock,
  LockOpen,
  Security,
  AccountBalance
} from '@mui/icons-material'

interface StageTarget {
  stage: number
  targetProfit: number
  exitRatio: number
  dynamicStopLoss?: boolean
  combineWith?: 'AND' | 'OR'  // 각 단계별 지표 조건 결합 방식
}

interface TargetProfitSettingsEnhancedProps {
  targetProfit?: {
    mode: 'simple' | 'staged'
    simple?: {
      enabled: boolean
      value: number
      combineWith: 'AND' | 'OR'
    }
    staged?: {
      enabled: boolean
      stages: StageTarget[]
      combineWith: 'AND' | 'OR'
    }
  }
  stopLoss?: {
    enabled: boolean
    value: number
    breakEven?: boolean
    trailingStop?: {
      enabled: boolean
      activation: number
      distance: number
    }
  }
  onChange: (settings: any) => void
  hasIndicatorConditions?: boolean
  isStageBasedStrategy?: boolean
}

const TargetProfitSettingsEnhanced: React.FC<TargetProfitSettingsEnhancedProps> = ({
  targetProfit = {
    mode: 'simple',
    simple: { enabled: false, value: 5.0, combineWith: 'OR' },
    staged: {
      enabled: false,
      stages: [
        { stage: 1, targetProfit: 3, exitRatio: 50, dynamicStopLoss: false, combineWith: 'OR' },
        { stage: 2, targetProfit: 5, exitRatio: 30, dynamicStopLoss: false, combineWith: 'OR' },
        { stage: 3, targetProfit: 10, exitRatio: 20, dynamicStopLoss: true, combineWith: 'AND' }
      ],
      combineWith: 'OR'  // 기본값 (하위 호환성)
    }
  },
  stopLoss = {
    enabled: false,
    value: 3.0,
    breakEven: false,
    trailingStop: {
      enabled: false,
      activation: 5,
      distance: 2
    }
  },
  onChange,
  hasIndicatorConditions = false,
  isStageBasedStrategy = false
}) => {
  const [mode, setMode] = useState<'simple' | 'staged'>(targetProfit.mode || 'simple')
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleModeChange = (event: React.MouseEvent<HTMLElement>, newMode: 'simple' | 'staged' | null) => {
    if (newMode !== null) {
      setMode(newMode)
      onChange({
        targetProfit: {
          ...targetProfit,
          mode: newMode
        },
        stopLoss
      })
    }
  }

  const handleSimpleTargetChange = (field: string, value: any) => {
    onChange({
      targetProfit: {
        ...targetProfit,
        mode: 'simple',
        simple: { ...targetProfit.simple, [field]: value }
      },
      stopLoss
    })
  }

  const handleStageTargetChange = (stageIndex: number, field: string, value: any) => {
    const updatedStages = [...(targetProfit.staged?.stages || [])]
    updatedStages[stageIndex] = {
      ...updatedStages[stageIndex],
      [field]: value
    }

    onChange({
      targetProfit: {
        ...targetProfit,
        mode: 'staged',
        staged: {
          ...targetProfit.staged,
          stages: updatedStages
        }
      },
      stopLoss
    })
  }

  const handleStagedSettingChange = (field: string, value: any) => {
    onChange({
      targetProfit: {
        ...targetProfit,
        mode: 'staged',
        staged: {
          ...targetProfit.staged,
          [field]: value
        }
      },
      stopLoss
    })
  }

  const handleStopLossChange = (field: string, value: any) => {
    onChange({
      targetProfit,
      stopLoss: { ...stopLoss, [field]: value }
    })
  }

  const handleTrailingStopChange = (field: string, value: any) => {
    onChange({
      targetProfit,
      stopLoss: {
        ...stopLoss,
        trailingStop: {
          ...stopLoss.trailingStop,
          [field]: value
        }
      }
    })
  }

  const calculateRemainingRatio = () => {
    if (!targetProfit.staged) return 100
    const totalExit = targetProfit.staged.stages.reduce((sum, stage) => sum + stage.exitRatio, 0)
    return Math.max(0, 100 - totalExit)
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <TrendingUp sx={{ mr: 1 }} />
        목표 수익률 설정
      </Typography>

      {/* 모드 선택 */}
      {isStageBasedStrategy && (
        <Box sx={{ mb: 3 }}>
          <ToggleButtonGroup
            value={mode}
            exclusive
            onChange={handleModeChange}
            fullWidth
            size="small"
          >
            <ToggleButton value="simple">
              <ShowChart sx={{ mr: 1 }} />
              단일 목표
            </ToggleButton>
            <ToggleButton value="staged">
              <Timeline sx={{ mr: 1 }} />
              단계별 목표
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>
      )}

      <Alert severity="info" sx={{ mb: 2 }}>
        {mode === 'simple'
          ? '모든 포지션에 대해 동일한 목표 수익률을 적용합니다.'
          : '각 단계별로 다른 목표 수익률과 매도 비율을 설정할 수 있습니다.'}
      </Alert>

      <Grid container spacing={3}>
        {/* 단일 목표 모드 */}
        {mode === 'simple' && (
          <Grid item xs={12}>
            <Box sx={{ mb: 3 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={targetProfit.simple?.enabled || false}
                    onChange={(e) => handleSimpleTargetChange('enabled', e.target.checked)}
                    color="success"
                  />
                }
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography>목표 수익률 사용</Typography>
                    <Tooltip title="보유 중인 포지션이 설정한 수익률에 도달하면 매도 신호를 생성합니다">
                      <Info sx={{ ml: 1, fontSize: 18, color: 'text.secondary' }} />
                    </Tooltip>
                  </Box>
                }
              />

              {targetProfit.simple?.enabled && (
                <Box sx={{ mt: 2, ml: 4 }}>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} sm={4}>
                      <TextField
                        label="목표 수익률 (%)"
                        type="number"
                        value={targetProfit.simple?.value || 5}
                        onChange={(e) => handleSimpleTargetChange('value', parseFloat(e.target.value) || 0)}
                        fullWidth
                        size="small"
                        inputProps={{ min: 0.1, max: 100, step: 0.5 }}
                      />
                    </Grid>

                    {hasIndicatorConditions && (
                      <Grid item xs={12} sm={4}>
                        <FormControl fullWidth size="small">
                          <InputLabel>지표 조건과 결합</InputLabel>
                          <Select
                            value={targetProfit.simple?.combineWith || 'OR'}
                            onChange={(e) => handleSimpleTargetChange('combineWith', e.target.value)}
                            label="지표 조건과 결합"
                          >
                            <MenuItem value="OR">
                              <Chip label="OR" size="small" color="primary" sx={{ mr: 1 }} />
                              둘 중 하나만 충족
                            </MenuItem>
                            <MenuItem value="AND">
                              <Chip label="AND" size="small" color="secondary" sx={{ mr: 1 }} />
                              모두 충족
                            </MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                    )}
                  </Grid>
                </Box>
              )}
            </Box>
          </Grid>
        )}

        {/* 단계별 목표 모드 */}
        {mode === 'staged' && (
          <Grid item xs={12}>
            <Box sx={{ mb: 3 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={targetProfit.staged?.enabled || false}
                    onChange={(e) => handleStagedSettingChange('enabled', e.target.checked)}
                    color="success"
                  />
                }
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography>단계별 목표 수익률 사용</Typography>
                    <Tooltip title="각 단계별로 다른 목표와 매도 비율을 설정합니다">
                      <Info sx={{ ml: 1, fontSize: 18, color: 'text.secondary' }} />
                    </Tooltip>
                  </Box>
                }
              />

              {targetProfit.staged?.enabled && (
                <Box sx={{ mt: 3 }}>
                  {targetProfit.staged?.stages.map((stage, index) => (
                    <Paper key={index} sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle2" color="primary" sx={{ mr: 1 }}>
                          {stage.stage}단계
                        </Typography>
                        {stage.dynamicStopLoss && (
                          <Chip
                            icon={<Shield sx={{ fontSize: 16 }} />}
                            label={
                              index === 0 ? '본전 보호' :
                              index === 1 ? '수익 보호' :
                              '수익 확정'
                            }
                            size="small"
                            color="info"
                            variant="outlined"
                          />
                        )}
                      </Box>
                      {/* 첫 번째 줄: 기본 설정 */}
                      <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} sm={3}>
                          <TextField
                            label="목표 수익률 (%)"
                            type="number"
                            value={stage.targetProfit}
                            onChange={(e) => handleStageTargetChange(index, 'targetProfit', parseFloat(e.target.value) || 0)}
                            fullWidth
                            size="small"
                            inputProps={{ min: 0.1, max: 100, step: 0.5 }}
                          />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              매도 비율: {stage.exitRatio}%
                            </Typography>
                            <Slider
                              value={stage.exitRatio}
                              onChange={(e, value) => handleStageTargetChange(index, 'exitRatio', value as number)}
                              min={10}
                              max={100}
                              step={10}
                              marks
                              valueLabelDisplay="auto"
                            />
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={3}>
                          <FormControlLabel
                            control={
                              <Switch
                                checked={stage.dynamicStopLoss || false}
                                onChange={(e) => handleStageTargetChange(index, 'dynamicStopLoss', e.target.checked)}
                                size="small"
                              />
                            }
                            label={
                              <Tooltip title={`${stage.stage}단계 목표 달성 시 손절선을 매도가(${stage.targetProfit}%)로 상향 조정합니다`}>
                                <span style={{ fontSize: '0.875rem' }}>
                                  {index === 0 ? '손절→본전' :
                                   index === 1 ? '손절→1단계가' :
                                   '손절→2단계가'}
                                </span>
                              </Tooltip>
                            }
                          />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                          <Chip
                            icon={<TrendingUp sx={{ fontSize: 16 }} />}
                            label={`${stage.targetProfit}% → ${stage.exitRatio}% 매도`}
                            size="small"
                            color="success"
                            variant="outlined"
                          />
                        </Grid>
                      </Grid>

                      {/* 두 번째 줄: 지표 결합 방식 (지표 조건이 있을 때만) */}
                      {hasIndicatorConditions && (
                        <Grid container spacing={2} alignItems="center" sx={{ mt: 1 }}>
                          <Grid item xs={12}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Typography variant="body2" color="text.secondary">
                                지표 조건과 결합:
                              </Typography>
                              <ToggleButtonGroup
                                value={stage.combineWith || 'OR'}
                                exclusive
                                onChange={(e, newValue) => {
                                  if (newValue !== null) {
                                    handleStageTargetChange(index, 'combineWith', newValue)
                                  }
                                }}
                                size="small"
                              >
                                <ToggleButton value="OR" sx={{ px: 2 }}>
                                  <Chip label="OR" size="small" color="primary" sx={{ mr: 1 }} />
                                  목표 또는 지표
                                </ToggleButton>
                                <ToggleButton value="AND" sx={{ px: 2 }}>
                                  <Chip label="AND" size="small" color="secondary" sx={{ mr: 1 }} />
                                  목표 그리고 지표
                                </ToggleButton>
                              </ToggleButtonGroup>
                              <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>
                                {stage.combineWith === 'AND'
                                  ? `(${stage.targetProfit}% 도달 그리고 지표 조건 충족 시 매도)`
                                  : `(${stage.targetProfit}% 도달 또는 지표 조건 충족 시 매도)`}
                              </Typography>
                            </Box>
                          </Grid>
                        </Grid>
                      )}

                      {/* 동적 손절 표시 */}
                      {stage.dynamicStopLoss && (
                        <Box sx={{ mt: 1 }}>
                          <Chip
                            icon={<Lock sx={{ fontSize: 16 }} />}
                            label={
                              index === 0 ? `손절 ${stopLoss.value}% → 0% (본전)` :
                              index === 1 ? `손절 → +${targetProfit.staged?.stages[0]?.targetProfit || 3}%` :
                              `손절 → +${targetProfit.staged?.stages[1]?.targetProfit || 5}%`
                            }
                            size="small"
                            color="warning"
                            variant="outlined"
                            sx={{ fontSize: '0.75rem' }}
                          />
                        </Box>
                      )}
                    </Paper>
                  ))}

                  {/* 남은 포지션 및 수익 보호 시각화 */}
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <AccountBalance sx={{ mr: 1, color: 'info.main' }} />
                          <Typography variant="body2" color="text.secondary">
                            포지션 분배
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', height: 30, borderRadius: 1, overflow: 'hidden', bgcolor: 'grey.200' }}>
                          {targetProfit.staged?.stages.map((stage, idx) => (
                            <Box
                              key={idx}
                              sx={{
                                width: `${stage.exitRatio}%`,
                                bgcolor: idx === 0 ? 'success.light' : idx === 1 ? 'warning.light' : 'error.light',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRight: '1px solid white'
                              }}
                            >
                              <Typography variant="caption" sx={{ color: 'white', fontWeight: 'bold' }}>
                                {stage.exitRatio}%
                              </Typography>
                            </Box>
                          ))}
                          {calculateRemainingRatio() > 0 && (
                            <Box
                              sx={{
                                width: `${calculateRemainingRatio()}%`,
                                bgcolor: 'grey.400',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                              }}
                            >
                              <Typography variant="caption" sx={{ color: 'white' }}>
                                {calculateRemainingRatio()}%
                              </Typography>
                            </Box>
                          )}
                        </Box>
                      </Grid>

                      <Grid item xs={12} sm={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Shield sx={{ mr: 1, color: 'warning.main' }} />
                          <Typography variant="body2" color="text.secondary">
                            수익 보호 단계
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                          {targetProfit.staged?.stages.filter(s => s.dynamicStopLoss).map((stage, idx) => (
                            <Box key={idx} sx={{ display: 'flex', alignItems: 'center' }}>
                              <Lock sx={{ fontSize: 14, mr: 0.5, color: 'warning.main' }} />
                              <Typography variant="caption">
                                {stage.stage}단계: 손절 → +{
                                  stage.stage === 1 ? '0' :
                                  stage.stage === 2 ? targetProfit.staged?.stages[0]?.targetProfit :
                                  targetProfit.staged?.stages[1]?.targetProfit
                                }% 보장
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      </Grid>
                    </Grid>
                  </Box>

                  {/* 지표 조건과 결합 */}
                  {hasIndicatorConditions && (
                    <Grid item xs={12} sm={6} sx={{ mt: 2 }}>
                      <FormControl fullWidth size="small">
                        <InputLabel>지표 조건과 결합</InputLabel>
                        <Select
                          value={targetProfit.staged?.combineWith || 'OR'}
                          onChange={(e) => handleStagedSettingChange('combineWith', e.target.value)}
                          label="지표 조건과 결합"
                        >
                          <MenuItem value="OR">
                            <Chip label="OR" size="small" color="primary" sx={{ mr: 1 }} />
                            목표 수익 또는 지표 조건
                          </MenuItem>
                          <MenuItem value="AND">
                            <Chip label="AND" size="small" color="secondary" sx={{ mr: 1 }} />
                            목표 수익 그리고 지표 조건
                          </MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  )}
                </Box>
              )}
            </Box>
          </Grid>
        )}

        <Grid item xs={12}>
          <Divider />
        </Grid>

        {/* 손절 설정 */}
        <Grid item xs={12}>
          <Box>
            <FormControlLabel
              control={
                <Switch
                  checked={stopLoss.enabled}
                  onChange={(e) => handleStopLossChange('enabled', e.target.checked)}
                  color="error"
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TrendingDown sx={{ mr: 1, color: 'error.main' }} />
                  <Typography>손절 라인 사용</Typography>
                  <Tooltip title="손실이 설정한 비율에 도달하면 즉시 매도합니다">
                    <Info sx={{ ml: 1, fontSize: 18, color: 'text.secondary' }} />
                  </Tooltip>
                </Box>
              }
            />

            {stopLoss.enabled && (
              <Box sx={{ mt: 2, ml: 4 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} sm={3}>
                    <TextField
                      label="손절 라인 (%)"
                      type="number"
                      value={stopLoss.value}
                      onChange={(e) => handleStopLossChange('value', Math.abs(parseFloat(e.target.value)) || 0)}
                      fullWidth
                      size="small"
                      inputProps={{ min: 0.1, max: 50, step: 0.5 }}
                    />
                  </Grid>

                  {mode === 'staged' && (
                    <Grid item xs={12} sm={3}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={stopLoss.breakEven || false}
                            onChange={(e) => handleStopLossChange('breakEven', e.target.checked)}
                            size="small"
                            color="info"
                          />
                        }
                        label="동적 손절"
                      />
                      {stopLoss.breakEven && (
                        <Typography variant="caption" color="text.secondary">
                          목표 달성 시 손절 상향
                        </Typography>
                      )}
                    </Grid>
                  )}

                  {/* 고급 설정 토글 */}
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        고급 설정
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={() => setShowAdvanced(!showAdvanced)}
                      >
                        {showAdvanced ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    </Box>
                  </Grid>
                </Grid>

                {/* 트레일링 스톱 (고급) */}
                <Collapse in={showAdvanced}>
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={stopLoss.trailingStop?.enabled || false}
                          onChange={(e) => handleTrailingStopChange('enabled', e.target.checked)}
                          size="small"
                          color="warning"
                        />
                      }
                      label={
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Speed sx={{ mr: 1, fontSize: 20 }} />
                          <Typography variant="body2">트레일링 스톱</Typography>
                        </Box>
                      }
                    />

                    {stopLoss.trailingStop?.enabled && (
                      <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            label="활성화 수익률 (%)"
                            type="number"
                            value={stopLoss.trailingStop?.activation || 5}
                            onChange={(e) => handleTrailingStopChange('activation', parseFloat(e.target.value) || 0)}
                            fullWidth
                            size="small"
                            helperText="이 수익률 도달 시 활성화"
                            inputProps={{ min: 1, max: 50, step: 0.5 }}
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            label="추적 거리 (%)"
                            type="number"
                            value={stopLoss.trailingStop?.distance || 2}
                            onChange={(e) => handleTrailingStopChange('distance', parseFloat(e.target.value) || 0)}
                            fullWidth
                            size="small"
                            helperText="최고점 대비 하락률"
                            inputProps={{ min: 0.5, max: 10, step: 0.5 }}
                          />
                        </Grid>
                      </Grid>
                    )}
                  </Box>
                </Collapse>
              </Box>
            )}
          </Box>
        </Grid>
      </Grid>

      {/* 설정 요약 */}
      {((mode === 'simple' && targetProfit.simple?.enabled) ||
        (mode === 'staged' && targetProfit.staged?.enabled) ||
        stopLoss.enabled) && (
        <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            매도 조건 요약:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {hasIndicatorConditions && (
              <Chip
                label="지표 조건"
                size="small"
                variant="outlined"
              />
            )}

            {mode === 'simple' && targetProfit.simple?.enabled && (
              <>
                {hasIndicatorConditions && (
                  <Chip
                    label={targetProfit.simple.combineWith}
                    size="small"
                    color={targetProfit.simple.combineWith === 'OR' ? 'primary' : 'secondary'}
                  />
                )}
                <Chip
                  label={`목표 수익 ${targetProfit.simple.value}%`}
                  size="small"
                  color="success"
                  icon={<TrendingUp />}
                />
              </>
            )}

            {mode === 'staged' && targetProfit.staged?.enabled && (
              <>
                {hasIndicatorConditions && (
                  <Chip
                    label={targetProfit.staged.combineWith}
                    size="small"
                    color={targetProfit.staged.combineWith === 'OR' ? 'primary' : 'secondary'}
                  />
                )}
                {targetProfit.staged.stages.map((stage, idx) => (
                  <Chip
                    key={idx}
                    label={`${stage.stage}단계: ${stage.targetProfit}% → ${stage.exitRatio}% 매도`}
                    size="small"
                    color="success"
                    variant="outlined"
                  />
                ))}
              </>
            )}

            {stopLoss.enabled && (
              <>
                {((mode === 'simple' && targetProfit.simple?.enabled) ||
                  (mode === 'staged' && targetProfit.staged?.enabled) ||
                  hasIndicatorConditions) && (
                  <Chip label="OR" size="small" color="primary" />
                )}
                <Chip
                  label={`손절 -${stopLoss.value}%`}
                  size="small"
                  color="error"
                  icon={<TrendingDown />}
                />
                {stopLoss.breakEven && (
                  <Chip
                    label="동적 손절"
                    size="small"
                    color="info"
                    variant="outlined"
                  />
                )}
                {stopLoss.trailingStop?.enabled && (
                  <Chip
                    label={`트레일링 ${stopLoss.trailingStop.distance}%`}
                    size="small"
                    color="warning"
                    variant="outlined"
                  />
                )}
              </>
            )}
          </Box>
        </Box>
      )}
    </Paper>
  )
}

export default TargetProfitSettingsEnhanced