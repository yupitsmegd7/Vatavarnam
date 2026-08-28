import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],

  server: {
    host: '0.0.0.0',
    allowedHosts: ['vatavarnam-1.onrender.com'],

    proxy: {
      '/api': {
        target: 'https://vatavarnam-api.onrender.com',
        changeOrigin: true,
      },
    },
  },
});
