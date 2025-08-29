import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import AppQuant from './AppQuant'
import { store } from './store'
import './index.css'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#0a0e27',
      paper: '#1e1e2e',
    },
  },
  typography: {
    fontFamily: '"Pretendard", "Noto Sans KR", "Roboto", sans-serif',
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <AppQuant />
      </ThemeProvider>
    </Provider>
  </React.StrictMode>,
)