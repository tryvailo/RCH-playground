import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000, // Frontend on port 3000
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:3001', // Backend on port 3001
        changeOrigin: true,
        timeout: 300000, // 5 minutes timeout for long-running requests (professional report generation)
        proxyTimeout: 300000,
      },
      '/health': {
        target: 'http://127.0.0.1:3001', // Backend on port 3001
        changeOrigin: true,
      },
      '/ws': {
        target: 'http://127.0.0.1:3001', // Backend on port 3001
        ws: true,
        changeOrigin: true,
        secure: false,
      },
    },
  },
})

