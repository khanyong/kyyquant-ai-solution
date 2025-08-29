import { configureStore } from '@reduxjs/toolkit'
import authReducer from './authSlice'
import marketReducer from './marketSlice'
import portfolioReducer from './portfolioSlice'
import orderReducer from './orderSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    market: marketReducer,
    portfolio: portfolioReducer,
    order: orderReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch