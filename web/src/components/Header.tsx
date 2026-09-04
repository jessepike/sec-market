import type { MouseEvent } from 'react'
import { useEffect, useState } from 'react'
import { LAST_UPDATED_DISPLAY, LAST_UPDATED_ISO, PRODUCT_TITLE } from '../data/meta'
import { normalizePath } from '../data/routes'

interface NavItem {
  href: string
  label: string
  /** Cross-page link (Archive lives at /issues/, not a same-page hash). */
  crossPage?: true
}

const navItems: NavItem[] = [
  { href: '#overview', label: 'Issue' },
  { href: '/issues/', label: 'Archive', crossPage: true },
  { href: '#read', label: 'Thesis' },
  { href: '#landscape', label: 'Landscape' },
  { href: '#prints', label: 'Scorecard' },
  { href: '#research', label: 'Evidence' },
  { href: '#method', label: 'Method' },
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
 * — "read", "landscape", "prints", "research", "method" — live only on the
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
          <time dateTime={LAST_UPDATED_ISO}>{LAST_UPDATED_DISPLAY}</time>
        </p>
      </div>
    </header>
  )
}
