import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    // 청크 크기 경고 임계값 조정 (KB)
    chunkSizeWarningLimit: 1000,

    // 압축 최적화 - terser 비활성화하여 문제 해결
    minify: 'esbuild',
    target: 'es2015',

    // 코드 스플리팅 최적화
    rollupOptions: {
      output: {
        manualChunks: {
          // React 코어
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],

          // Redux
          'vendor-redux': ['@reduxjs/toolkit', 'react-redux'],

          // UI 라이브러리
          'vendor-mui': [
            '@mui/material',
            '@mui/icons-material',
            '@emotion/react',
            '@emotion/styled'
          ],

          // 차트 라이브러리
          'vendor-charts': ['lightweight-charts'],

          // Supabase
          'vendor-supabase': ['@supabase/supabase-js']
        }
      }
    }
  },
  
})