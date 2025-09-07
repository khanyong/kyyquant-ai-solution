// 필터링 모드 관련 타입 정의
export interface FilterRules {
  valuation?: {
    marketCap?: [number, number]
    per?: [number, number]
    pbr?: [number, number]
    pcr?: [number, number]
    psr?: [number, number]
    peg?: [number, number]
    eps?: [number, number]
    bps?: [number, number]
    currentPrice?: [number, number]
    priceToHigh52w?: [number, number]
    volume?: [number, number]
    foreignRatio?: [number, number]
  }
  financial?: {
    roe?: [number, number]
    roa?: [number, number]
    debtRatio?: [number, number]
    currentRatio?: [number, number]
    quickRatio?: [number, number]
    operatingMargin?: [number, number]
    netMargin?: [number, number]
    revenueGrowth?: [number, number]
    profitGrowth?: [number, number]
    equityGrowth?: [number, number]
    dividendYield?: [number, number]
    dividendPayout?: [number, number]
  }
  sector?: {
    include?: string[]
    exclude?: string[]
  }
  investor?: {  // 투자자 동향 필터 추가
    foreignHoldingRatio?: [number, number]      // 외국인 보유비율 (%)
    institutionHoldingRatio?: [number, number]  // 기관 보유비율 (%)
    foreignNetBuyDays?: number                  // 외국인 순매수 일수 (최근 N일)
    institutionNetBuyDays?: number              // 기관 순매수 일수 (최근 N일)
    foreignNetBuyAmount?: [number, number]      // 외국인 순매수 금액 (억원)
    institutionNetBuyAmount?: [number, number]  // 기관 순매수 금액 (억원)
    trendDirection?: 'buying' | 'selling' | 'both'  // 매수/매도 추세
    investorType?: ('foreign' | 'institution' | 'pension')[]  // 투자자 유형
    minConsecutiveBuyDays?: number              // 최소 연속 매수일
  }
  custom?: {
    [key: string]: any
  }
}

export type FilteringModeType = 'pre-filter' | 'post-filter' | 'hybrid'
export type RebalancePeriod = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'none'

export interface FilteringMode {
  mode: FilteringModeType
  preFilterRules?: FilterRules  // 사전 필터 규칙
  postFilterRules?: FilterRules  // 사후 필터 규칙
  hybridSettings?: {
    primaryFilter: FilterRules   // 1차 필터 (기본 스크리닝)
    secondaryFilter: FilterRules // 2차 필터 (시그널 후 검증)
  }
  dynamicRebalance: boolean      // 동적 리밸런싱 여부
  rebalancePeriod: RebalancePeriod
  filterPriority: {
    required: string[]   // 필수 통과 필터
    preferred: string[]  // 선호 필터 (가중치 부여)
    excluded: string[]   // 제외 필터 (블랙리스트)
  }
  filterId?: string  // 사전 필터링 모드에서 사용할 필터 ID
  stockCodes?: string[]  // 사전 필터링 모드에서 사용할 종목 코드 리스트
}

export interface FilteringResult {
  totalStocks: number
  filteredStocks: number
  passedStocks: string[]
  failedStocks: string[]
  filterStats: {
    [filterName: string]: {
      passed: number
      failed: number
      passRate: number
    }
  }
}

export interface FilteringStrategy {
  id: string
  name: string
  description: string
  mode: FilteringMode
  createdAt: Date
  updatedAt: Date
  isActive: boolean
  performance?: {
    backtestCount: number
    avgReturn: number
    avgSharpe: number
    avgMaxDrawdown: number
  }
}

// 필터링 모드별 설명
export const FILTERING_MODE_DESCRIPTIONS = {
  'pre-filter': {
    title: '사전 필터링 (Pre-Filter)',
    description: '백테스트 시작 전 유니버스를 필터링하여 선정된 종목만 전략 적용',
    pros: ['빠른 백테스트 속도', '적은 메모리 사용', '명확한 투자 대상'],
    cons: ['잠재적 기회 놓칠 가능성', '정적인 유니버스'],
    useCase: '명확한 투자 기준이 있는 경우 (예: 대형주만, 특정 섹터만)'
  },
  'post-filter': {
    title: '사후 필터링 (Post-Filter)',
    description: '전체 종목에 전략을 적용한 후 시그널 발생 시 필터 체크',
    pros: ['더 많은 기회 포착', '동적 필터링 가능', '유연한 전략'],
    cons: ['느린 백테스트 속도', '많은 메모리 사용'],
    useCase: '전략 우선, 필터는 리스크 관리용'
  },
  'hybrid': {
    title: '하이브리드 모드 (Hybrid)',
    description: '기본 필터로 1차 스크리닝 후 전략 적용, 시그널 시 2차 검증',
    pros: ['균형잡힌 성능', '유연한 필터링', '단계별 검증'],
    cons: ['복잡한 설정', '중간 수준의 속도'],
    useCase: '기본 조건 + 추가 검증이 필요한 경우'
  }
}