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
          <caption className="visually-hidden">
            Vendor prints for the current period, grouped by domain, with period, metric,
            value, note, and source
          </caption>
          <thead>
            <tr>
              <th scope="col">Vendor</th>
              <th scope="col">Period</th>
              <th scope="col">Metric</th>
              <th scope="col">Value</th>
              <th scope="col">Note</th>
              {/* aria-label directly on the cell, not a nested visually-hidden
                  span: an absolutely-positioned descendant with no visible
                  sibling content in a header cell defeats this table's
                  auto width algorithm and makes the page scroll
                  horizontally on narrow viewports. */}
              <th scope="col" aria-label="Source" />
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
