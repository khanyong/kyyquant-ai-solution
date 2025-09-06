// 투자 설정 및 전략 타입 정의

export interface FinancialFilters {
  marketCap: [number, number]      // 시가총액 범위 (억원)
  per: [number, number]            // PER 범위
  pbr: [number, number]            // PBR 범위
  roe: [number, number]            // ROE 범위 (%)
  debtRatio: [number, number]      // 부채비율 범위 (%)
  tradingVolume: [number, number]  // 거래대금 범위 (백만원)
}

export interface SectorFilters {
  include: string[]                // 포함 섹터
  exclude: string[]                // 제외 섹터
  sectorWeights?: { [key: string]: number }  // 섹터별 가중치
}

export interface InvestmentUniverse {
  financialFilters: FinancialFilters
  sectorFilters: SectorFilters
  stockList?: string[]            // 필터링된 종목 리스트
  lastUpdated?: Date              // 마지막 업데이트 시간
}

export interface TradingStrategy {
  id: string
  name: string
  description: string
  indicators: any[]               // 기술적 지표
  buyConditions: any[]           // 매수 조건
  sellConditions: any[]          // 매도 조건
  riskManagement: any            // 리스크 관리
}

export enum InvestmentFlowType {
  FILTER_FIRST = 'filter_first',   // 흐름 1: 필터 우선
  STRATEGY_FIRST = 'strategy_first' // 흐름 2: 전략 우선
}

export interface InvestmentFlow {
  type: InvestmentFlowType
  universe?: InvestmentUniverse    // 투자 유니버스
  strategy?: TradingStrategy        // 매매 전략
  enabled: boolean
  priority: number                  // 우선순위 (복수 전략 실행 시)
}

export interface TradingSignal {
  stockCode: string
  stockName: string
  signalType: 'buy' | 'sell'
  strategy: string                 // 전략명
  flowType: InvestmentFlowType    // 어떤 흐름에서 발생
  passedFilters: boolean           // 필터 통과 여부
  filterResults?: {
    marketCap?: boolean
    per?: boolean
    pbr?: boolean
    roe?: boolean
    debtRatio?: boolean
    sector?: boolean
  }
  confidence: number               // 신호 신뢰도 (0-100)
  timestamp: Date
}

export interface InvestmentConfig {
  flows: InvestmentFlow[]          // 활성화된 투자 흐름들
  universe: InvestmentUniverse     // 전체 투자 유니버스
  strategies: TradingStrategy[]    // 전체 전략 목록
  activeMode: InvestmentFlowType   // 현재 활성 모드
}