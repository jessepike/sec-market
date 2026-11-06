import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Onboarding suppliers render on Vercel preview builds only (D-138).
  define: { __SMP_SHOW_ONBOARDING__: JSON.stringify(process.env.VERCEL_ENV === 'preview') },
})
