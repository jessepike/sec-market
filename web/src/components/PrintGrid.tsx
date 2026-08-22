import { useEffect } from 'react'
import { printGroups, vendorPrints } from '../data/prints'
import { EvidenceLink } from './EvidenceLink'

// Keep this in lockstep with the min-width:769px / max-width:768px pair in
// index.css — both the CSS and this query decide the same "is this desktop"
// question and must agree.
const DESKTOP_QUERY = '(min-width: 769px)'

const COUNT_WORDS = [
  'zero',
  'one',
  'two',
  'three',
  'four',
  'five',
  'six',
  'seven',
  'eight',
  'nine',
  'ten',
] as const

function countWord(n: number): string {
  if (n >= 1 && n <= 10) return COUNT_WORDS[n]
  return String(n)
}

export function PrintGrid() {
  const printCount = vendorPrints.length
  const domainCount = printGroups.filter((group) =>
    vendorPrints.some((print) => print.group === group),
  ).length

  // Chrome (and, per the HTML spec's own default-rendering rule, potentially
  // other engines) does not just `display: none` a closed <details>' children
  // — it excludes them from paint/hit-testing at a level plain author CSS
  // cannot override, confirmed by checking elementFromPoint against a
  // `display:grid`-forced card: nothing was there. So "all groups open on
  // desktop, nothing to click" cannot be done in CSS; the `open` attribute
  // itself has to be true on wide viewports. This effect is what the App.tsx
  // Analytics comment describes: it runs strictly after mount, never during
  // the render React hydrates against, so server HTML and the client's first
  // paint stay identical (no `open` attribute anywhere) and there is nothing
  // for hydration to disagree about. Only after that first paint does this
  // mutate the real DOM nodes directly — deliberately not React state, since
  // `open` here is uncontrolled native widget state, the same way a ref-based
  // `.focus()` call would be.
  useEffect(() => {
    const mq = window.matchMedia(DESKTOP_QUERY)
    const sync = () => {
      document.querySelectorAll<HTMLDetailsElement>('.print-group').forEach((details) => {
        details.open = mq.matches
      })
    }
    sync()
    mq.addEventListener('change', sync)
    return () => mq.removeEventListener('change', sync)
  }, [])

  return (
    <section id="prints" className="print-grid" aria-labelledby="prints-heading">
      <div className="section-heading">
        <p className="eyebrow">
          The full scorecard · {countWord(printCount)} prints across {countWord(domainCount)}{' '}
          domains
        </p>
        <h2 id="prints-heading">This period</h2>
        <p>Public prints first. Private names stay on the board as capital or “no series” — not invented ARR.</p>
      </div>
      {printGroups.map((group) => {
        const prints = vendorPrints.filter((print) => print.group === group)
        if (prints.length === 0) return null
        const comparable = prints.filter((print) => print.surface !== 'coverage').length
        return (
          // No `open` prop here — see the effect above for why. The <summary>
          // is what keeps the group header always visible and always in the
          // accessibility tree: that part of a <details> element never hides,
          // with or without JS, at any width.
          <details key={group} className="print-group">
            <summary>
              <div className="grouphdr">
                <span className="grouphdr__title">{group}</span>
                <span className="grouphdr__meta">
                  <span className="grouphdr__count">
                    {comparable} print{comparable === 1 ? '' : 's'} · {prints.length} covered
                  </span>
                  {/* Mobile-only tap affordance — the native <details> marker
                      doesn't align on the same line as a flex child, so we
                      draw our own instead of fighting that. Hidden entirely
                      at desktop widths (see index.css), where there's nothing
                      to tap. */}
                  <span className="grouphdr__chevron" aria-hidden="true" />
                </span>
              </div>
            </summary>
            <div className="print-cards">
              {prints.map((print) => (
                <article
                  key={print.id}
                  className={
                    print.surface === 'coverage' ? 'print-card print-card--coverage' : 'print-card'
                  }
                >
                  <header className="print-card__top">
                    <h3>{print.name}</h3>
                    <span>{print.period}</span>
                  </header>
                  <p className={`print-card__value print-card__value--${print.tone}`}>{print.value}</p>
                  <p className="print-card__metric">{print.metric}</p>
                  <p className="print-card__note">{print.note}</p>
                  <EvidenceLink ids={print.evidenceIds} />
                </article>
              ))}
            </div>
          </details>
        )
      })}
    </section>
  )
}
