import { formatShortDate } from '../data/dates'
import { landscapeDomains, securityDomains, trackedPrintEvidenceIds } from '../data/domains'
import { currentEdition, editionDomainRows } from '../data/edition'
import { EvidenceLink } from './EvidenceLink'

function kindLabel(kind: string): string {
  if (kind === 'revised') return 'Moved'
  if (kind === 'new') return 'New'
  return 'Held'
}

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

/** The one confidence value every landscape card shares, when they agree. */
function uniformLandscapeConfidence(): string | null {
  const values = new Set(landscapeDomains.map((domain) => domain.evidenceStrength))
  return values.size === 1 ? [...values][0] : null
}

/**
 * D-76/autonomy-coverage-plan.md §3, step 1: this card used to carry a
 * direction glyph, a PREPARE/WATCH chip, the domain's judged "why"/"summary"
 * prose, a JUDGED stamp, and a HORIZON/CONFIDENCE line — all judgment. The
 * site publishes sourced facts only now, so a card is the domain name and
 * its tracked print, nothing else.
 */
function LandscapeSection() {
  const domainCount = landscapeDomains.length
  const domainLabel = domainCount === 1 ? 'domain' : 'domains'

  return (
    <section id="landscape" className="landscape" aria-labelledby="landscape-heading">
      <div className="landscape__intro">
        <p className="eyebrow">
          The landscape · {countWord(domainCount)} {domainLabel}
        </p>
        <h2 id="landscape-heading">The security market, by domain.</h2>
        <p className="landscape__lede">Tracked suppliers and the latest sourced figure for each.</p>
      </div>
      <div className="landscape__cards">
        {landscapeDomains.map((domain) => (
          <article key={domain.id} className="domain-card">
            <div className="domain-card__top">
              <h2>
                <span className="domain-card__label">{domain.name}</span>
              </h2>
            </div>
            <div className="domain-card__layer domain-card__layer--tracked">
              <p className="stamp-label">TRACKED</p>
              <p className="domain-card__print">{domain.print}</p>
              <EvidenceLink ids={trackedPrintEvidenceIds(domain)} />
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

function TempoSection() {
  const prior = currentEdition.priorDateDisplay
  const domainRows = editionDomainRows()
  const uniformConfidence = uniformLandscapeConfidence()

  return (
    <section id="domains" className="tempo-board" aria-labelledby="domains-heading">
      <div className="section-heading">
        <h2 id="domains-heading">Tempo</h2>
        <p>
          Each domain has a dated posture, a horizon, and the evidence that produced it. Tag will
          not exceed the Episode 002 posture.
        </p>
        {uniformConfidence ? (
          <p className="tempo-confidence-note">
            Confidence: {uniformConfidence.toUpperCase()} across every landscape domain.
          </p>
        ) : null}
      </div>

      <div className="edition-delta" aria-labelledby="edition-delta-heading">
        <div className="edition-delta__head">
          <h3 id="edition-delta-heading">{prior ? `Since ${prior}` : 'Opening edition'}</h3>
          <p>{currentEdition.summary}</p>
        </div>
        <div className="table-scroll">
          <table className="tempo-table edition-table">
            <caption className="visually-hidden">
              What changed in this edition versus the prior published edition
            </caption>
            <thead>
              <tr>
                <th scope="col">Surface</th>
                <th scope="col">This edition</th>
                <th scope="col">Vs last</th>
              </tr>
            </thead>
            <tbody>
              {currentEdition.surfaces.map((surface) => (
                <tr key={surface.id}>
                  <th scope="row">{surface.label}</th>
                  <td>{surface.detail}</td>
                  <td>
                    <span className={`edition-kind edition-kind--${surface.kind}`}>
                      {kindLabel(surface.kind)}
                    </span>
                  </td>
                </tr>
              ))}
              {domainRows.map((row) => (
                <tr key={row.id}>
                  <th scope="row">{row.name}</th>
                  <td>{row.change}</td>
                  <td>
                    <span className={`edition-kind edition-kind--${row.kind}`}>
                      {kindLabel(row.kind)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="table-scroll">
        <table className="tempo-table">
          <caption className="visually-hidden">
            Security domain tempo: dated posture, horizon, and recommended action
          </caption>
          <thead>
            <tr>
              <th scope="col">Domain</th>
              <th scope="col">As of</th>
              <th scope="col">Horizon</th>
              <th scope="col">Do</th>
            </tr>
          </thead>
          {securityDomains.map((domain) => {
            const row = domainRows.find((item) => item.id === domain.id)
            return (
              <tbody key={domain.id} className="tempo-block">
                <tr>
                  <th scope="row">{domain.name}</th>
                  <td className="tempo-table__win">
                    <time dateTime={domain.asOf}>{formatShortDate(domain.asOf)}</time>
                  </td>
                  <td className="tempo-table__win">{domain.horizon}</td>
                  <td>
                    <span className={`tag tag--${domain.tag.toLowerCase()}`}>{domain.tag}</span>
                  </td>
                </tr>
                <tr className="tempo-table__detail">
                  <td colSpan={4}>
                    <p>{domain.why}</p>
                    {row?.note ? (
                      <p className="tempo-table__delta">
                        <span className={`edition-kind edition-kind--${row.kind}`}>
                          {kindLabel(row.kind)}
                        </span>{' '}
                        {row.note}
                      </p>
                    ) : null}
                    <div className="tempo-table__evidence">
                      <p className="tempo-table__produced">Produced by</p>
                      <EvidenceLink ids={domain.supportingEvidenceIds} />
                      {domain.counterEvidenceIds.length > 0 ? (
                        <>
                          <p className="tempo-table__produced">Tension</p>
                          <EvidenceLink
                            ids={domain.counterEvidenceIds}
                            className="evidence-link--counter"
                          />
                        </>
                      ) : null}
                    </div>
                  </td>
                </tr>
              </tbody>
            )
          })}
        </table>
      </div>
    </section>
  )
}

export function DomainBoard({ surface = 'landscape' }: { surface?: 'landscape' | 'tempo' }) {
  if (surface === 'tempo') return <TempoSection />
  return <LandscapeSection />
}
