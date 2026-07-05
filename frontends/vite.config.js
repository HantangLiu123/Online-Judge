import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())

  console.log('proxy target:', env.VITE_API_TARGET)

  return {
    plugins: [
      vue(),
      vueDevTools(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {              // 👈 关键在这里
      proxy: {
        '/api': {
          target: env.VITE_API_TARGET,
          changeOrigin: true,
        },
      },
    },
  }
})
