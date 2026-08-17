import { printGroups, vendorPrints } from '../data/prints'
import { EvidenceLink } from './EvidenceLink'

export function PrintGrid() {
  return (
    <section id="prints" className="print-grid" aria-labelledby="prints-heading">
      <div className="section-heading">
        <h2 id="prints-heading">This period</h2>
        <p>Public prints first. Private names stay on the board as capital or “no series” — not invented ARR.</p>
      </div>
      <div className="table-scroll print-table-scroll">
        <table className="print-table">
          <thead>
            <tr>
              <th scope="col">Vendor</th>
              <th scope="col">Period</th>
              <th scope="col">Metric</th>
              <th scope="col">Value</th>
              <th scope="col">Note</th>
              <th scope="col">
                <span className="visually-hidden">Source</span>
              </th>
            </tr>
          </thead>
          {printGroups.map((group) => {
            const prints = vendorPrints.filter((print) => print.group === group)
            if (prints.length === 0) return null
            return (
              <tbody key={group} className="print-table__group">
                <tr>
                  <th scope="colgroup" colSpan={6}>
                    {group}
                  </th>
                </tr>
                {prints.map((print) => (
                  <tr
                    key={print.id}
                    className={print.surface === 'coverage' ? 'print-table__coverage' : undefined}
                  >
                    <th scope="row">{print.name}</th>
                    <td className="print-table__period">{print.period}</td>
                    <td className="print-table__metric">{print.metric}</td>
                    <td className={`print-table__value print-table__value--${print.tone}`}>{print.value}</td>
                    <td className="print-table__note">{print.note}</td>
                    <td className="print-table__source">
                      <EvidenceLink ids={print.evidenceIds} />
                    </td>
                  </tr>
                ))}
              </tbody>
            )
          })}
        </table>
      </div>
    </section>
  )
}
