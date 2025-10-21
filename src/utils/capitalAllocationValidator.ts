/**
 * 전략별 자금 할당 검증 유틸리티
 */

interface Strategy {
  id: string
  name: string
  allocated_capital?: number
  allocated_percent?: number
  is_active?: boolean
}

export interface AllocationValidationResult {
  isValid: boolean
  totalPercent: number
  totalCapital: number
  errors: string[]
  warnings: string[]
  suggestions: string[]
}

/**
 * 전략별 자금 할당 유효성 검증
 */
export function validateCapitalAllocation(
  strategies: Strategy[],
  totalAccountBalance?: number
): AllocationValidationResult {
  const result: AllocationValidationResult = {
    isValid: true,
    totalPercent: 0,
    totalCapital: 0,
    errors: [],
    warnings: [],
    suggestions: []
  }

  // 활성화된 전략만 필터링
  const activeStrategies = strategies.filter(s => s.is_active !== false)

  if (activeStrategies.length === 0) {
    result.warnings.push('활성화된 전략이 없습니다.')
    return result
  }

  // 총 할당 비율 계산
  activeStrategies.forEach(strategy => {
    if (strategy.allocated_percent) {
      result.totalPercent += strategy.allocated_percent
    }
    if (strategy.allocated_capital) {
      result.totalCapital += strategy.allocated_capital
    }
  })

  // 1. 할당 비율이 100%를 초과하는지 확인
  if (result.totalPercent > 100) {
    result.isValid = false
    result.errors.push(
      `전체 할당 비율이 ${result.totalPercent.toFixed(1)}%로 100%를 초과합니다. ` +
      `각 전략의 할당 비율을 조정하세요.`
    )
  }

  // 2. 할당 비율이 100% 미만일 때 경고
  if (result.totalPercent > 0 && result.totalPercent < 80) {
    result.warnings.push(
      `전체 할당 비율이 ${result.totalPercent.toFixed(1)}%입니다. ` +
      `${(100 - result.totalPercent).toFixed(1)}%의 자금이 유휴 상태입니다.`
    )
    result.suggestions.push('더 많은 자금을 활용하려면 전략별 할당 비율을 높이세요.')
  }

  // 3. 계좌 잔고가 제공된 경우, 할당 자금이 잔고를 초과하는지 확인
  if (totalAccountBalance && result.totalCapital > totalAccountBalance) {
    result.isValid = false
    result.errors.push(
      `할당된 총 자금 ${result.totalCapital.toLocaleString()}원이 ` +
      `계좌 잔고 ${totalAccountBalance.toLocaleString()}원을 초과합니다.`
    )
  }

  // 4. 자금과 비율이 혼용되었을 때 경고
  const hasCapital = activeStrategies.some(s => s.allocated_capital && s.allocated_capital > 0)
  const hasPercent = activeStrategies.some(s => s.allocated_percent && s.allocated_percent > 0)

  if (hasCapital && hasPercent) {
    result.warnings.push(
      '일부 전략은 고정 자금으로, 일부는 비율로 설정되어 있습니다. ' +
      '통일된 방식을 사용하는 것을 권장합니다.'
    )
  }

  // 5. 할당되지 않은 활성 전략이 있는지 확인
  const unallocatedStrategies = activeStrategies.filter(
    s => (!s.allocated_capital || s.allocated_capital === 0) &&
         (!s.allocated_percent || s.allocated_percent === 0)
  )

  if (unallocatedStrategies.length > 0) {
    result.warnings.push(
      `${unallocatedStrategies.length}개 전략에 자금이 할당되지 않았습니다: ` +
      unallocatedStrategies.map(s => s.name).join(', ')
    )
    result.suggestions.push('모든 활성 전략에 자금을 할당하세요.')
  }

  // 6. 단일 전략에 과도하게 집중된 경우 경고
  activeStrategies.forEach(strategy => {
    if (strategy.allocated_percent && strategy.allocated_percent > 50) {
      result.warnings.push(
        `전략 "${strategy.name}"에 ${strategy.allocated_percent}%가 할당되어 ` +
        `과도하게 집중되어 있습니다. 리스크 분산을 고려하세요.`
      )
    }
  })

  return result
}

/**
 * 할당 비율 자동 조정 (균등 배분)
 */
export function autoAllocateEqual(strategies: Strategy[]): Strategy[] {
  const activeStrategies = strategies.filter(s => s.is_active !== false)
  if (activeStrategies.length === 0) return strategies

  const equalPercent = Math.floor(100 / activeStrategies.length)
  const remainder = 100 - (equalPercent * activeStrategies.length)

  return strategies.map((strategy, index) => {
    if (strategy.is_active === false) return strategy

    const activeIndex = activeStrategies.findIndex(s => s.id === strategy.id)
    return {
      ...strategy,
      allocated_percent: activeIndex === 0 ? equalPercent + remainder : equalPercent,
      allocated_capital: 0  // 비율 모드로 전환
    }
  })
}

/**
 * 계좌 잔고 기준으로 비율을 자금으로 변환
 */
export function convertPercentToCapital(
  strategies: Strategy[],
  totalAccountBalance: number
): Strategy[] {
  return strategies.map(strategy => ({
    ...strategy,
    allocated_capital: strategy.allocated_percent
      ? Math.floor(totalAccountBalance * strategy.allocated_percent / 100)
      : strategy.allocated_capital,
    allocated_percent: 0  // 자금 모드로 전환
  }))
}

/**
 * 할당 자금 기준으로 비율 계산
 */
export function convertCapitalToPercent(
  strategies: Strategy[],
  totalAccountBalance: number
): Strategy[] {
  if (!totalAccountBalance || totalAccountBalance === 0) {
    console.warn('계좌 잔고가 0이거나 제공되지 않았습니다.')
    return strategies
  }

  return strategies.map(strategy => ({
    ...strategy,
    allocated_percent: strategy.allocated_capital
      ? Math.round((strategy.allocated_capital / totalAccountBalance) * 100 * 10) / 10
      : strategy.allocated_percent,
    allocated_capital: 0  // 비율 모드로 전환
  }))
}

/**
 * 전략별 실제 사용 가능 자금 계산
 */
export function calculateAvailableCapital(
  strategy: Strategy,
  totalAccountBalance: number
): number {
  // 할당 자금이 우선
  if (strategy.allocated_capital && strategy.allocated_capital > 0) {
    return strategy.allocated_capital
  }

  // 할당 비율로 계산
  if (strategy.allocated_percent && strategy.allocated_percent > 0) {
    return Math.floor(totalAccountBalance * strategy.allocated_percent / 100)
  }

  // 할당되지 않은 경우 0
  return 0
}
