import { store } from '../store'
import { updateRealTimeData } from '../store/marketSlice'
import { RealTimeData } from '../types'

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let pingInterval: ReturnType<typeof setInterval> | null = null

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

export const connectWebSocket = () => {
  if (ws?.readyState === WebSocket.OPEN) {
    return
  }

  ws = new WebSocket(WS_URL)

  ws.onopen = () => {
    console.log('WebSocket connected')
    
    // Start ping interval
    pingInterval = setInterval(() => {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    } catch (error) {
      console.error('WebSocket message parse error:', error)
    }
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }

  ws.onclose = () => {
    console.log('WebSocket disconnected')
    
    // Clear ping interval
    if (pingInterval) {
      clearInterval(pingInterval)
      pingInterval = null
    }

    // Attempt to reconnect after 5 seconds
    if (!reconnectTimer) {
      reconnectTimer = setTimeout(() => {
        reconnectTimer = null
        connectWebSocket()
      }, 5000)
    }
  }
}

export const disconnectWebSocket = () => {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }

  if (pingInterval) {
    clearInterval(pingInterval)
    pingInterval = null
  }

  if (ws) {
    ws.close()
    ws = null
  }
}

const handleWebSocketMessage = (data: any) => {
  switch (data.type) {
    case 'real_data':
      const realTimeData: RealTimeData = {
        code: data.data.code,
        time: data.data.time,
        price: data.data.price,
        change: data.data.change,
        changeRate: data.data.changeRate,
        volume: data.data.volume,
        totalVolume: data.data.totalVolume,
      }
      store.dispatch(updateRealTimeData(realTimeData))
      break

    case 'subscribed':
      console.log(`Subscribed to ${data.stock_code}`)
      break

    case 'unsubscribed':
      console.log(`Unsubscribed from ${data.stock_code}`)
      break

    case 'pong':
      // Server acknowledged ping
      break

    default:
      console.log('Unknown message type:', data.type)
  }
}

export const subscribeToStock = (stockCode: string) => {
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: 'subscribe',
      stock_code: stockCode,
    }))
  }
}

export const unsubscribeFromStock = (stockCode: string) => {
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: 'unsubscribe',
      stock_code: stockCode,
    }))
  }
}

export const getWebSocketStatus = (): 'connected' | 'disconnected' | 'connecting' => {
  if (!ws) return 'disconnected'
  
  switch (ws.readyState) {
    case WebSocket.OPEN:
      return 'connected'
    case WebSocket.CONNECTING:
      return 'connecting'
    default:
      return 'disconnected'
  }
}