import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Stack,
  Chip,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  Slider,
  Alert
} from '@mui/material'
import {
  Add,
  Delete,
  ExpandMore,
  PlayArrow,
  Save,
  Code,
  TrendingUp
} from '@mui/icons-material'

// 보조지표 타입
type IndicatorType = 'RSI' | 'MACD' | 'BB' | 'MA' | 'VOLUME' | 'STOCHASTIC' | 'CCI' | 'ADX'
type ComparisonOperator = '>' | '<' | '>=' | '<=' | '==' | 'CROSS_UP' | 'CROSS_DOWN'
type ActionType = 'BUY' | 'SELL' | 'HOLD'

interface TradingCondition {
  id: string
  indicator: IndicatorType
  parameter1: number
  parameter2?: number
  operator: ComparisonOperator
  value: number | string
  combineWith: 'AND' | 'OR'
}

interface TradingStrategy {
  name: string
  description: string
  buyConditions: TradingCondition[]
  sellConditions: TradingCondition[]
  stopLoss: number
  takeProfit: number
  trailingStop: boolean
  trailingStopPercent: number
  positionSize: number
  enabled: boolean
}

const StrategyBuilder: React.FC = () => {
  const [strategy, setStrategy] = useState<TradingStrategy>({
    name: '새 전략',
    description: '',
    buyConditions: [],
    sellConditions: [],
    stopLoss: 3,
    takeProfit: 5,
    trailingStop: false,
    trailingStopPercent: 2,
    positionSize: 10,
    enabled: true
  })

  const [showCode, setShowCode] = useState(false)

  const indicatorParams = {
    RSI: { name: 'RSI', params: ['기간'], default: [14] },
    MACD: { name: 'MACD', params: ['단기', '장기', '시그널'], default: [12, 26, 9] },
    BB: { name: '볼린저밴드', params: ['기간', '표준편차'], default: [20, 2] },
    MA: { name: '이동평균', params: ['기간'], default: [20] },
    VOLUME: { name: '거래량', params: [], default: [] },
    STOCHASTIC: { name: '스토캐스틱', params: ['%K', '%D'], default: [14, 3] },
    CCI: { name: 'CCI', params: ['기간'], default: [20] },
    ADX: { name: 'ADX', params: ['기간'], default: [14] }
  }

  const addCondition = (type: 'buy' | 'sell') => {
    const newCondition: TradingCondition = {
      id: Date.now().toString(),
      indicator: 'RSI',
      parameter1: 14,
      operator: '<',
      value: 30,
      combineWith: 'AND'
    }

    if (type === 'buy') {
      setStrategy(prev => ({
        ...prev,
        buyConditions: [...prev.buyConditions, newCondition]
      }))
    } else {
      setStrategy(prev => ({
        ...prev,
        sellConditions: [...prev.sellConditions, newCondition]
      }))
    }
  }

  const removeCondition = (type: 'buy' | 'sell', id: string) => {
    if (type === 'buy') {
      setStrategy(prev => ({
        ...prev,
        buyConditions: prev.buyConditions.filter(c => c.id !== id)
      }))
    } else {
      setStrategy(prev => ({
        ...prev,
        sellConditions: prev.sellConditions.filter(c => c.id !== id)
      }))
    }
  }

  const updateCondition = (type: 'buy' | 'sell', id: string, field: keyof TradingCondition, value: any) => {
    const updateFn = (conditions: TradingCondition[]) =>
      conditions.map(c => c.id === id ? { ...c, [field]: value } : c)

    if (type === 'buy') {
      setStrategy(prev => ({
        ...prev,
        buyConditions: updateFn(prev.buyConditions)
      }))
    } else {
      setStrategy(prev => ({
        ...prev,
        sellConditions: updateFn(prev.sellConditions)
      }))
    }
  }

  const generateCode = () => {
    const buyLogic = strategy.buyConditions.map((c, i) => {
      const combine = i > 0 ? (c.combineWith === 'AND' ? '&&' : '||') : ''
      return `${combine} ${c.indicator}(${c.parameter1}) ${c.operator} ${c.value}`
    }).join(' ')

    const sellLogic = strategy.sellConditions.map((c, i) => {
      const combine = i > 0 ? (c.combineWith === 'AND' ? '&&' : '||') : ''
      return `${combine} ${c.indicator}(${c.parameter1}) ${c.operator} ${c.value}`
    }).join(' ')

    return `
# ${strategy.name}
# ${strategy.description}

def should_buy():
    return ${buyLogic || 'False'}

def should_sell():
    return ${sellLogic || 'False'}

# Risk Management
STOP_LOSS = ${strategy.stopLoss}%
TAKE_PROFIT = ${strategy.takeProfit}%
POSITION_SIZE = ${strategy.positionSize}%
`
  }

  const ConditionRow = ({ 
    condition, 
    type, 
    index 
  }: { 
    condition: TradingCondition
    type: 'buy' | 'sell'
    index: number 
  }) => (
    <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
      <Grid container spacing={2} alignItems="center">
        {index > 0 && (
          <Grid item xs={1}>
            <Select
              size="small"
              value={condition.combineWith}
              onChange={(e) => updateCondition(type, condition.id, 'combineWith', e.target.value)}
              fullWidth
            >
              <MenuItem value="AND">AND</MenuItem>
              <MenuItem value="OR">OR</MenuItem>
            </Select>
          </Grid>
        )}
        
        <Grid item xs={index > 0 ? 2 : 3}>
          <FormControl size="small" fullWidth>
            <InputLabel>지표</InputLabel>
            <Select
              value={condition.indicator}
              onChange={(e) => updateCondition(type, condition.id, 'indicator', e.target.value)}
              label="지표"
            >
              {Object.entries(indicatorParams).map(([key, value]) => (
                <MenuItem key={key} value={key}>{value.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={2}>
          <TextField
            size="small"
            label="파라미터"
            type="number"
            value={condition.parameter1}
            onChange={(e) => updateCondition(type, condition.id, 'parameter1', Number(e.target.value))}
            fullWidth
          />
        </Grid>

        <Grid item xs={2}>
          <FormControl size="small" fullWidth>
            <InputLabel>조건</InputLabel>
            <Select
              value={condition.operator}
              onChange={(e) => updateCondition(type, condition.id, 'operator', e.target.value)}
              label="조건"
            >
              <MenuItem value=">">{'>'}</MenuItem>
              <MenuItem value="<">{'<'}</MenuItem>
              <MenuItem value=">=">{'>='}</MenuItem>
              <MenuItem value="<=">{'<='}</MenuItem>
              <MenuItem value="==">{'='}</MenuItem>
              <MenuItem value="CROSS_UP">상향돌파</MenuItem>
              <MenuItem value="CROSS_DOWN">하향돌파</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={2}>
          <TextField
            size="small"
            label="값"
            value={condition.value}
            onChange={(e) => updateCondition(type, condition.id, 'value', e.target.value)}
            fullWidth
          />
        </Grid>

        <Grid item xs={1}>
          <IconButton 
            color="error" 
            onClick={() => removeCondition(type, condition.id)}
            size="small"
          >
            <Delete />
          </IconButton>
        </Grid>
      </Grid>
    </Paper>
  )

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h5">
          <Code sx={{ mr: 1, verticalAlign: 'middle' }} />
          전략 빌더
        </Typography>
        
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            onClick={() => setShowCode(!showCode)}
          >
            {showCode ? '빌더 보기' : '코드 보기'}
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
          >
            저장
          </Button>
          <Button
            variant="contained"
            color="success"
            startIcon={<PlayArrow />}
          >
            백테스트
          </Button>
        </Stack>
      </Stack>

      {showCode ? (
        <Paper sx={{ p: 3, bgcolor: 'grey.900', color: 'grey.100' }}>
          <pre style={{ margin: 0, fontFamily: 'monospace' }}>
            {generateCode()}
          </pre>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {/* 기본 정보 */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>기본 정보</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    label="전략 이름"
                    value={strategy.name}
                    onChange={(e) => setStrategy(prev => ({ ...prev, name: e.target.value }))}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="설명"
                    value={strategy.description}
                    onChange={(e) => setStrategy(prev => ({ ...prev, description: e.target.value }))}
                    fullWidth
                  />
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* 매수 조건 */}
          <Grid item xs={12} lg={6}>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">
                  매수 조건 
                  <Chip 
                    label={strategy.buyConditions.length} 
                    size="small" 
                    color="error" 
                    sx={{ ml: 1 }}
                  />
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {strategy.buyConditions.map((condition, index) => (
                  <ConditionRow 
                    key={condition.id} 
                    condition={condition} 
                    type="buy"
                    index={index}
                  />
                ))}
                
                <Button
                  startIcon={<Add />}
                  onClick={() => addCondition('buy')}
                  variant="outlined"
                  fullWidth
                  sx={{ mt: 2 }}
                >
                  매수 조건 추가
                </Button>
              </AccordionDetails>
            </Accordion>
          </Grid>

          {/* 매도 조건 */}
          <Grid item xs={12} lg={6}>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">
                  매도 조건
                  <Chip 
                    label={strategy.sellConditions.length} 
                    size="small" 
                    color="primary" 
                    sx={{ ml: 1 }}
                  />
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {strategy.sellConditions.map((condition, index) => (
                  <ConditionRow 
                    key={condition.id} 
                    condition={condition} 
                    type="sell"
                    index={index}
                  />
                ))}
                
                <Button
                  startIcon={<Add />}
                  onClick={() => addCondition('sell')}
                  variant="outlined"
                  fullWidth
                  sx={{ mt: 2 }}
                >
                  매도 조건 추가
                </Button>
              </AccordionDetails>
            </Accordion>
          </Grid>

          {/* 리스크 관리 */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>리스크 관리</Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <Typography gutterBottom>손절 (%)</Typography>
                  <Slider
                    value={strategy.stopLoss}
                    onChange={(e, v) => setStrategy(prev => ({ ...prev, stopLoss: v as number }))}
                    min={0}
                    max={10}
                    step={0.5}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Grid>

                <Grid item xs={12} md={3}>
                  <Typography gutterBottom>익절 (%)</Typography>
                  <Slider
                    value={strategy.takeProfit}
                    onChange={(e, v) => setStrategy(prev => ({ ...prev, takeProfit: v as number }))}
                    min={0}
                    max={20}
                    step={0.5}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Grid>

                <Grid item xs={12} md={3}>
                  <Typography gutterBottom>포지션 크기 (%)</Typography>
                  <Slider
                    value={strategy.positionSize}
                    onChange={(e, v) => setStrategy(prev => ({ ...prev, positionSize: v as number }))}
                    min={1}
                    max={100}
                    step={1}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Grid>

                <Grid item xs={12} md={3}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={strategy.trailingStop}
                        onChange={(e) => setStrategy(prev => ({ ...prev, trailingStop: e.target.checked }))}
                      />
                    }
                    label="트레일링 스탑"
                  />
                  {strategy.trailingStop && (
                    <TextField
                      size="small"
                      label="트레일링 %"
                      type="number"
                      value={strategy.trailingStopPercent}
                      onChange={(e) => setStrategy(prev => ({ ...prev, trailingStopPercent: Number(e.target.value) }))}
                      fullWidth
                    />
                  )}
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* 예시 전략 */}
          <Grid item xs={12}>
            <Alert severity="info" icon={<TrendingUp />}>
              <Typography variant="subtitle2" gutterBottom>
                <strong>인기 전략 템플릿</strong>
              </Typography>
              <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                <Chip label="RSI 과매도 전략" onClick={() => {}} />
                <Chip label="골든크로스 전략" onClick={() => {}} />
                <Chip label="볼린저밴드 돌파" onClick={() => {}} />
                <Chip label="MACD 다이버전스" onClick={() => {}} />
                <Chip label="거래량 돌파" onClick={() => {}} />
              </Stack>
            </Alert>
          </Grid>
        </Grid>
      )}
    </Box>
  )
}

export default StrategyBuilder