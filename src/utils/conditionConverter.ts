/**
 * 전략 조건 형식 변환 유틸리티
 * 구 형식(indicator/operator/value) → 표준 형식(left/operator/right)
 */

interface OldCondition {
  id?: string
  type?: 'buy' | 'sell'
  indicator: string
  operator: string
  value: number | string
  combineWith?: 'AND' | 'OR'
  // 기타 레거시 필드
  ichimokuLine?: string
  confirmBars?: number
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
  const left = normalizeIndicatorName(oldCondition.indicator)
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