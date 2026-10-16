import type { MouseEvent } from 'react'
import { useEffect, useState } from 'react'
import { PRODUCT_TITLE } from '../data/meta'
import { certifiedDateDisplay } from '../data/tracker/certification'
import { normalizePath } from '../data/routes'

interface NavItem {
  href: string
  label: string
  /** Cross-page link (Archive lives at /issues/, not a same-page hash). */
  crossPage?: true
}

// "Thesis" left this list under SEC-MARKET-FABLE-001 T6-16: the founding
// thesis moved to its own page, /thesis/ (product-core.md §5 — it is "one
// standing analysis on the site, not the site's identity"), and is linked
// from the front page's #read pointer and the footer instead of the primary
// nav. #read still exists on the front page; it just carries a different,
// quieter block now — see ThesisPointer.tsx.
// Step 5 (autonomy-coverage-plan.md §3): "Scorecard" pointed at `#prints`
// (PrintGrid), which no longer renders on any route — the twelve-domain
// tracker at `#market` (MarketByDomain) replaces it, so the nav item now
// points there instead of at a dead anchor.
// AUTO-001 fix pass (2026-09-26), item 4: "Landscape" (`#landscape`) is
// dropped — DomainBoard's LandscapeSection no longer renders on any route,
// so the link had no target left to resolve to (see App.tsx's FrontPage
// comment).
const navItems: NavItem[] = [
  { href: '#tracker-changed', label: 'What changed' },
  { href: '#reported-growth', label: 'Reported growth' },
  { href: '/issues/', label: 'Archive', crossPage: true },
  { href: '#market', label: 'Market' },
  { href: '#research', label: 'Evidence' },
  { href: '#method', label: 'Method' },
  { href: '/feed.xml', label: 'Feed', crossPage: true },
]

function scrollToHash(hash: string) {
  const id = decodeURIComponent(hash.replace('#', ''))
  if (!id) return
  const target = document.getElementById(id)
  if (!target) return

  const details = target instanceof HTMLDetailsElement ? target : target.closest('details')
  if (details) details.open = true

  requestAnimationFrame(() => {
    target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

/**
 * `path` is the route this Header is rendered on (see src/data/routes.ts —
 * threaded down from App via AppShell). On the front page every hash target
 * in navItems exists in the document, so the in-page scroll behaviour below
 * is unconditional there and unchanged from before this route-awareness was
 * added. On any other route (the archive, an issue permalink) some targets
 * — "market", "landscape", "research", "method" — live only on the
 * front page, so the href must point there (`/#<id>`) and a click must be
 * allowed to navigate normally rather than preventDefault into a no-op.
 */
export function Header({ path = '/' }: { path?: string }) {
  const [navOpen, setNavOpen] = useState(false)
  const onFrontPage = normalizePath(path) === '/'

  useEffect(() => {
    if (window.location.hash) {
      scrollToHash(window.location.hash)
    }
    const onHash = () => scrollToHash(window.location.hash)
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  /** `hash` is always the bare `#id` form; resolves to a same-page or a cross-page href. */
  function hrefFor(hash: string): string {
    return onFrontPage ? hash : `/${hash}`
  }

  /**
   * Only intercepts the click (and scrolls in place) when `hash`'s target
   * actually exists in the current document. Otherwise it leaves the
   * default navigation alone, so the browser follows the href — a same-page
   * jump on the front page, or a real navigation to `/#<id>` elsewhere.
   */
  function handleNavClick(hash: string) {
    return (event: MouseEvent<HTMLAnchorElement>) => {
      const id = hash.slice(1)
      if (typeof document === 'undefined' || !document.getElementById(id)) {
        setNavOpen(false)
        return
      }
      event.preventDefault()
      setNavOpen(false)
      scrollToHash(hash)
      window.history.replaceState(null, '', hash)
    }
  }

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <a
          href={hrefFor('#overview')}
          className="site-header__brand"
          onClick={handleNavClick('#overview')}
        >
          <span className="site-header__mark" aria-hidden="true" />
          <strong>{PRODUCT_TITLE}</strong>
        </a>
        <nav className={`site-header__nav${navOpen ? ' is-open' : ''}`} aria-label="Primary">
          <button
            type="button"
            className="nav-toggle"
            aria-expanded={navOpen}
            aria-controls="primary-nav"
            onClick={() => setNavOpen((open) => !open)}
          >
            {navOpen ? 'Close' : 'Menu'}
          </button>
          <ul id="primary-nav">
            {navItems.map((item) =>
              item.crossPage ? (
                <li key={item.href}>
                  <a href={item.href} onClick={() => setNavOpen(false)}>
                    {item.label}
                  </a>
                </li>
              ) : (
                <li key={item.href}>
                  <a href={hrefFor(item.href)} onClick={handleNavClick(item.href)}>
                    {item.label}
                  </a>
                </li>
              ),
            )}
          </ul>
        </nav>
        <p className="site-header__updated">
          Certified SEC figures last changed {certifiedDateDisplay}
        </p>
      </div>
    </header>
  )
}
