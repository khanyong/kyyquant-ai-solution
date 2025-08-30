/**
 * Supabase Realtime 서비스
 * WebSocket 대신 Supabase의 Realtime 기능을 사용
 */

import { supabase } from './supabase'
import { store } from '../store'
import { updateRealTimeData } from '../store/marketSlice'
import { RealTimeData } from '../types'
import { RealtimeChannel } from '@supabase/supabase-js'

let channels: Map<string, RealtimeChannel> = new Map()

/**
 * Supabase Realtime 채널 구독
 */
export const subscribeToRealtime = (channelName: string = 'market-data') => {
  // 이미 구독 중인 채널이면 중복 구독하지 않음
  if (channels.has(channelName)) {
    console.log(`Already subscribed to channel: ${channelName}`)
    return
  }

  const channel = supabase
    .channel(channelName)
    .on('broadcast', { event: 'real_data' }, (payload) => {
      handleRealtimeMessage(payload.payload)
    })
    .on('broadcast', { event: 'price_update' }, (payload) => {
      handlePriceUpdate(payload.payload)
    })
    .subscribe((status) => {
      console.log(`Realtime subscription status for ${channelName}:`, status)
    })

  channels.set(channelName, channel)
}

/**
 * 특정 주식 데이터 구독
 */
export const subscribeToStock = (stockCode: string) => {
  const channelName = `stock-${stockCode}`
  
  if (channels.has(channelName)) {
    console.log(`Already subscribed to stock: ${stockCode}`)
    return
  }

  const channel = supabase
    .channel(channelName)
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'real_time_prices',
      filter: `stock_code=eq.${stockCode}`
    }, (payload) => {
      handleDatabaseChange(payload)
    })
    .subscribe()

  channels.set(channelName, channel)
  console.log(`Subscribed to stock: ${stockCode}`)
}

/**
 * 주식 구독 해제
 */
export const unsubscribeFromStock = (stockCode: string) => {
  const channelName = `stock-${stockCode}`
  const channel = channels.get(channelName)
  
  if (channel) {
    supabase.removeChannel(channel)
    channels.delete(channelName)
    console.log(`Unsubscribed from stock: ${stockCode}`)
  }
}

/**
 * 모든 Realtime 연결 해제
 */
export const disconnectRealtime = () => {
  channels.forEach((channel) => {
    supabase.removeChannel(channel)
  })
  channels.clear()
  console.log('All realtime connections closed')
}

/**
 * Realtime 메시지 처리
 */
const handleRealtimeMessage = (data: any) => {
  if (data.type === 'real_data') {
    const realTimeData: RealTimeData = {
      code: data.code,
      time: data.time,
      price: data.price,
      change: data.change,
      changeRate: data.changeRate,
      volume: data.volume,
      totalVolume: data.totalVolume,
    }
    store.dispatch(updateRealTimeData(realTimeData))
  }
}

/**
 * 가격 업데이트 처리
 */
const handlePriceUpdate = (data: any) => {
  const realTimeData: RealTimeData = {
    code: data.stock_code,
    time: new Date().toISOString(),
    price: data.current_price,
    change: data.price_change,
    changeRate: data.change_rate,
    volume: data.volume || 0,
    totalVolume: data.total_volume || 0,
  }
  store.dispatch(updateRealTimeData(realTimeData))
}

/**
 * 데이터베이스 변경 처리
 */
const handleDatabaseChange = (payload: any) => {
  console.log('Database change:', payload)
  
  if (payload.new) {
    const data = payload.new
    const realTimeData: RealTimeData = {
      code: data.stock_code,
      time: data.timestamp,
      price: data.price,
      change: data.change,
      changeRate: data.change_rate,
      volume: data.volume,
      totalVolume: data.total_volume,
    }
    store.dispatch(updateRealTimeData(realTimeData))
  }
}

/**
 * Realtime 연결 상태 확인
 */
export const getRealtimeStatus = (): 'connected' | 'disconnected' => {
  return channels.size > 0 ? 'connected' : 'disconnected'
}

/**
 * 커뮤니티 게시판 실시간 업데이트 구독
 */
export const subscribeToCommunityUpdates = (onUpdate: (payload: any) => void) => {
  const channel = supabase
    .channel('community-updates')
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'posts'
    }, onUpdate)
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'comments'
    }, onUpdate)
    .subscribe()

  channels.set('community-updates', channel)
  return channel
}