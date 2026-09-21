import { formatShortDate } from '../data/dates'
import { landscapeDomains, securityDomains, trackedPrintEvidenceIds } from '../data/domains'
import { currentEdition, editionDomainRows } from '../data/edition'
import { claimId, effectiveJudgment } from '../data/reconfirmationHelpers'
import { reconfirmations } from '../data/reconfirmations'
import type { Momentum, TempoTag } from '../data/types'
import { EvidenceLink } from './EvidenceLink'
import { JudgedStamp } from './JudgedStamp'

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

function DirectionGlyph({ tag, momentum }: { tag: TempoTag; momentum: Momentum }) {
  if (tag === 'PREPARE') {
    return (
      <svg className="domain-card__glyph" width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <path d="M4 14 L16 5 M11 5 h5 v5" stroke="currentColor" strokeWidth="1.8" />
      </svg>
    )
  }
  if (momentum === 'stable-to-decelerating') {
    return (
      <svg className="domain-card__glyph" width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <path d="M4 10 h12" stroke="currentColor" strokeWidth="1.8" />
      </svg>
    )
  }
  return (
    <svg className="domain-card__glyph" width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M4 12 L9 8 L13 11 L16 7" stroke="currentColor" strokeWidth="1.8" fill="none" />
    </svg>
  )
}

/**
 * Whether the landscape cards' confidence chip is worth showing at all. Per
 * spec §4, the chip is shown per-card only when confidence actually differs
 * across the four landscape cards; when every card carries the same value the
 * chip is dropped from the cards and the shared value is stated once, in the
 * Tempo table instead (see TempoSection's confidence note below).
 */
function landscapeConfidenceVaries(): boolean {
  return new Set(landscapeDomains.map((domain) => domain.evidenceStrength)).size > 1
}

/** The one confidence value every landscape card shares, when they agree. */
function uniformLandscapeConfidence(): string | null {
  const values = new Set(landscapeDomains.map((domain) => domain.evidenceStrength))
  return values.size === 1 ? [...values][0] : null
}

function LandscapeSection() {
  const domainCount = landscapeDomains.length
  const domainLabel = domainCount === 1 ? 'domain' : 'domains'
  const showConfidenceChip = landscapeConfidenceVaries()

  return (
    <section id="landscape" className="landscape" aria-labelledby="landscape-heading">
      <div className="landscape__intro">
        <p className="eyebrow">
          The landscape · {countWord(domainCount)} {domainLabel}
        </p>
        <h2 id="landscape-heading">Where the security market is going, not where it has been.</h2>
        <p className="landscape__lede">
          Dated postures, the evidence under each one, and an honest mark on how sure anyone is.
          A posture moves only when a person signs it.
        </p>
      </div>
      <div className="landscape__cards">
        {landscapeDomains.map((domain) => (
          <article
            key={domain.id}
            className={'domain-card domain-card--' + domain.tag.toLowerCase()}
          >
            <div className="domain-card__top">
              <h2>
                <span className="domain-card__label">{domain.name}</span>
                {domain.why}
              </h2>
              <DirectionGlyph tag={domain.tag} momentum={domain.momentum} />
              <span className={'chip chip--' + domain.tag.toLowerCase()}>{domain.tag}</span>
            </div>
            <p className="domain-card__read">{domain.summary}</p>
            <div className="domain-card__layer domain-card__layer--tracked">
              <p className="stamp-label">TRACKED</p>
              <p className="domain-card__print">{domain.print}</p>
              <EvidenceLink ids={trackedPrintEvidenceIds(domain)} />
            </div>
            <div className="domain-card__layer domain-card__layer--judged">
              <JudgedStamp
                judgedOn={domain.asOf}
                reconfirmedOn={effectiveJudgment(claimId('domain', domain.id), domain.asOf, reconfirmations).reconfirmedOn}
              />
              <p className="domain-card__judged">
                <span className="domain-card__judged-part">HORIZON · {domain.horizon}</span>
                {showConfidenceChip ? (
                  <span className="domain-card__judged-part">
                    CONFIDENCE · {domain.evidenceStrength.toUpperCase()}
                  </span>
                ) : null}
              </p>
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
