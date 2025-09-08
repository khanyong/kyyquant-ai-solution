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
  initialStrategy?: any  // 초기 전략 설정을 받기 위한 prop
}

const StageBasedStrategy: React.FC<StageBasedStrategyProps> = ({
  type,
  availableIndicators,
  onStrategyChange,
  initialStrategy
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

  // initialStrategy가 제공될 때 state 업데이트
  useEffect(() => {
    if (initialStrategy) {
      // stage1, stage2, stage3 형식을 stages 배열로 변환
      if (initialStrategy.stage1 || initialStrategy.stage2 || initialStrategy.stage3) {
        const newStages: Stage[] = []
        
        if (initialStrategy.stage1) {
          const indicators = initialStrategy.stage1.conditions?.map((cond: any, idx: number) => ({
            id: `s1-${idx}`,
            indicatorId: cond.indicator,
            name: cond.indicator,
            operator: cond.operator,
            value: cond.value,
            combineWith: 'AND'
          })) || []
          
          newStages.push({
            stage: 1,
            enabled: true,
            indicators,
            passAllRequired: true
          })
        } else {
          newStages.push({ stage: 1, enabled: false, indicators: [], passAllRequired: true })
        }
        
        if (initialStrategy.stage2) {
          const indicators = initialStrategy.stage2.conditions?.map((cond: any, idx: number) => ({
            id: `s2-${idx}`,
            indicatorId: cond.indicator,
            name: cond.indicator,
            operator: cond.operator,
            value: cond.value,
            combineWith: 'AND'
          })) || []
          
          newStages.push({
            stage: 2,
            enabled: true,
            indicators,
            passAllRequired: true
          })
        } else {
          newStages.push({ stage: 2, enabled: false, indicators: [], passAllRequired: true })
        }
        
        if (initialStrategy.stage3 && initialStrategy.stage3.conditions?.length > 0) {
          const indicators = initialStrategy.stage3.conditions?.map((cond: any, idx: number) => ({
            id: `s3-${idx}`,
            indicatorId: cond.indicator,
            name: cond.indicator,
            operator: cond.operator,
            value: cond.value,
            combineWith: 'AND'
          })) || []
          
          newStages.push({
            stage: 3,
            enabled: true,
            indicators,
            passAllRequired: true
          })
        } else {
          newStages.push({ stage: 3, enabled: false, indicators: [], passAllRequired: true })
        }
        
        setStrategy({
          type,
          stages: newStages,
          usedIndicators: new Set()
        })
      }
    }
  }, [initialStrategy, type])

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

  // 지표별 특화된 연산자 옵션
  const getOperatorOptions = (indicatorId: string) => {
    // 기본 비교 연산자
    const basicOptions = [
      { value: '>', label: '초과 (>)' },
      { value: '<', label: '미만 (<)' },
      { value: '>=', label: '이상 (≥)' },
      { value: '<=', label: '이하 (≤)' },
      { value: '=', label: '같음 (=)' }
    ]
    
    // 이동평균선 전용 (SMA, EMA)
    const movingAverageOptions = [
      { value: 'price_above', label: '현재가 > 이평선' },
      { value: 'price_below', label: '현재가 < 이평선' },
      { value: 'golden_cross', label: '골든크로스 (단기 > 장기)' },
      { value: 'death_cross', label: '데드크로스 (단기 < 장기)' },
      { value: 'ma_rising', label: '이평선 상승중' },
      { value: 'ma_falling', label: '이평선 하락중' },
      { value: 'perfect_order_bull', label: '정배열 (단기>중기>장기)' },
      { value: 'perfect_order_bear', label: '역배열 (장기>중기>단기)' },
      { value: 'distance_from_ma', label: '이평선 이격도 (%)' },
      { value: 'ma_support', label: '이평선 지지 (터치 후 반등)' },
      { value: 'ma_resistance', label: '이평선 저항 (터치 후 하락)' },
      { value: 'ma_convergence', label: '이평선 수렴 (변동성 감소)' },
      { value: 'ma_divergence', label: '이평선 확산 (변동성 증가)' }
    ]
    
    // 일목균형표 전용 옵션 (5대 요소 기반)
    const ichimokuOptions = [
      // 구름대 관련
      { value: 'price_above_cloud', label: '가격 > 구름대 (강세)' },
      { value: 'price_below_cloud', label: '가격 < 구름대 (약세)' },
      { value: 'price_in_cloud', label: '가격 구름대 내부 (보합)' },
      { value: 'cloud_breakout_up', label: '구름대 상향 돌파' },
      { value: 'cloud_breakout_down', label: '구름대 하향 돌파' },
      { value: 'cloud_green', label: '양운(선행A > 선행B)' },
      { value: 'cloud_red', label: '음운(선행A < 선행B)' },
      { value: 'cloud_twist', label: '구름대 꼬임 (전환점)' },
      { value: 'cloud_thickness_increasing', label: '구름대 두께 증가 (변동성 확대)' },
      { value: 'cloud_thickness_decreasing', label: '구름대 두께 감소 (변동성 축소)' },
      // 전환선/기준선 관련
      { value: 'tenkan_above_kijun', label: '전환선 > 기준선 (단기강세)' },
      { value: 'tenkan_below_kijun', label: '전환선 < 기준선 (단기약세)' },
      { value: 'tenkan_cross_kijun_up', label: '전환선 기준선 상향교차' },
      { value: 'tenkan_cross_kijun_down', label: '전환선 기준선 하향교차' },
      { value: 'price_above_kijun', label: '가격 > 기준선' },
      { value: 'price_above_tenkan', label: '가격 > 전환선' },
      // 후행스팬 관련
      { value: 'chikou_above_price', label: '후행스팬 > 26일전 가격' },
      { value: 'chikou_below_price', label: '후행스팬 < 26일전 가격' },
      { value: 'chikou_above_cloud', label: '후행스팬 > 구름대' },
      // 삼역호전
      { value: 'three_line_bullish', label: '삼역호전 강세 (모든 조건 충족)' },
      { value: 'three_line_bearish', label: '삼역호전 약세 (모든 조건 미충족)' }
    ]
    
    // 볼린저밴드 전용 옵션
    const bollingerOptions = [
      // 밴드 위치 관련
      { value: 'price_above_upper', label: '가격 > 상단밴드 (과매수)' },
      { value: 'price_below_lower', label: '가격 < 하단밴드 (과매도)' },
      { value: 'price_above_middle', label: '가격 > 중심선 (20일 이평)' },
      { value: 'price_below_middle', label: '가격 < 중심선 (20일 이평)' },
      // 밴드 터치/돌파
      { value: 'upper_touch', label: '상단밴드 터치 (저항)' },
      { value: 'lower_touch', label: '하단밴드 터치 (지지)' },
      { value: 'upper_breakout', label: '상단밴드 돌파 (추세강화)' },
      { value: 'lower_breakout', label: '하단밴드 돌파 (추세강화)' },
      { value: 'band_walk_upper', label: '상단밴드 따라 상승 (강한 상승추세)' },
      { value: 'band_walk_lower', label: '하단밴드 따라 하락 (강한 하락추세)' },
      // 밴드폭 관련
      { value: 'band_squeeze', label: '밴드 수축 (변동성 감소)' },
      { value: 'band_expansion', label: '밴드 확장 (변동성 증가)' },
      { value: 'band_squeeze_fire', label: '스퀴즈 후 확장 (브레이크아웃)' },
      // %B 지표 (0-1 정규화)
      { value: 'percent_b_high', label: '%B > 0.8 (상단 근접)' },
      { value: 'percent_b_low', label: '%B < 0.2 (하단 근접)' },
      { value: 'percent_b_above_1', label: '%B > 1 (밴드 이탈)' },
      { value: 'percent_b_below_0', label: '%B < 0 (밴드 이탈)' },
      { value: 'percent_b_divergence', label: '%B 다이버전스' }
    ]
    
    // MACD 전용 옵션 (12-26-9 기본설정)
    const macdOptions = [
      // MACD 라인과 시그널 라인
      { value: 'macd_above_signal', label: 'MACD > Signal (강세)' },
      { value: 'macd_below_signal', label: 'MACD < Signal (약세)' },
      { value: 'macd_cross_signal_up', label: 'MACD 시그널 상향교차 (매수신호)' },
      { value: 'macd_cross_signal_down', label: 'MACD 시그널 하향교차 (매도신호)' },
      // 제로라인 관련
      { value: 'macd_above_zero', label: 'MACD > 0 (상승추세)' },
      { value: 'macd_below_zero', label: 'MACD < 0 (하락추세)' },
      { value: 'macd_cross_zero_up', label: 'MACD 0선 상향돌파' },
      { value: 'macd_cross_zero_down', label: 'MACD 0선 하향돌파' },
      // 히스토그램 (MACD - Signal)
      { value: 'histogram_positive', label: '히스토그램 > 0 (강세)' },
      { value: 'histogram_negative', label: '히스토그램 < 0 (약세)' },
      { value: 'histogram_increasing', label: '히스토그램 증가 (모멘텀 강화)' },
      { value: 'histogram_decreasing', label: '히스토그램 감소 (모멘텀 약화)' },
      { value: 'histogram_peak', label: '히스토그램 고점 (전환 가능)' },
      { value: 'histogram_trough', label: '히스토그램 저점 (전환 가능)' },
      // 다이버전스
      { value: 'bullish_divergence', label: '강세 다이버전스 (가격↓ MACD↑)' },
      { value: 'bearish_divergence', label: '약세 다이버전스 (가격↑ MACD↓)' },
      { value: 'hidden_bullish_div', label: '숨은 강세 다이버전스' },
      { value: 'hidden_bearish_div', label: '숨은 약세 다이버전스' }
    ]
    
    // RSI 전용 옵션 (14일 기본)
    const rsiOptions = [
      // 절대값 기준
      { value: 'rsi_oversold_30', label: 'RSI < 30 (과매도)' },
      { value: 'rsi_overbought_70', label: 'RSI > 70 (과매수)' },
      { value: 'rsi_oversold_20', label: 'RSI < 20 (극단 과매도)' },
      { value: 'rsi_overbought_80', label: 'RSI > 80 (극단 과매수)' },
      // 중심선 관련
      { value: 'rsi_above_50', label: 'RSI > 50 (상승모멘텀)' },
      { value: 'rsi_below_50', label: 'RSI < 50 (하락모멘텀)' },
      { value: 'rsi_cross_50_up', label: 'RSI 50 상향돌파' },
      { value: 'rsi_cross_50_down', label: 'RSI 50 하향돌파' },
      // 과매도/과매수 탈출
      { value: 'rsi_exit_oversold', label: 'RSI 30 상향돌파 (반등신호)' },
      { value: 'rsi_exit_overbought', label: 'RSI 70 하향돌파 (조정신호)' },
      // 다이버전스
      { value: 'rsi_bullish_divergence', label: 'RSI 강세 다이버전스' },
      { value: 'rsi_bearish_divergence', label: 'RSI 약세 다이버전스' },
      { value: 'rsi_hidden_bullish_div', label: 'RSI 숨은 강세 다이버전스' },
      { value: 'rsi_hidden_bearish_div', label: 'RSI 숨은 약세 다이버전스' },
      // 패턴
      { value: 'rsi_failure_swing_buy', label: 'RSI Failure Swing (매수)' },
      { value: 'rsi_failure_swing_sell', label: 'RSI Failure Swing (매도)' },
      // 범위 조건
      { value: 'rsi_range', label: 'RSI 특정 범위' }
    ]
    
    // 스토캐스틱 전용 옵션 (%K, %D)
    const stochasticOptions = [
      // 과매도/과매수
      { value: 'stoch_oversold_20', label: '%K < 20 (과매도)' },
      { value: 'stoch_overbought_80', label: '%K > 80 (과매수)' },
      { value: 'stoch_oversold_exit', label: '%K 20 상향돌파 (반등)' },
      { value: 'stoch_overbought_exit', label: '%K 80 하향돌파 (조정)' },
      // %K와 %D 교차
      { value: 'stoch_k_above_d', label: '%K > %D (단기강세)' },
      { value: 'stoch_k_below_d', label: '%K < %D (단기약세)' },
      { value: 'stoch_k_cross_d_up', label: '%K가 %D 상향교차' },
      { value: 'stoch_k_cross_d_down', label: '%K가 %D 하향교차' },
      { value: 'stoch_k_cross_d_oversold', label: '과매도 구간 %K/%D 상향교차' },
      { value: 'stoch_k_cross_d_overbought', label: '과매수 구간 %K/%D 하향교차' },
      // 슬로우 스토캐스틱
      { value: 'slow_stoch_oversold', label: 'Slow %D < 20' },
      { value: 'slow_stoch_overbought', label: 'Slow %D > 80' },
      // 다이버전스
      { value: 'stoch_bullish_divergence', label: '스토캐스틱 강세 다이버전스' },
      { value: 'stoch_bearish_divergence', label: '스토캐스틱 약세 다이버전스' }
    ]
    
    // 거래량 지표 옵션
    const volumeOptions = [
      // 거래량 변화
      { value: 'volume_increase', label: '거래량 증가 (전일 대비)' },
      { value: 'volume_decrease', label: '거래량 감소 (전일 대비)' },
      { value: 'volume_spike', label: '거래량 폭증 (평균 2배 이상)' },
      { value: 'volume_above_ma', label: '거래량 > 20일 평균' },
      { value: 'volume_below_ma', label: '거래량 < 20일 평균' },
      // 가격-거래량 관계
      { value: 'price_up_volume_up', label: '가격↑ 거래량↑ (강세지속)' },
      { value: 'price_up_volume_down', label: '가격↑ 거래량↓ (상승력약화)' },
      { value: 'price_down_volume_up', label: '가격↓ 거래량↑ (매도세강함)' },
      { value: 'price_down_volume_down', label: '가격↓ 거래량↓ (바닥근접)' },
      { value: 'volume_dry_up', label: '거래량 고갈 (3일 연속 감소)' },
      { value: 'volume_climax', label: '거래량 클라이맥스 (극단적 폭증)' },
      // 특정 배수 조건
      { value: 'volume_multiplier', label: '평균 대비 N배' }
    ]
    
    // OBV (On-Balance Volume) 전용
    const obvOptions = [
      { value: 'obv_rising', label: 'OBV 상승 (매집)' },
      { value: 'obv_falling', label: 'OBV 하락 (분산)' },
      { value: 'obv_divergence_bullish', label: 'OBV 강세 다이버전스' },
      { value: 'obv_divergence_bearish', label: 'OBV 약세 다이버전스' },
      { value: 'obv_above_ma', label: 'OBV > 이동평균' },
      { value: 'obv_below_ma', label: 'OBV < 이동평균' },
      { value: 'obv_breakout', label: 'OBV 신고점 돌파' },
      { value: 'obv_breakdown', label: 'OBV 신저점 하향돌파' },
      { value: 'obv_ma_cross_up', label: 'OBV 이평선 상향돌파' },
      { value: 'obv_ma_cross_down', label: 'OBV 이평선 하향돌파' }
    ]
    
    // VWAP (Volume Weighted Average Price) 전용
    const vwapOptions = [
      { value: 'price_above_vwap', label: '가격 > VWAP (강세)' },
      { value: 'price_below_vwap', label: '가격 < VWAP (약세)' },
      { value: 'price_cross_vwap_up', label: '가격 VWAP 상향돌파' },
      { value: 'price_cross_vwap_down', label: '가격 VWAP 하향돌파' },
      { value: 'vwap_support', label: 'VWAP 지지선 역할' },
      { value: 'vwap_resistance', label: 'VWAP 저항선 역할' }
    ]
    
    // ADX (Average Directional Index) 전용
    const adxOptions = [
      // 추세 강도
      { value: 'adx_strong_trend', label: 'ADX > 25 (강한 추세)' },
      { value: 'adx_weak_trend', label: 'ADX < 25 (약한 추세/횡보)' },
      { value: 'adx_very_strong', label: 'ADX > 40 (매우 강한 추세)' },
      { value: 'adx_no_trend', label: 'ADX < 20 (무추세)' },
      { value: 'adx_extreme', label: 'ADX > 50 (극단 추세)' },
      // ADX 변화
      { value: 'adx_rising', label: 'ADX 상승 (추세 강화)' },
      { value: 'adx_falling', label: 'ADX 하락 (추세 약화)' },
      { value: 'adx_turning_up', label: 'ADX 바닥에서 상승전환' },
      { value: 'adx_turning_down', label: 'ADX 고점에서 하락전환' }
    ]
    
    // DMI (+DI, -DI) 전용
    const dmiOptions = [
      // 방향성 지표
      { value: 'di_bullish', label: '+DI > -DI (상승추세)' },
      { value: 'di_bearish', label: '-DI > +DI (하락추세)' },
      { value: 'di_cross_bullish', label: '+DI가 -DI 상향교차' },
      { value: 'di_cross_bearish', label: '-DI가 +DI 상향교차' },
      // ADX와 조합
      { value: 'strong_bullish', label: '+DI>-DI & ADX>25' },
      { value: 'strong_bearish', label: '-DI>+DI & ADX>25' }
    ]
    
    // Parabolic SAR 전용
    const sarOptions = [
      { value: 'sar_below_price', label: 'SAR < 가격 (상승추세)' },
      { value: 'sar_above_price', label: 'SAR > 가격 (하락추세)' },
      { value: 'sar_flip_bullish', label: 'SAR 상승전환 (매수신호)' },
      { value: 'sar_flip_bearish', label: 'SAR 하락전환 (매도신호)' },
      { value: 'sar_acceleration', label: 'SAR 가속 (추세강화)' }
    ]
    
    // ATR (Average True Range) 전용
    const atrOptions = [
      { value: 'atr_high', label: 'ATR 높음 (변동성 큼)' },
      { value: 'atr_low', label: 'ATR 낮음 (변동성 작음)' },
      { value: 'atr_increasing', label: 'ATR 증가 (변동성 확대)' },
      { value: 'atr_decreasing', label: 'ATR 감소 (변동성 축소)' },
      { value: 'atr_breakout', label: 'ATR 급증 (브레이크아웃)' },
      { value: 'atr_squeeze', label: 'ATR 수축 (변동성 축소)' },
      { value: 'atr_expansion', label: 'ATR 확장 (변동성 확대)' },
      { value: 'atr_multiple', label: 'ATR 배수 (손절/익절용)' }
    ]
    
    // CCI (Commodity Channel Index) 전용
    const cciOptions = [
      { value: 'cci_overbought_100', label: 'CCI > +100 (과매수)' },
      { value: 'cci_oversold_100', label: 'CCI < -100 (과매도)' },
      { value: 'cci_extreme_200', label: 'CCI > +200 (극단 과매수)' },
      { value: 'cci_extreme_neg200', label: 'CCI < -200 (극단 과매도)' },
      { value: 'cci_zero_cross_up', label: 'CCI 0선 상향돌파' },
      { value: 'cci_zero_cross_down', label: 'CCI 0선 하향돌파' },
      { value: 'cci_divergence', label: 'CCI 다이버전스' }
    ]
    
    // Williams %R 전용
    const williamsOptions = [
      { value: 'williams_oversold_80', label: '%R < -80 (과매도)' },
      { value: 'williams_overbought_20', label: '%R > -20 (과매수)' },
      { value: 'williams_oversold_exit', label: '%R -80 탈출 (반등)' },
      { value: 'williams_overbought_exit', label: '%R -20 탈출 (조정)' },
      { value: 'williams_midline_cross', label: '%R -50 교차' },
      { value: 'williams_divergence', label: 'Williams %R 다이버전스' }
    ]
    
    // 지표별 조건 매핑
    switch(indicatorId) {
      case 'sma':
      case 'ema':
        return movingAverageOptions
      
      case 'ichimoku':
        return ichimokuOptions
      
      case 'bb':
        return bollingerOptions
      
      case 'macd':
        return macdOptions
      
      case 'rsi':
        return rsiOptions
        
      case 'stochastic':
        return stochasticOptions
      
      case 'volume':
        return volumeOptions
        
      case 'obv':
        return obvOptions
        
      case 'vwap':
        return vwapOptions
      
      case 'adx':
        return adxOptions
        
      case 'dmi':
        return dmiOptions
      
      case 'parabolic':
        return sarOptions
      
      case 'atr':
        return atrOptions
        
      case 'cci':
        return cciOptions
        
      case 'williams':
        return williamsOptions
      
      default:
        return basicOptions
    }
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

            {/* 연산자 - 지표별 특화 조건 */}
            <Grid item xs={tempIndicator.indicatorId && ['ichimoku', 'bb', 'macd', 'volume', 'adx', 'parabolic'].includes(tempIndicator.indicatorId) ? 12 : 6}>
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
                  {getOperatorOptions(tempIndicator.indicatorId).map(op => (
                    <MenuItem key={op.value} value={op.value}>
                      {op.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* 값 입력 필드 - 조건별 맞춤 표시 */}
            {(() => {
              // 값이 필요한 조건들만 정의
              const needsValueConditions = [
                'distance_from_ma', // 이격도 %
                'volume_multiplier', // 거래량 배수
                'atr_multiple', // ATR 배수
                'rsi_range', // RSI 범위
                'bb_width_threshold', // 볼린저밴드 폭 임계값
                'adx_threshold', // ADX 임계값
                'cci_threshold', // CCI 임계값
                '>', '<', '>=', '<=', '=' // 기본 비교 연산자
              ]
              
              // 범위 값이 필요한 조건들
              const needsRangeConditions = ['rsi_range']
              
              return needsValueConditions.includes(tempIndicator.operator) ? (
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
                  helperText={
                    tempIndicator.operator === 'distance_from_ma' ? '이격도 % (예: 5 = 5%)' :
                    tempIndicator.operator === 'volume_multiplier' ? '평균 대비 배수 (예: 2 = 2배)' :
                    tempIndicator.operator === 'atr_multiple' ? 'ATR 배수 (예: 2 = 2*ATR)' :
                    tempIndicator.operator === 'rsi_range' ? '하한-상한 (예: 30-70)' :
                    tempIndicator.operator === 'bb_width_threshold' ? '밴드폭 임계값 (예: 10 = 10%)' :
                    tempIndicator.operator === 'adx_threshold' ? 'ADX 임계값 (예: 25)' :
                    tempIndicator.operator === 'cci_threshold' ? 'CCI 임계값 (예: 100)' :
                    tempIndicator.indicatorId === 'rsi' && tempIndicator.operator.includes('>') ? 'RSI 값 (0-100)' :
                    tempIndicator.indicatorId === 'stochastic' && tempIndicator.operator.includes('>') ? '%K 값 (0-100)' :
                    tempIndicator.indicatorId === 'cci' && tempIndicator.operator.includes('>') ? 'CCI 값 (일반적으로 ±100)' :
                    tempIndicator.indicatorId === 'williams' && tempIndicator.operator.includes('>') ? '%R 값 (-100 ~ 0)' :
                    tempIndicator.indicatorId === 'adx' && tempIndicator.operator.includes('>') ? 'ADX 값 (0-100)' :
                    ''
                  }
                />
              </Grid>
              ) : null
            })()}

            {/* 지표별 상세 설명 */}
            {tempIndicator.indicatorId && (
              <Grid item xs={12}>
                <Alert severity="info">
                  <Typography variant="caption">
                    {tempIndicator.indicatorId === 'ichimoku' && 
                      '일목균형표: 구름대(선행스팬), 전환선/기준선, 후행스팬을 종합적으로 분석. 구름대 돌파는 강력한 추세 전환 신호'}
                    {tempIndicator.indicatorId === 'rsi' && 
                      'RSI: 30 이하 과매도 구간(반등 가능), 70 이상 과매수 구간(조정 가능). 다이버전스 확인 중요'}
                    {tempIndicator.indicatorId === 'macd' && 
                      'MACD: 시그널선 교차는 매매신호, 0선 돌파는 추세전환, 히스토그램은 모멘텀 강도 표시'}
                    {tempIndicator.indicatorId === 'bb' && 
                      '볼린저밴드: 밴드 폭은 변동성, 상/하단 터치는 과매수/과매도, 밴드 돌파는 추세 시작'}
                    {tempIndicator.indicatorId === 'sma' && 
                      'SMA: 이동평균선 돌파는 추세 전환, 지지/저항선 역할. 골든크로스/데드크로스 확인'}
                    {tempIndicator.indicatorId === 'ema' && 
                      'EMA: SMA보다 최근 가격에 가중치. 단기 추세 파악에 유리'}
                    {tempIndicator.indicatorId === 'stochastic' && 
                      '스토캐스틱: %K와 %D 교차 확인. 20 이하 과매도, 80 이상 과매수'}
                    {tempIndicator.indicatorId === 'volume' && 
                      '거래량: 가격 움직임의 신뢰도 확인. 거래량 급증은 추세 시작/종료 신호'}
                    {tempIndicator.indicatorId === 'obv' && 
                      'OBV: 누적거래량으로 매집/분산 확인. 가격과 다이버전스 시 추세 전환 가능'}
                    {tempIndicator.indicatorId === 'adx' && 
                      'ADX: 25 이상 강한 추세, 25 이하 횡보. +DI/-DI 교차로 방향 확인'}
                    {tempIndicator.indicatorId === 'atr' && 
                      'ATR: 변동성 측정 지표. 손절/익절 설정, 포지션 사이징에 활용'}
                    {tempIndicator.indicatorId === 'cci' && 
                      'CCI: ±100 이상/이하 과매수/과매도. 추세장에서 유용'}
                    {tempIndicator.indicatorId === 'williams' && 
                      'Williams %R: -20 이상 과매수, -80 이하 과매도. 스토캐스틱과 유사'}
                    {tempIndicator.indicatorId === 'dmi' && 
                      'DMI: +DI > -DI 상승추세, 반대는 하락추세. ADX와 함께 사용'}
                    {tempIndicator.indicatorId === 'parabolic' && 
                      'Parabolic SAR: 점이 가격 아래는 상승추세, 위는 하락추세. 추세 추종에 효과적'}
                    {tempIndicator.indicatorId === 'vwap' && 
                      'VWAP: 거래량 가중 평균가격. 기관 매매 기준선, 당일 매매에 중요'}
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