// 전략 데이터 검증 및 정리 유틸리티

export interface ValidationResult {
  isValid: boolean
  errors: string[]
  warnings: string[]
}

// 단계별 전략 검증
export function validateStageStrategy(stageStrategy: any): ValidationResult {
  const errors: string[] = []
  const warnings: string[] = []

  if (!stageStrategy) {
    return { isValid: true, errors: [], warnings: [] }
  }

  // 단계 구조 검증
  if (!stageStrategy.stages || !Array.isArray(stageStrategy.stages)) {
    errors.push('단계 정보가 올바르지 않습니다')
    return { isValid: false, errors, warnings }
  }

  // 각 단계 검증
  stageStrategy.stages.forEach((stage: any, index: number) => {
    if (stage.enabled && stage.indicators) {
      // 지표 개수 확인
      if (stage.indicators.length > 5) {
        errors.push(`${index + 1}단계에 지표가 5개를 초과합니다`)
      }

      // 지표 데이터 검증
      stage.indicators.forEach((ind: any) => {
        if (!ind.indicatorId || !ind.operator) {
          warnings.push(`${index + 1}단계의 지표 설정이 불완전합니다`)
        }
      })
      
      // 포지션 비율 검증
      if (stage.positionPercent !== undefined) {
        if (stage.positionPercent < 0 || stage.positionPercent > 100) {
          errors.push(`${index + 1}단계의 비율이 0-100% 범위를 벗어났습니다`)
        }
      } else {
        warnings.push(`${index + 1}단계의 비율 설정이 없습니다`)
      }
    }
  })

  // 지표 중복 검증
  const usedIndicators = new Set<string>()
  stageStrategy.stages.forEach((stage: any) => {
    if (stage.enabled && stage.indicators) {
      stage.indicators.forEach((ind: any) => {
        if (usedIndicators.has(ind.indicatorId)) {
          errors.push(`지표 ${ind.name || ind.indicatorId}가 여러 단계에서 중복 사용되었습니다`)
        }
        usedIndicators.add(ind.indicatorId)
      })
    }
  })

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  }
}

// 투자 유니버스 설정 검증
export function validateInvestmentUniverse(universe: any): ValidationResult {
  const errors: string[] = []
  const warnings: string[] = []

  if (!universe) {
    warnings.push('투자 유니버스 설정이 없습니다')
    return { isValid: true, errors, warnings }
  }

  // 재무 필터 검증
  if (universe.financialFilters) {
    const filters = universe.financialFilters
    
    // 시가총액 범위 검증
    if (filters.marketCap && filters.marketCap[0] >= filters.marketCap[1]) {
      errors.push('시가총액 최소값이 최대값보다 크거나 같습니다')
    }
    
    // PER 범위 검증
    if (filters.per && filters.per[0] >= filters.per[1]) {
      warnings.push('PER 범위 설정을 확인하세요')
    }
    
    // PBR 범위 검증
    if (filters.pbr && filters.pbr[0] >= filters.pbr[1]) {
      warnings.push('PBR 범위 설정을 확인하세요')
    }
    
    // ROE 범위 검증
    if (filters.roe && filters.roe[0] >= filters.roe[1]) {
      warnings.push('ROE 범위 설정을 확인하세요')
    }
  }

  // 섹터 필터 검증
  if (universe.sectorFilters) {
    const { include, exclude } = universe.sectorFilters
    
    // 포함과 제외 섹터 중복 확인
    if (include && exclude) {
      const overlap = include.filter((s: string) => exclude.includes(s))
      if (overlap.length > 0) {
        errors.push(`다음 섹터가 포함과 제외 목록에 동시에 있습니다: ${overlap.join(', ')}`)
      }
    }
  }

  // 포트폴리오 설정 검증
  if (universe.portfolioSettings) {
    const portfolio = universe.portfolioSettings
    
    if (portfolio.minPositions > portfolio.maxPositions) {
      errors.push('최소 보유 종목 수가 최대 보유 종목 수보다 큽니다')
    }
    
    if (portfolio.minPositionSize > portfolio.maxPositionSize) {
      errors.push('최소 포지션 크기가 최대 포지션 크기보다 큽니다')
    }
    
    if (portfolio.cashBuffer < 0 || portfolio.cashBuffer > 100) {
      warnings.push('현금 보유 비율이 0-100% 범위를 벗어났습니다')
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  }
}

// 전체 전략 데이터 검증
export function validateStrategyData(strategyData: any): ValidationResult {
  const errors: string[] = []
  const warnings: string[] = []

  // 기본 정보 검증
  if (!strategyData.name || strategyData.name.trim() === '') {
    errors.push('전략 이름이 필요합니다')
  }

  // 단계별 전략 사용 시 검증
  if (strategyData.useStageBasedStrategy) {
    // 매수 단계 전략 검증
    if (strategyData.buyStageStrategy) {
      const buyValidation = validateStageStrategy(strategyData.buyStageStrategy)
      errors.push(...buyValidation.errors.map(e => `매수 전략: ${e}`))
      warnings.push(...buyValidation.warnings.map(w => `매수 전략: ${w}`))
    }

    // 매도 단계 전략 검증
    if (strategyData.sellStageStrategy) {
      const sellValidation = validateStageStrategy(strategyData.sellStageStrategy)
      errors.push(...sellValidation.errors.map(e => `매도 전략: ${e}`))
      warnings.push(...sellValidation.warnings.map(w => `매도 전략: ${w}`))
    }
  } else {
    // 기본 전략 검증
    if (!strategyData.buyConditions || strategyData.buyConditions.length === 0) {
      warnings.push('매수 조건이 설정되지 않았습니다')
    }
    
    if (!strategyData.sellConditions || strategyData.sellConditions.length === 0) {
      warnings.push('매도 조건이 설정되지 않았습니다')
    }
  }

  // 투자 유니버스 검증
  if (strategyData.investmentUniverse) {
    const universeValidation = validateInvestmentUniverse(strategyData.investmentUniverse)
    errors.push(...universeValidation.errors)
    warnings.push(...universeValidation.warnings)
  }

  // 리스크 관리 검증
  if (strategyData.riskManagement) {
    const risk = strategyData.riskManagement
    
    if (risk.stopLoss > 0) {
      warnings.push('손절매 값이 양수입니다. 일반적으로 음수를 사용합니다')
    }
    
    if (risk.takeProfit < 0) {
      warnings.push('익절매 값이 음수입니다. 일반적으로 양수를 사용합니다')
    }
    
    if (risk.positionSize > 100) {
      errors.push('포지션 크기가 100%를 초과합니다')
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  }
}

// Supabase 저장 전 데이터 정리
export function prepareStrategyForSave(strategyData: any): any {
  // 깊은 복사
  const cleaned = JSON.parse(JSON.stringify(strategyData))

  // undefined 값을 null로 변환
  function cleanUndefined(obj: any): any {
    if (obj === undefined) return null
    if (obj === null) return null
    if (typeof obj !== 'object') return obj
    if (Array.isArray(obj)) {
      return obj.map(cleanUndefined)
    }
    
    const result: any = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        result[key] = cleanUndefined(obj[key])
      }
    }
    return result
  }

  return cleanUndefined(cleaned)
}

// JSONB 필드 크기 확인
export function checkJsonSize(data: any): { size: number; sizeInKB: number; isValid: boolean } {
  const jsonString = JSON.stringify(data)
  const size = new Blob([jsonString]).size
  const sizeInKB = size / 1024
  
  // PostgreSQL JSONB 최대 크기는 약 1GB이지만, 실용적으로 1MB 이하 권장
  const isValid = sizeInKB < 1024

  return {
    size,
    sizeInKB: Math.round(sizeInKB * 100) / 100,
    isValid
  }
}

// 전략 데이터 요약 생성
export function generateStrategySummary(strategyData: any): string {
  const parts = []

  // 기본 정보
  parts.push(`전략명: ${strategyData.name || '이름 없음'}`)
  
  // 전략 타입
  if (strategyData.useStageBasedStrategy) {
    parts.push('타입: 3단계 전략')
    
    // 단계별 정보
    if (strategyData.buyStageStrategy?.stages) {
      const activeStages = strategyData.buyStageStrategy.stages.filter((s: any) => s.enabled)
      parts.push(`매수 단계: ${activeStages.length}개 활성`)
    }
    if (strategyData.sellStageStrategy?.stages) {
      const activeStages = strategyData.sellStageStrategy.stages.filter((s: any) => s.enabled)
      parts.push(`매도 단계: ${activeStages.length}개 활성`)
    }
  } else {
    parts.push('타입: 기본 전략')
    parts.push(`매수 조건: ${strategyData.buyConditions?.length || 0}개`)
    parts.push(`매도 조건: ${strategyData.sellConditions?.length || 0}개`)
  }

  // 투자 유니버스
  if (strategyData.investmentUniverse) {
    const universe = strategyData.investmentUniverse
    if (universe.financialFilters) {
      parts.push('재무 필터: 설정됨')
    }
    if (universe.sectorFilters?.include?.length > 0) {
      parts.push(`포함 섹터: ${universe.sectorFilters.include.length}개`)
    }
  }

  // 리스크 관리
  if (strategyData.riskManagement) {
    const risk = strategyData.riskManagement
    parts.push(`손절: ${risk.stopLoss}%, 익절: ${risk.takeProfit}%`)
  }

  return parts.join(' | ')
}