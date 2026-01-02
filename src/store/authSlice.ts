import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { User } from '../types'

interface AuthState {
  isConnected: boolean
  user: User | null
  accounts: string[]
  selectedAccount: string | null
  tradingMode: 'live' | 'test' // [NEW] Track Mode
}

const initialState: AuthState = {
  isConnected: false,
  user: null,
  accounts: [],
  selectedAccount: null,
  tradingMode: 'live' // Default
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginSuccess: (state, action: PayloadAction<{ user: User; accounts: string[]; tradingMode?: 'live' | 'test' }>) => {
      state.isConnected = true
      state.user = action.payload.user
      state.accounts = action.payload.accounts
      state.selectedAccount = action.payload.accounts[0] || null
      if (action.payload.tradingMode) {
        state.tradingMode = action.payload.tradingMode
      }
    },
    logout: (state) => {
      state.isConnected = false
      state.user = null
      state.accounts = []
      state.selectedAccount = null
      state.tradingMode = 'live'
    },
    selectAccount: (state, action: PayloadAction<string>) => {
      state.selectedAccount = action.payload
    },
    setTradingMode: (state, action: PayloadAction<'live' | 'test'>) => {
      state.tradingMode = action.payload
    }
  },
})

export const { loginSuccess, logout, selectAccount, setTradingMode } = authSlice.actions
export default authSlice.reducer