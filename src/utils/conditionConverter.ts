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
 * 지표 컬럼 매핑 (다중 출력 지표)
 * 예: 'stochastic' → 'stochastic_k' (기본값)
 */
const INDICATOR_COLUMN_MAPPING: Record<string, string> = {
  'stochastic': 'stochastic_k',  // stochastic → stochastic_k (기본값)
  'stoch_k': 'stochastic_k',     // 레거시 호환
  'stoch_d': 'stochastic_d',     // 레거시 호환
}

/**
 * 지표명 정규화 (대문자 → 소문자, 언더스코어 제거)
 */
const normalizeIndicatorName = (name: string): string => {
  const normalized = name
    .toLowerCase()
    .replace(/_/g, '_')  // 일단 유지
    .replace('ma_', 'sma_')  // MA → SMA
    .replace('price', 'close')  // PRICE → close

  // 컬럼 매핑 적용
  return INDICATOR_COLUMN_MAPPING[normalized] || normalized
}

/**
 * 단일 조건 변환
 */
export const convertConditionToStandard = (
  oldCondition: OldCondition
): StandardCondition => {
  // golden_cross / death_cross 특수 처리 (잘못된 조건 수정)
  // 문제: golden_cross는 2개의 MA가 필요한데 숫자 값과 비교하려고 함
  // 해결: 단순 비교로 변환하거나 에러 표시
  if (oldCondition.operator === 'golden_cross' || oldCondition.operator === 'death_cross') {
    const isGolden = oldCondition.operator === 'golden_cross'

    // right가 숫자인 경우 (잘못된 설정)
    if (typeof oldCondition.right === 'number' || !isNaN(Number(oldCondition.right))) {
      console.warn(`[ConditionConverter] ${oldCondition.operator} requires two MAs, but got number value. Converting to simple comparison.`)
      return {
        left: oldCondition.left || oldCondition.indicator || 'sma',
        operator: isGolden ? '>' : '<',
        right: oldCondition.right || oldCondition.value || 0
      }
    }
  }

  // Ichimoku 커스텀 연산자 특수 처리
  // 중요: Ichimoku 컬럼명은 ichimoku_ 접두사가 붙음 (ichimoku_tenkan, ichimoku_kijun)
  if (oldCondition.operator === 'tenkan_above_kijun' || oldCondition.operator === 'tenkan_below_kijun') {
    const isAbove = oldCondition.operator === 'tenkan_above_kijun'

    console.warn(`[ConditionConverter] ${oldCondition.operator} converted to ichimoku_tenkan ${isAbove ? '>' : '<'} ichimoku_kijun`)
    return {
      left: 'ichimoku_tenkan',
      operator: isAbove ? '>' : '<',
      right: 'ichimoku_kijun'
    }
  }

  // 기타 Ichimoku 연산자들
  if (oldCondition.operator === 'tenkan_cross_kijun_up') {
    return { left: 'ichimoku_tenkan', operator: 'crossover', right: 'ichimoku_kijun' }
  } else if (oldCondition.operator === 'tenkan_cross_kijun_down') {
    return { left: 'ichimoku_tenkan', operator: 'crossunder', right: 'ichimoku_kijun' }
  }

  // 가격 vs 일목균형표 선 비교 연산자들
  if (oldCondition.operator === 'price_above_tenkan') {
    return { left: 'close', operator: '>', right: 'ichimoku_tenkan' }
  } else if (oldCondition.operator === 'price_below_tenkan') {
    return { left: 'close', operator: '<', right: 'ichimoku_tenkan' }
  } else if (oldCondition.operator === 'price_above_kijun') {
    return { left: 'close', operator: '>', right: 'ichimoku_kijun' }
  } else if (oldCondition.operator === 'price_below_kijun') {
    return { left: 'close', operator: '<', right: 'ichimoku_kijun' }
  } else if (oldCondition.operator === 'price_above_senkou_a') {
    return { left: 'close', operator: '>', right: 'ichimoku_senkou_a' }
  } else if (oldCondition.operator === 'price_below_senkou_a') {
    return { left: 'close', operator: '<', right: 'ichimoku_senkou_a' }
  } else if (oldCondition.operator === 'price_above_senkou_b') {
    return { left: 'close', operator: '>', right: 'ichimoku_senkou_b' }
  } else if (oldCondition.operator === 'price_below_senkou_b') {
    return { left: 'close', operator: '<', right: 'ichimoku_senkou_b' }
  }

  // 구름대(Cloud) 관련 연산자들
  if (oldCondition.operator === 'price_above_cloud') {
    // 가격 > 구름대 → close > max(senkou_a, senkou_b)
    return { left: 'close', operator: '>', right: 'ichimoku_cloud_top' }
  } else if (oldCondition.operator === 'price_below_cloud') {
    // 가격 < 구름대 → close < min(senkou_a, senkou_b)
    return { left: 'close', operator: '<', right: 'ichimoku_cloud_bottom' }
  } else if (oldCondition.operator === 'cloud_green') {
    // 양운 → senkou_a > senkou_b
    return { left: 'ichimoku_senkou_a', operator: '>', right: 'ichimoku_senkou_b' }
  } else if (oldCondition.operator === 'cloud_red') {
    // 음운 → senkou_a < senkou_b
    return { left: 'ichimoku_senkou_a', operator: '<', right: 'ichimoku_senkou_b' }
  }

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
    // stochLine 매핑 (stoch_k → stochastic_k)
    left = INDICATOR_COLUMN_MAPPING[oldCondition.stochLine] || oldCondition.stochLine
  } else if (oldCondition.indicator === 'ichimoku' && oldCondition.ichimokuLine) {
    left = oldCondition.ichimokuLine
  } else if (oldCondition.indicator) {
    left = normalizeIndicatorName(oldCondition.indicator)
  } else {
    // fallback: indicator도 없으면 에러 방지
    left = 'close'
  }

  const operator = OPERATOR_MAPPING[oldCondition.operator] || oldCondition.operator
  const right = typeof oldCondition.value === 'string'
    ? normalizeIndicatorName(oldCondition.value)
    : (oldCondition.value ?? 0)

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
  indicators?: any[]
}) => {
  const format = detectStrategyFormat(strategy)

  if (format === 'standard') {
    // 표준 형식이지만 SMA/EMA 같은 동적 컬럼명 수정 필요
    const fixedStrategy = fixDynamicColumnNames(strategy)
    return fixedStrategy
  }

  // 레거시 또는 혼재 → 변환
  console.log(`[Converter] Detected ${format} format, converting to standard...`)

  const converted = {
    ...strategy,
    ...convertStrategyConditions(strategy)
  }

  // 동적 컬럼명 수정
  return fixDynamicColumnNames(converted)
}

/**
 * SMA/EMA 같은 동적 컬럼명 수정
 * sma → sma_20, ema → ema_12 등
 */
const fixDynamicColumnNames = (strategy: {
  buyConditions?: any[]
  sellConditions?: any[]
  indicators?: any[]
}) => {
  const indicators = strategy.indicators || []

  // 지표별 실제 컬럼명 매핑 생성
  const columnMap: Record<string, string> = {}

  indicators.forEach((ind: any) => {
    const name = ind.name?.toLowerCase()
    const params = ind.params || {}

    // SMA, EMA: sma_20, ema_12 형태
    if (name === 'sma' || name === 'ema') {
      const period = params.period || 20
      columnMap[name] = `${name}_${period}`
    }
  })

  // 조건의 left/right 값 수정
  const fixConditions = (conditions: any[]) => {
    return conditions.map(cond => {
      const fixed = { ...cond }

      // left 수정
      if (typeof fixed.left === 'string' && columnMap[fixed.left]) {
        console.log(`[ConditionConverter] Fixing column: ${fixed.left} → ${columnMap[fixed.left]}`)
        fixed.left = columnMap[fixed.left]
      }

      // right 수정 (문자열인 경우만)
      if (typeof fixed.right === 'string' && columnMap[fixed.right]) {
        console.log(`[ConditionConverter] Fixing column: ${fixed.right} → ${columnMap[fixed.right]}`)
        fixed.right = columnMap[fixed.right]
      }

      return fixed
    })
  }

  return {
    ...strategy,
    buyConditions: strategy.buyConditions ? fixConditions(strategy.buyConditions) : [],
    sellConditions: strategy.sellConditions ? fixConditions(strategy.sellConditions) : []
  }
}