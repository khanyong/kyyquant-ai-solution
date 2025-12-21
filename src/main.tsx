import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import App from './AppWithRouter'
import { store } from './store'
import { AuthProvider } from './contexts/AuthContext'
import './index.css'
import './styles/ipc-theme.css'
import './i18n/config'

const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#212121', // Grey 900
    },
    secondary: {
      main: '#757575', // Grey 600
    },
    background: {
      default: '#FFFFFF', // Pure White
      paper: '#FFFFFF',
    },
    text: {
      primary: '#000000', // Absolute Black
      secondary: '#616161', // Grey 700
    },
    divider: '#E0E0E0',
  },
  typography: {
    fontFamily: '"Pretendard Variable", system-ui, sans-serif',
    h1: { fontFamily: '"Playfair Display", serif', fontWeight: 700, letterSpacing: '-0.02em' },
    h2: { fontFamily: '"Playfair Display", serif', fontWeight: 700, letterSpacing: '-0.02em' },
    h3: { fontFamily: '"Playfair Display", serif', fontWeight: 700, letterSpacing: '-0.02em' },
    h4: { fontFamily: '"Pretendard Variable", sans-serif', fontWeight: 600, letterSpacing: '-0.01em', textTransform: 'uppercase' },
    h5: { fontFamily: '"Pretendard Variable", sans-serif', fontWeight: 600 },
    h6: { fontFamily: '"Pretendard Variable", sans-serif', fontWeight: 600 },
    body1: { fontFamily: '"Lora", serif', lineHeight: 1.6 }, /* Editorial body text */
    body2: { fontFamily: '"Pretendard Variable", sans-serif' }, /* UI text */
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#ffffff',
          color: '#212121',
          boxShadow: 'none',
          borderBottom: '1px solid #e0e0e0',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
          border: '1px solid #e0e0e0',
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none', // Disable dark mode gradient overlay
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          boxShadow: 'none',
          fontWeight: 600,
          '&:hover': {
            boxShadow: 'none',
          },
        },
        contained: {
          color: '#ffffff',
        }
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          fontWeight: 600,
        }
      }

    }
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <AuthProvider>
        <ThemeProvider theme={lightTheme}>
          <CssBaseline />
          <App />
        </ThemeProvider>
      </AuthProvider>
    </Provider>
  </React.StrictMode>,
)
