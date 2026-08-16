import { EPISODE_ID, LAST_UPDATED_DISPLAY, PRODUCT_TITLE } from '../data/meta'

const navItems = [
  { href: '#overview', label: 'Overview' },
  { href: '#layers', label: 'Market layers' },
  { href: '#domains', label: 'Domains' },
  { href: '#signals', label: 'Signals' },
  { href: '#prompts', label: 'Prompts' },
  { href: '#research', label: 'Research' },
]

export function Header() {
  return (
    <header className="site-header">
      <div className="site-header__inner">
        <a href="#" className="site-header__brand">
          <span className="site-header__mark" aria-hidden="true" />
          <span>
            <strong>{PRODUCT_TITLE}</strong>
            <small>{EPISODE_ID}</small>
          </span>
        </a>
        <nav className="site-header__nav" aria-label="Primary">
          <ul>
            {navItems.map((item) => (
              <li key={item.href}>
                <a href={item.href}>{item.label}</a>
              </li>
            ))}
          </ul>
        </nav>
        <p className="site-header__updated">
          <span className="label">Last updated</span>
          <time dateTime="2026-08-15">{LAST_UPDATED_DISPLAY}</time>
        </p>
      </div>
    </header>
  )
}
