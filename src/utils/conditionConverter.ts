/**
 * 전략 조건 형식 변환 유틸리티
 * 구 형식(indicator/operator/value) → 표준 형식(left/operator/right)
 */

interface OldCondition {
  id?: string
  type?: 'buy' | 'sell'
  indicator?: string
  operator: string
  value?: number | string
  combineWith?: 'AND' | 'OR'
  // 표준 형식 필드 (left/right)
  left?: string
  right?: string | number
  // 기타 레거시 필드
  ichimokuLine?: string
  confirmBars?: number
  // 다중 출력 지표 필드
  bollingerLine?: string
  macdLine?: string
  stochLine?: string
}

interface StandardCondition {
  left: string | number
  operator: string
  right: string | number
}

/**
 * 연산자 변환 매핑
 */
const OPERATOR_MAPPING: Record<string, string> = {
  'cross_above': 'crossover',
  'cross_below': 'crossunder',
  '>': '>',
  '<': '<',
  '>=': '>=',
  '<=': '<=',
  '=': '==',
  '==': '==',
  '!=': '!=',
  // 기타 유지
  'cloud_above': 'cloud_above',
  'cloud_below': 'cloud_below',
  'tenkan_kijun_cross_up': 'tenkan_kijun_cross_up',
  'tenkan_kijun_cross_down': 'tenkan_kijun_cross_down'
}

/**
 * 지표명 정규화 (대문자 → 소문자, 언더스코어 제거)
 */
const normalizeIndicatorName = (name: string): string => {
  return name
    .toLowerCase()
    .replace(/_/g, '_')  // 일단 유지
    .replace('ma_', 'sma_')  // MA → SMA
    .replace('price', 'close')  // PRICE → close
}

/**
 * 단일 조건 변환
 */
export const convertConditionToStandard = (
  oldCondition: OldCondition
): StandardCondition => {
  // MACD 커스텀 연산자 특수 처리
  const isMacdCondition = oldCondition.indicator === 'macd' ||
                          oldCondition.left === 'macd' ||
                          oldCondition.left === 'macd_line' ||
                          oldCondition.left === 'macd_hist'

  if (isMacdCondition) {
    if (oldCondition.operator === 'macd_above_signal') {
      return { left: 'macd_line', operator: '>', right: 'macd_signal' }
    } else if (oldCondition.operator === 'macd_below_signal') {
      return { left: 'macd_line', operator: '<', right: 'macd_signal' }
    } else if (oldCondition.operator === 'macd_cross_signal_up') {
      return { left: 'macd_line', operator: 'crossover', right: 'macd_signal' }
    } else if (oldCondition.operator === 'macd_cross_signal_down') {
      return { left: 'macd_line', operator: 'crossunder', right: 'macd_signal' }
    } else if (oldCondition.operator === 'histogram_positive') {
      return { left: 'macd_hist', operator: '>', right: 0 }
    } else if (oldCondition.operator === 'histogram_negative') {
      return { left: 'macd_hist', operator: '<', right: 0 }
    } else if (oldCondition.operator === 'macd_above_zero') {
      return { left: 'macd_line', operator: '>', right: 0 }
    } else if (oldCondition.operator === 'macd_below_zero') {
      return { left: 'macd_line', operator: '<', right: 0 }
    }
  }

  // 볼린저 밴드 특수 처리: price_above/price_below를 close와 밴드 비교로 변환
  if ((oldCondition.indicator === 'bollinger' || oldCondition.indicator === 'bb') && oldCondition.bollingerLine) {
    const bandLine = oldCondition.bollingerLine // bollinger_upper, bollinger_middle, bollinger_lower

    if (oldCondition.operator === 'price_above') {
      // 종가가 밴드보다 위 → close > bollinger_xxx
      return { left: 'close', operator: '>', right: bandLine }
    } else if (oldCondition.operator === 'price_below') {
      // 종가가 밴드보다 아래 → close < bollinger_xxx
      return { left: 'close', operator: '<', right: bandLine }
    } else if (oldCondition.operator === 'cross_above') {
      // 종가가 밴드를 상향 돌파 → close crossover bollinger_xxx
      return { left: 'close', operator: 'crossover', right: bandLine }
    } else if (oldCondition.operator === 'cross_below') {
      // 종가가 밴드를 하향 돌파 → close crossunder bollinger_xxx
      return { left: 'close', operator: 'crossunder', right: bandLine }
    }
  }

  // 다중 출력 지표의 경우 특정 라인을 left로 사용
  let left: string

  if (oldCondition.indicator === 'bollinger' && oldCondition.bollingerLine) {
    left = oldCondition.bollingerLine
  } else if (oldCondition.indicator === 'macd' && oldCondition.macdLine) {
    left = oldCondition.macdLine
  } else if (oldCondition.indicator === 'stochastic' && oldCondition.stochLine) {
    left = oldCondition.stochLine
  } else if (oldCondition.indicator === 'ichimoku' && oldCondition.ichimokuLine) {
    left = oldCondition.ichimokuLine
  } else {
    left = normalizeIndicatorName(oldCondition.indicator)
  }

  const operator = OPERATOR_MAPPING[oldCondition.operator] || oldCondition.operator
  const right = typeof oldCondition.value === 'string'
    ? normalizeIndicatorName(oldCondition.value)
    : oldCondition.value

  return {
    left,
    operator,
    right
  }
}

/**
 * 조건 배열 변환
 */
export const convertConditionsToStandard = (
  oldConditions: OldCondition[]
): StandardCondition[] => {
  return oldConditions.map(convertConditionToStandard)
}

/**
 * 전략 전체 변환 (buyConditions + sellConditions)
 */
export const convertStrategyConditions = (strategy: {
  buyConditions?: OldCondition[]
  sellConditions?: OldCondition[]
}) => {
  return {
    buyConditions: strategy.buyConditions
      ? convertConditionsToStandard(strategy.buyConditions)
      : [],
    sellConditions: strategy.sellConditions
      ? convertConditionsToStandard(strategy.sellConditions)
      : []
  }
}

/**
 * 조건 형식 감지
 */
export const detectConditionFormat = (condition: any): 'standard' | 'legacy' => {
  if ('left' in condition && 'right' in condition) {
    return 'standard'
  }
  if ('indicator' in condition && 'value' in condition) {
    return 'legacy'
  }
  return 'legacy'
}

/**
 * 전략 전체 형식 감지
 */
export const detectStrategyFormat = (strategy: {
  buyConditions?: any[]
  sellConditions?: any[]
}): 'standard' | 'legacy' | 'mixed' => {
  const allConditions = [
    ...(strategy.buyConditions || []),
    ...(strategy.sellConditions || [])
  ]

  if (allConditions.length === 0) {
    return 'standard' // 빈 배열은 표준으로 간주
  }

  const formats = allConditions.map(detectConditionFormat)
  const hasStandard = formats.includes('standard')
  const hasLegacy = formats.includes('legacy')

  if (hasStandard && hasLegacy) return 'mixed'
  if (hasStandard) return 'standard'
  return 'legacy'
}

/**
 * 저장 전 자동 변환 (안전)
 */
export const ensureStandardFormat = (strategy: {
  buyConditions?: any[]
  sellConditions?: any[]
}) => {
  const format = detectStrategyFormat(strategy)

  if (format === 'standard') {
    // 이미 표준 형식
    return strategy
  }

  // 레거시 또는 혼재 → 변환
  console.log(`[Converter] Detected ${format} format, converting to standard...`)

  return {
    ...strategy,
    ...convertStrategyConditions(strategy)
  }
}