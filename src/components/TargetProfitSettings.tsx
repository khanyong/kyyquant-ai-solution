import React from 'react'
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
  Divider
} from '@mui/material'
import { TrendingUp, TrendingDown, Info } from '@mui/icons-material'

interface TargetProfitSettingsProps {
  targetProfit?: {
    enabled: boolean
    value: number
    combineWith: 'AND' | 'OR'
  }
  stopLoss?: {
    enabled: boolean
    value: number
  }
  onChange: (settings: {
    targetProfit?: {
      enabled: boolean
      value: number
      combineWith: 'AND' | 'OR'
    }
    stopLoss?: {
      enabled: boolean
      value: number
    }
  }) => void
  hasIndicatorConditions?: boolean
}

const TargetProfitSettings: React.FC<TargetProfitSettingsProps> = ({
  targetProfit = { enabled: false, value: 5.0, combineWith: 'OR' },
  stopLoss = { enabled: false, value: 3.0 },
  onChange,
  hasIndicatorConditions = false
}) => {
  const handleTargetProfitChange = (field: string, value: any) => {
    onChange({
      targetProfit: { ...targetProfit, [field]: value },
      stopLoss
    })
  }

  const handleStopLossChange = (field: string, value: any) => {
    onChange({
      targetProfit,
      stopLoss: { ...stopLoss, [field]: value }
    })
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <TrendingUp sx={{ mr: 1 }} />
        목표 수익률 설정
      </Typography>

      <Alert severity="info" sx={{ mb: 2 }}>
        지표 조건과 별도로 목표 수익률 도달 시 자동 매도를 설정할 수 있습니다.
      </Alert>

      <Grid container spacing={3}>
        {/* 목표 수익률 */}
        <Grid item xs={12}>
          <Box sx={{ mb: 3 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={targetProfit.enabled}
                  onChange={(e) => handleTargetProfitChange('enabled', e.target.checked)}
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

            {targetProfit.enabled && (
              <Box sx={{ mt: 2, ml: 4 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="목표 수익률 (%)"
                      type="number"
                      value={targetProfit.value}
                      onChange={(e) => handleTargetProfitChange('value', parseFloat(e.target.value) || 0)}
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
                          value={targetProfit.combineWith}
                          onChange={(e) => handleTargetProfitChange('combineWith', e.target.value)}
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

                  <Grid item xs={12} sm={4}>
                    <Box sx={{ p: 1, bgcolor: 'success.light', borderRadius: 1 }}>
                      <Typography variant="body2" color="success.dark">
                        {targetProfit.value}% 수익 달성 시
                        {hasIndicatorConditions && targetProfit.combineWith === 'OR' && ' (또는 지표 조건)'}
                        {hasIndicatorConditions && targetProfit.combineWith === 'AND' && ' (그리고 지표 조건)'}
                        {' 매도'}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            )}
          </Box>
        </Grid>

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
                  <Tooltip title="손실이 설정한 비율에 도달하면 즉시 매도합니다 (지표 조건 무시)">
                    <Info sx={{ ml: 1, fontSize: 18, color: 'text.secondary' }} />
                  </Tooltip>
                </Box>
              }
            />

            {stopLoss.enabled && (
              <Box sx={{ mt: 2, ml: 4 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} sm={4}>
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

                  <Grid item xs={12} sm={8}>
                    <Box sx={{ p: 1, bgcolor: 'error.light', borderRadius: 1 }}>
                      <Typography variant="body2" color="error.dark">
                        -{stopLoss.value}% 손실 시 즉시 매도 (지표 조건 무관)
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            )}
          </Box>
        </Grid>
      </Grid>

      {/* 설정 요약 */}
      {(targetProfit.enabled || stopLoss.enabled) && (
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
            {targetProfit.enabled && (
              <>
                {hasIndicatorConditions && (
                  <Chip
                    label={targetProfit.combineWith}
                    size="small"
                    color={targetProfit.combineWith === 'OR' ? 'primary' : 'secondary'}
                  />
                )}
                <Chip
                  label={`목표 수익 ${targetProfit.value}%`}
                  size="small"
                  color="success"
                  icon={<TrendingUp />}
                />
              </>
            )}
            {stopLoss.enabled && (
              <>
                {(hasIndicatorConditions || targetProfit.enabled) && (
                  <Chip label="OR" size="small" color="primary" />
                )}
                <Chip
                  label={`손절 -${stopLoss.value}%`}
                  size="small"
                  color="error"
                  icon={<TrendingDown />}
                />
              </>
            )}
          </Box>
        </Box>
      )}
    </Paper>
  )
}

export default TargetProfitSettings