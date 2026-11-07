import { CONTACT_EMAIL } from '../data/meta'

/**
 * One footer on every page (UX and consistency review, 2026-11-07): the reference pages that left
 * the top nav, the corrections address and the standing disclaimer.
 */
export function SiteFooter() {
  return (
    <footer id="follow" className="site-footer" aria-label="Site">
      <nav aria-label="Reference">
        <ul>
          <li><a href="/data/">Data for agents</a></li>
          <li><a href="/corrections/">Corrections</a></li>
          <li><a href="/thesis/">Standing analysis</a></li>
          <li><a href="/issues/">Issue archive</a></li>
          <li><a href="/feed.xml">Corrections feed (RSS)</a></li>
          <li><a href="/certified-coverage.json">Certification receipt</a></li>
          <li><a href={`mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent('Security Market Pulse: correction or question')}`}>Contact</a></li>
        </ul>
      </nav>
      <p>Public sources only. Not investment advice. If a figure is wrong, send it to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>; every published correction is listed on the <a href="/corrections/">corrections page</a>.</p>
    </footer>
  )
}
