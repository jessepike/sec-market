import { useState } from 'react'
import { LAST_UPDATED_DISPLAY, PRODUCT_TITLE } from '../data/meta'

const navItems = [
  { href: '#overview', label: 'Overview' },
  { href: '#layers', label: 'Layers' },
  { href: '#domains', label: 'Domains' },
  { href: '#signals', label: 'Signals' },
  { href: '#prompts', label: 'Prompts' },
  { href: '#research', label: 'Research' },
]

export function Header() {
  const [navOpen, setNavOpen] = useState(false)

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <a href="#" className="site-header__brand">
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
            {navItems.map((item) => (
              <li key={item.href}>
                <a href={item.href} onClick={() => setNavOpen(false)}>
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
        <p className="site-header__updated">
          <time dateTime="2026-08-15">{LAST_UPDATED_DISPLAY}</time>
        </p>
      </div>
    </header>
  )
}
