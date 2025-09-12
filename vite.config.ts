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
    
    rollupOptions: {
      output: {
        // 수동 청크 분할 설정
        manualChunks(id) {
          // node_modules 내부 패키지 분리
          if (id.includes('node_modules')) {
            // React 관련
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router')) {
              return 'react-vendor';
            }
            // MUI 관련
            if (id.includes('@mui')) {
              return 'mui-vendor';
            }
            // 차트 라이브러리
            if (id.includes('recharts') || id.includes('lightweight-charts')) {
              return 'chart-vendor';
            }
            // Supabase
            if (id.includes('supabase')) {
              return 'supabase-vendor';
            }
            // 기타 유틸리티
            if (id.includes('date-fns') || id.includes('lodash')) {
              return 'utils-vendor';
            }
          }
        }
      }
    },
    
    // 압축 최적화
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 프로덕션에서 console.log 제거
        drop_debugger: true
      }
    }
  },
  
  // 최적화 설정
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      '@mui/material',
      '@mui/icons-material',
      'recharts',
      '@supabase/supabase-js'
    ]
  }
})