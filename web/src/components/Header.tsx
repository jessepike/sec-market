import { useEffect, useState } from 'react'
import { LAST_UPDATED_DISPLAY, LAST_UPDATED_ISO, PRODUCT_TITLE } from '../data/meta'

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

export function Header() {
  const [navOpen, setNavOpen] = useState(false)

  useEffect(() => {
    if (window.location.hash) {
      scrollToHash(window.location.hash)
    }
    const onHash = () => scrollToHash(window.location.hash)
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <a
          href="#overview"
          className="site-header__brand"
          onClick={(event) => {
            event.preventDefault()
            setNavOpen(false)
            scrollToHash('#overview')
            window.history.replaceState(null, '', '#overview')
          }}
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
                  <a
                    href={item.href}
                    onClick={(event) => {
                      event.preventDefault()
                      setNavOpen(false)
                      scrollToHash(item.href)
                      window.history.replaceState(null, '', item.href)
                    }}
                  >
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
