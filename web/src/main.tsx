import { StrictMode } from 'react'
import { createRoot, hydrateRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

const container = document.getElementById('root')!

// Mirrors normalizePath in src/data/routes.ts: vite dev serves every path as
// the bare index.html, so a missing trailing slash (e.g. a manually typed
// "/issues") is normalised the same way the route table itself is keyed.
const rawPath = window.location.pathname || '/'
const path = rawPath === '/' || rawPath.endsWith('/') ? rawPath : `${rawPath}/`

const app = (
  <StrictMode>
    <App path={path} />
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
