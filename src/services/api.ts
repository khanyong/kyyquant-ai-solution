import axios from 'axios'
import { User, Stock, Portfolio, Order } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Server status
export const checkServerStatus = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health')
    return response.data.status === 'healthy'
  } catch {
    return false
  }
}

// Auth APIs
export const login = async (accountNo?: string, password?: string, demoMode = true) => {
  const response = await api.post('/api/login', {
    account_no: accountNo,
    password,
    demo_mode: demoMode,
  })
  return response.data
}

export const getAccounts = async () => {
  const response = await api.get('/api/accounts')
  return response.data.accounts
}

// Portfolio APIs
export const getBalance = async (accountNo: string): Promise<Portfolio[]> => {
  const response = await api.get('/api/account/holdings', {
    params: {
      account_no: accountNo,
    }
  })
  return response.data.holdings || response.data
}

// Stock APIs
export const getStockInfo = async (stockCode: string): Promise<Stock> => {
  const response = await api.post('/api/stock-info', {
    stock_code: stockCode,
  })
  return response.data
}

export const getMarketStocks = async (market: 'KOSPI' | 'KOSDAQ', limit = 50) => {
  const response = await api.get(`/api/markets/${market}/stocks`, {
    params: { limit },
  })
  return response.data.stocks
}

// Order APIs
export const placeOrder = async (order: Order) => {
  const response = await api.post('/api/order', {
    account_no: order.accountNo,
    stock_code: order.stockCode,
    order_type: order.orderType,
    quantity: order.quantity,
    price: order.price,
    order_method: order.orderMethod,
  })
  return response.data
}

export default api