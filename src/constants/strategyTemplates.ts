// 전략 템플릿 정의
// StrategyBuilder와 BacktestRunner에서 공통으로 사용

export interface StrategyTemplate {
  id: string
  name: string
  description: string
  type: 'basic' | 'complex'  // 기본 전략 or 3단계 복합 전략
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  icon: string
  iconColor: 'success' | 'warning' | 'error' | 'info' | 'primary' | 'secondary'
  // 기본 전략 설정
  strategy?: {
    indicators: any[]
    buyConditions: any[]
    sellConditions: any[]
    riskManagement?: any
  }
  // 3단계 전략 설정
  stageStrategy?: {
    buyStages: any
    sellStages: any
  }
}

export const STRATEGY_TEMPLATES: StrategyTemplate[] = [
  {
    id: 'golden-cross',
    name: '[템플릿] 골든크로스',
    description: 'MA20이 MA60을 상향 돌파할 때 매수',
    type: 'basic',
    difficulty: 'beginner',
    icon: 'TrendingUp',
    iconColor: 'success',
    strategy: {
      indicators: [
        { type: 'ma', params: { period: 20 } },
        { type: 'ma', params: { period: 60 } }
      ],
      buyConditions: [
        { id: '1', type: 'buy', indicator: 'ma_20', operator: 'cross_above', value: 'ma_60', combineWith: 'AND' }
      ],
      sellConditions: [
        { id: '2', type: 'sell', indicator: 'ma_20', operator: 'cross_below', value: 'ma_60', combineWith: 'AND' }
      ]
    }
  },
  {
    id: 'rsi-reversal',
    name: '[템플릿] RSI 반전',
    description: 'RSI 과매도/과매수 구간 활용',
    type: 'basic',
    difficulty: 'beginner',
    icon: 'Autorenew',
    iconColor: 'secondary',
    strategy: {
      indicators: [
        { type: 'rsi', params: { period: 14 } }
      ],
      buyConditions: [
        { id: '1', type: 'buy', indicator: 'rsi_14', operator: '<', value: 30, combineWith: 'AND' }
      ],
      sellConditions: [
        { id: '2', type: 'sell', indicator: 'rsi_14', operator: '>', value: 70, combineWith: 'AND' }
      ]
    }
  },
  {
    id: 'bollinger-band',
    name: '[템플릿] 볼린저밴드',
    description: '밴드 하단 매수, 상단 매도',
    type: 'basic',
    difficulty: 'intermediate',
    icon: 'Timeline',
    iconColor: 'info',
    strategy: {
      indicators: [
        { type: 'bb', params: { period: 20, std: 2 } },
        { type: 'rsi', params: { period: 14 } }
      ],
      buyConditions: [
        { id: '1', type: 'buy', indicator: 'close', operator: '<', value: 'bb_lower_20_2', combineWith: 'AND' },
        { id: '2', type: 'buy', indicator: 'rsi_14', operator: '<', value: 40, combineWith: 'AND' }
      ],
      sellConditions: [
        { id: '3', type: 'sell', indicator: 'close', operator: '>', value: 'bb_upper_20_2', combineWith: 'AND' }
      ]
    }
  },
  {
    id: 'macd-signal',
    name: '[템플릿] MACD 시그널',
    description: 'MACD 골든/데드 크로스',
    type: 'basic',
    difficulty: 'intermediate',
    icon: 'ShowChart',
    iconColor: 'primary',
    strategy: {
      indicators: [
        { type: 'macd', params: { fast: 12, slow: 26, signal: 9 } }
      ],
      buyConditions: [
        { id: '1', type: 'buy', indicator: 'macd', operator: 'cross_above', value: 'macd_signal', combineWith: 'AND' },
        { id: '2', type: 'buy', indicator: 'macd', operator: '>', value: 0, combineWith: 'AND' }
      ],
      sellConditions: [
        { id: '3', type: 'sell', indicator: 'macd', operator: 'cross_below', value: 'macd_signal', combineWith: 'AND' }
      ]
    }
  },
  {
    id: 'complex-a',
    name: '[템플릿] 복합 전략 A',
    description: 'RSI → MACD → 거래량 3단계 검증',
    type: 'complex',
    difficulty: 'advanced',
    icon: 'AccountTree',
    iconColor: 'primary',
    stageStrategy: {
      buyStages: {
        stage1: {
          indicators: [{ type: 'rsi', period: 14 }],
          conditions: [
            { indicator: 'rsi_14', operator: '<', value: 35 }
          ]
        },
        stage2: {
          indicators: [{ type: 'macd', fast: 12, slow: 26, signal: 9 }],
          conditions: [
            { indicator: 'macd', operator: 'cross_above', value: 'macd_signal' }
          ]
        },
        stage3: {
          indicators: [{ type: 'ma', period: 20 }],
          conditions: [
            { indicator: 'volume', operator: '>', value: 'volume_ma_20' }
          ]
        }
      },
      sellStages: {
        stage1: {
          indicators: [{ type: 'rsi', period: 14 }],
          conditions: [
            { indicator: 'rsi_14', operator: '>', value: 70 }
          ]
        },
        stage2: {
          indicators: [{ type: 'macd', fast: 12, slow: 26, signal: 9 }],
          conditions: [
            { indicator: 'macd', operator: 'cross_below', value: 'macd_signal' }
          ]
        },
        stage3: {
          indicators: [],
          conditions: []
        }
      }
    }
  },
  {
    id: 'complex-b',
    name: '[템플릿] 복합 전략 B',
    description: '골든크로스 → 볼린저 → RSI 확인',
    type: 'complex',
    difficulty: 'advanced',
    icon: 'AccountTree',
    iconColor: 'secondary',
    stageStrategy: {
      buyStages: {
        stage1: {
          indicators: [{ type: 'ma', period: 20 }, { type: 'ma', period: 60 }],
          conditions: [
            { indicator: 'ma_20', operator: '>', value: 'ma_60' }
          ]
        },
        stage2: {
          indicators: [{ type: 'bb', period: 20, std_dev: 2 }],
          conditions: [
            { indicator: 'price', operator: '<', value: 'bb_middle' }
          ]
        },
        stage3: {
          indicators: [{ type: 'rsi', period: 14 }],
          conditions: [
            { indicator: 'rsi_14', operator: '<', value: 50 }
          ]
        }
      },
      sellStages: {
        stage1: {
          indicators: [{ type: 'ma', period: 20 }, { type: 'ma', period: 60 }],
          conditions: [
            { indicator: 'ma_20', operator: '<', value: 'ma_60' }
          ]
        },
        stage2: {
          indicators: [{ type: 'bb', period: 20, std_dev: 2 }],
          conditions: [
            { indicator: 'price', operator: '>', value: 'bb_upper' }
          ]
        },
        stage3: {
          indicators: [],
          conditions: []
        }
      }
    }
  },
  {
    id: 'scalping',
    name: '[템플릿] 스캘핑',
    description: '단기 빠른 진입/청산',
    type: 'basic',
    difficulty: 'expert',
    icon: 'Speed',
    iconColor: 'warning',
    strategy: {
      indicators: [
        { type: 'ma', period: 5 },
        { type: 'rsi', period: 9 }
      ],
      buyConditions: [
        { id: '1', type: 'buy', indicator: 'price', operator: '>', value: 'ma_5', combineWith: 'AND' },
        { id: '2', type: 'buy', indicator: 'rsi_9', operator: '<', value: 50, combineWith: 'AND' }
      ],
      sellConditions: [
        { id: '3', type: 'sell', indicator: 'rsi_9', operator: '>', value: 70, combineWith: 'AND' }
      ],
      riskManagement: {
        stopLoss: -2,
        takeProfit: 3,
        trailingStop: true,
        trailingStopPercent: 1,
        positionSize: 10,
        maxPositions: 3
      }
    }
  },
  {
    id: 'swing-trading',
    name: '[템플릿] 스윙 트레이딩',
    description: '중기 추세 포착',
    type: 'basic',
    difficulty: 'intermediate',
    icon: 'SwapHoriz',
    iconColor: 'info',
    strategy: {
      indicators: [
        { type: 'ma', period: 20 },
        { type: 'ma', period: 60 },
        { type: 'rsi', period: 14 },
        { type: 'macd', fast: 12, slow: 26, signal: 9 }
      ],
      buyConditions: [
        { id: '1', type: 'buy', indicator: 'ma_20', operator: '>', value: 'ma_60', combineWith: 'AND' },
        { id: '2', type: 'buy', indicator: 'rsi_14', operator: '<', value: 60, combineWith: 'AND' },
        { id: '3', type: 'buy', indicator: 'macd', operator: '>', value: 0, combineWith: 'AND' }
      ],
      sellConditions: [
        { id: '4', type: 'sell', indicator: 'ma_20', operator: '<', value: 'ma_60', combineWith: 'AND' },
        { id: '5', type: 'sell', indicator: 'rsi_14', operator: '>', value: 70, combineWith: 'AND' }
      ],
      riskManagement: {
        stopLoss: -7,
        takeProfit: 15,
        trailingStop: false,
        trailingStopPercent: 0,
        positionSize: 20,
        maxPositions: 5
      }
    }
  }
]

// 템플릿 ID로 찾기
export const getTemplateById = (id: string): StrategyTemplate | undefined => {
  return STRATEGY_TEMPLATES.find(t => t.id === id)
}

// 난이도별 필터링
export const getTemplatesByDifficulty = (difficulty: string): StrategyTemplate[] => {
  return STRATEGY_TEMPLATES.filter(t => t.difficulty === difficulty)
}

// 타입별 필터링
export const getTemplatesByType = (type: 'basic' | 'complex'): StrategyTemplate[] => {
  return STRATEGY_TEMPLATES.filter(t => t.type === type)
}