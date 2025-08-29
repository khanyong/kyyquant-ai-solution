export interface User {
  id: string
  name: string
  accounts: string[]
}

export interface Stock {
  code: string
  name: string
  price: number
  change: number
  changeRate: number
  volume: number
}

export interface Portfolio {
  stockCode: string
  stockName: string
  quantity: number
  avgPrice: number
  currentPrice: number
  profitLoss: number
  profitLossRate: number
}

export interface Order {
  accountNo: string
  stockCode: string
  orderType: 'buy' | 'sell'
  quantity: number
  price: number
  orderMethod: 'limit' | 'market'
}

export interface RealTimeData {
  code: string
  time: string
  price: number
  change: number
  changeRate: number
  volume: number
  totalVolume: number
}

export interface ChartData {
  time: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface MarketIndex {
  name: string
  value: number
  change: number
  changeRate: number
}