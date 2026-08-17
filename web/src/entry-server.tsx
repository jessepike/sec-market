import { StrictMode } from 'react'
import { renderToString } from 'react-dom/server'
import App from './App.tsx'

/**
 * Server-side render entry used at build time by scripts/prerender.ts.
 *
 * The tree here MUST match the tree mounted in main.tsx exactly (including
 * StrictMode) or React will report a hydration mismatch in the browser.
 * No stylesheet import here on purpose: the client entry owns index.css so
 * the SSR bundle stays a pure markup producer.
 */
export function render(): string {
  return renderToString(
    <StrictMode>
      <App />
    </StrictMode>,
  )
}
