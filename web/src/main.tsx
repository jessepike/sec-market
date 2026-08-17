import { StrictMode } from 'react'
import { createRoot, hydrateRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

const container = document.getElementById('root')!

const app = (
  <StrictMode>
    <App />
  </StrictMode>
)

// Production builds are prerendered by scripts/prerender.ts, so #root already
// holds server-rendered markup and we hydrate it. `vite dev` serves the bare
// index.html with an empty #root, so we mount fresh instead.
if (container.firstChild) {
  hydrateRoot(container, app)
} else {
  createRoot(container).render(app)
}
