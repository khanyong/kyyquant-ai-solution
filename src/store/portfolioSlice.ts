import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { Portfolio } from '../types'

interface PortfolioState {
  holdings: Portfolio[]
  totalValue: number
  totalProfitLoss: number
  loading: boolean
}

const initialState: PortfolioState = {
  holdings: [],
  totalValue: 0,
  totalProfitLoss: 0,
  loading: false,
}

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    setPortfolio: (state, action: PayloadAction<Portfolio[]>) => {
      state.holdings = action.payload
      state.totalValue = action.payload.reduce((sum, p) => sum + p.currentPrice * p.quantity, 0)
      state.totalProfitLoss = action.payload.reduce((sum, p) => sum + p.profitLoss, 0)
      state.loading = false
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
  },
})

export const { setPortfolio, setLoading } = portfolioSlice.actions
export default portfolioSlice.reducer