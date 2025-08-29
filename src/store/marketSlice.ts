import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { Stock, RealTimeData, MarketIndex } from '../types'

interface MarketState {
  selectedStock: Stock | null
  watchlist: Stock[]
  realTimeData: Record<string, RealTimeData>
  marketIndices: MarketIndex[]
}

const initialState: MarketState = {
  selectedStock: null,
  watchlist: [],
  realTimeData: {},
  marketIndices: [],
}

const marketSlice = createSlice({
  name: 'market',
  initialState,
  reducers: {
    selectStock: (state, action: PayloadAction<Stock>) => {
      state.selectedStock = action.payload
    },
    addToWatchlist: (state, action: PayloadAction<Stock>) => {
      if (!state.watchlist.find(s => s.code === action.payload.code)) {
        state.watchlist.push(action.payload)
      }
    },
    removeFromWatchlist: (state, action: PayloadAction<string>) => {
      state.watchlist = state.watchlist.filter(s => s.code !== action.payload)
    },
    updateRealTimeData: (state, action: PayloadAction<RealTimeData>) => {
      state.realTimeData[action.payload.code] = action.payload
    },
    updateMarketIndices: (state, action: PayloadAction<MarketIndex[]>) => {
      state.marketIndices = action.payload
    },
  },
})

export const { 
  selectStock, 
  addToWatchlist, 
  removeFromWatchlist, 
  updateRealTimeData,
  updateMarketIndices 
} = marketSlice.actions
export default marketSlice.reducer