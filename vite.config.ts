import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// During local dev, proxy /api/* to the FastAPI service on :8000 so the
// frontend and backend share an origin (mirrors Vercel's production routing).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
