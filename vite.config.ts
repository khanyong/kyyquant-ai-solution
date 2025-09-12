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
    chunkSizeWarningLimit: 1500,
    
    // 압축 최적화 - terser 비활성화하여 문제 해결
    minify: 'esbuild',
    target: 'es2015'
  },
  
})