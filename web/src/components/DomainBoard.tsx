import { securityDomains } from '../data/domains'
import { EvidenceLink } from './EvidenceLink'

export function DomainBoard() {
  return (
    <section id="domains" className="tempo-board" aria-labelledby="domains-heading">
      <div className="section-heading">
        <h2 id="domains-heading">Tempo</h2>
        <p>Where the prints convert into a decision. Tag will not exceed the Episode 002 posture.</p>
      </div>
      <div className="table-scroll">
        <table className="tempo-table">
          <thead>
            <tr>
              <th scope="col">Domain</th>
              <th scope="col">Window</th>
              <th scope="col">Do</th>
            </tr>
          </thead>
          {securityDomains.map((domain) => (
            <tbody key={domain.id} className="tempo-block">
              <tr>
                <th scope="row">{domain.name}</th>
                <td className="tempo-table__win">{domain.tempo}</td>
                <td>
                  <span className={`tag tag--${domain.tag.toLowerCase()}`}>{domain.tag}</span>
                </td>
              </tr>
              <tr className="tempo-table__detail">
                <td colSpan={3}>
                  <p>{domain.why}</p>
                  <EvidenceLink
                    ids={[...domain.supportingEvidenceIds, ...domain.counterEvidenceIds]}
                  />
                </td>
              </tr>
            </tbody>
          ))}
        </table>
      </div>
    </section>
  )
}
