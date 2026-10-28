import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const backendPort = process.env.BACKEND_PORT || env.BACKEND_PORT || '8300';
  const frontendPort = process.env.FRONTEND_PORT || env.FRONTEND_PORT || '3300';

  return {
    plugins: [react()],
    server: {
      host: '127.0.0.1',
      port: parseInt(frontendPort, 10),
      proxy: {
        '/api': {
          target: `http://127.0.0.1:${backendPort}`,
          changeOrigin: true,
        }
      }
    },
  };
});


