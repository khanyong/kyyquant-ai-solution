import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { User } from '../types'

interface AuthState {
  isConnected: boolean
  user: User | null
  accounts: string[]
  selectedAccount: string | null
}

const initialState: AuthState = {
  isConnected: false,
  user: null,
  accounts: [],
  selectedAccount: null,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginSuccess: (state, action: PayloadAction<{ user: User; accounts: string[] }>) => {
      state.isConnected = true
      state.user = action.payload.user
      state.accounts = action.payload.accounts
      state.selectedAccount = action.payload.accounts[0] || null
    },
    logout: (state) => {
      state.isConnected = false
      state.user = null
      state.accounts = []
      state.selectedAccount = null
    },
    selectAccount: (state, action: PayloadAction<string>) => {
      state.selectedAccount = action.payload
    },
  },
})

export const { loginSuccess, logout, selectAccount } = authSlice.actions
export default authSlice.reducer