/**
 * 자동매매 전략 엔진
 * 설정된 조건에 따라 자동으로 주문을 실행
 */

import { store } from '../store'
import { placeOrder } from './api'
import { subscribeToStock } from './websocket'
import { Order, RealTimeData } from '../types'

// 자동매매 전략 타입
export interface TradingStrategy {
  id: string
  name: string
  enabled: boolean
  stockCode: string
  conditions: TradingCondition[]
  action: TradingAction
}

export interface TradingCondition {
  type: 'price_above' | 'price_below' | 'volume_above' | 'rsi' | 'ma_cross'
  value: number
  comparison?: 'greater' | 'less' | 'equal'
}

export interface TradingAction {
  type: 'buy' | 'sell'
  quantity: number
  orderMethod: 'limit' | 'market'
  priceOffset?: number // 지정가 주문시 현재가 대비 오프셋
}

// 활성화된 전략들
const activeStrategies = new Map<string, TradingStrategy>()

// 전략 실행 히스토리
const executionHistory: Array<{
  strategyId: string
  timestamp: Date
  action: string
  result: 'success' | 'failed'
}> = []

/**
 * 자동매매 전략 등록
 */
export const registerStrategy = (strategy: TradingStrategy) => {
  if (strategy.enabled) {
    activeStrategies.set(strategy.id, strategy)
    // 해당 종목 실시간 데이터 구독
    subscribeToStock(strategy.stockCode)
    console.log(`Strategy registered: ${strategy.name}`)
  }
}

/**
 * 자동매매 전략 해제
 */
export const unregisterStrategy = (strategyId: string) => {
  activeStrategies.delete(strategyId)
  console.log(`Strategy unregistered: ${strategyId}`)
}

/**
 * 조건 검사
 */
const checkCondition = (condition: TradingCondition, data: RealTimeData): boolean => {
  switch (condition.type) {
    case 'price_above':
      return data.price > condition.value
    
    case 'price_below':
      return data.price < condition.value
    
    case 'volume_above':
      return data.totalVolume > condition.value
    
    // RSI, 이동평균선 교차 등 추가 지표는 별도 계산 필요
    default:
      return false
  }
}

/**
 * 전략 실행
 */
const executeStrategy = async (strategy: TradingStrategy, data: RealTimeData) => {
  const state = store.getState()
  const { selectedAccount } = state.auth
  
  if (!selectedAccount) {
    console.error('No account selected for auto trading')
    return
  }

  // 모든 조건 확인
  const allConditionsMet = strategy.conditions.every(condition => 
    checkCondition(condition, data)
  )

  if (!allConditionsMet) {
    return
  }

  console.log(`Executing strategy: ${strategy.name}`)

  // 주문 생성
  const order: Order = {
    accountNo: selectedAccount,
    stockCode: strategy.stockCode,
    orderType: strategy.action.type,
    quantity: strategy.action.quantity,
    price: strategy.action.orderMethod === 'limit' 
      ? data.price + (strategy.action.priceOffset || 0)
      : 0,
    orderMethod: strategy.action.orderMethod,
  }

  try {
    // 주문 실행
    const response = await placeOrder(order)
    
    if (response.success) {
      executionHistory.push({
        strategyId: strategy.id,
        timestamp: new Date(),
        action: `${strategy.action.type} ${strategy.action.quantity} shares`,
        result: 'success'
      })
      
      // 전략 자동 비활성화 (중복 실행 방지)
      strategy.enabled = false
      
      console.log(`Strategy executed successfully: ${strategy.name}`)
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    executionHistory.push({
      strategyId: strategy.id,
      timestamp: new Date(),
      action: `Failed: ${strategy.action.type}`,
      result: 'failed'
    })
    console.error(`Strategy execution failed: ${error}`)
  }
}

/**
 * 실시간 데이터 모니터링 및 전략 실행
 */
export const monitorAndExecute = () => {
  // Redux store 구독
  store.subscribe(() => {
    const state = store.getState()
    const { realTimeData } = state.market
    
    // 각 종목별 실시간 데이터 확인
    Object.entries(realTimeData).forEach(([stockCode, data]) => {
      // 해당 종목에 대한 활성 전략들 확인
      activeStrategies.forEach(strategy => {
        if (strategy.stockCode === stockCode && strategy.enabled) {
          executeStrategy(strategy, data)
        }
      })
    })
  })
}

/**
 * 예제 전략들
 */
export const exampleStrategies: TradingStrategy[] = [
  {
    id: 'strategy_1',
    name: '삼성전자 저가 매수',
    enabled: true,
    stockCode: '005930',
    conditions: [
      { type: 'price_below', value: 70000 },
      { type: 'volume_above', value: 1000000 }
    ],
    action: {
      type: 'buy',
      quantity: 10,
      orderMethod: 'limit',
      priceOffset: 100 // 현재가보다 100원 높게 지정가
    }
  },
  {
    id: 'strategy_2',
    name: '손절 전략',
    enabled: true,
    stockCode: '005930',
    conditions: [
      { type: 'price_below', value: 65000 } // 손절가
    ],
    action: {
      type: 'sell',
      quantity: 10,
      orderMethod: 'market' // 시장가 즉시 매도
    }
  },
  {
    id: 'strategy_3',
    name: '목표가 도달 매도',
    enabled: true,
    stockCode: '005930',
    conditions: [
      { type: 'price_above', value: 80000 } // 목표가
    ],
    action: {
      type: 'sell',
      quantity: 5,
      orderMethod: 'limit',
      priceOffset: -100 // 현재가보다 100원 낮게 지정가
    }
  }
]

// 자동매매 시작
export const startAutoTrading = () => {
  console.log('Auto trading started')
  monitorAndExecute()
  
  // 예제 전략들 등록
  exampleStrategies.forEach(strategy => {
    registerStrategy(strategy)
  })
}

// 자동매매 중지
export const stopAutoTrading = () => {
  console.log('Auto trading stopped')
  activeStrategies.clear()
}

// 실행 히스토리 조회
export const getExecutionHistory = () => {
  return executionHistory
}