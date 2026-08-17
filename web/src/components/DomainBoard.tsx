import { formatShortDate } from '../data/dates'
import { securityDomains } from '../data/domains'
import { currentEdition, editionDomainRows } from '../data/edition'
import { EvidenceLink } from './EvidenceLink'

function kindLabel(kind: string): string {
  if (kind === 'revised') return 'Moved'
  if (kind === 'new') return 'New'
  return 'Held'
}

export function DomainBoard() {
  const prior = currentEdition.priorDateDisplay
  const domainRows = editionDomainRows()

  return (
    <section id="domains" className="tempo-board" aria-labelledby="domains-heading">
      <div className="section-heading">
        <h2 id="domains-heading">Tempo</h2>
        <p>
          Each domain has a dated posture, a horizon, and the evidence that produced it. Tag will
          not exceed the Episode 002 posture.
        </p>
      </div>

      <div className="edition-delta" aria-labelledby="edition-delta-heading">
        <div className="edition-delta__head">
          <h3 id="edition-delta-heading">
            {prior ? `Since ${prior}` : 'Opening edition'}
          </h3>
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
                  <td>
                    {row.tag} · {row.horizon}
                  </td>
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
            const note = currentEdition.domainNotes.find((item) => item.domainId === domain.id)
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
                    {note ? <p className="tempo-table__delta">{note.note}</p> : null}
                    <div className="tempo-table__evidence">
                      <EvidenceLink ids={domain.supportingEvidenceIds} label="Produced by" />
                      {domain.counterEvidenceIds.length > 0 ? (
                        <EvidenceLink
                          ids={domain.counterEvidenceIds}
                          label="Tension"
                          className="evidence-link--counter"
                        />
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
