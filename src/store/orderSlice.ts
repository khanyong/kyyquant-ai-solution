import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { Order } from '../types'

interface OrderState {
  pendingOrders: Order[]
  orderHistory: Order[]
  loading: boolean
  error: string | null
}

const initialState: OrderState = {
  pendingOrders: [],
  orderHistory: [],
  loading: false,
  error: null,
}

const orderSlice = createSlice({
  name: 'order',
  initialState,
  reducers: {
    addPendingOrder: (state, action: PayloadAction<Order>) => {
      state.pendingOrders.push(action.payload)
    },
    removePendingOrder: (state, action: PayloadAction<number>) => {
      state.pendingOrders.splice(action.payload, 1)
    },
    addToHistory: (state, action: PayloadAction<Order>) => {
      state.orderHistory.unshift(action.payload)
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
  },
})

export const { 
  addPendingOrder, 
  removePendingOrder, 
  addToHistory,
  setLoading,
  setError 
} = orderSlice.actions
export default orderSlice.reducer