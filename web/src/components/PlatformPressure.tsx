import { formatShortDate } from '../data/dates'
import { platformPressure } from '../data/platformPressure'
import type { PressureGroup, VendorPosition } from '../data/types'
import { EvidenceLink } from './EvidenceLink'

const groupCopy: Record<PressureGroup, string> = {
  holding: 'Holding position',
  'buying-in': 'Buying in rather than building',
  outrun: 'Being outrun in their own motion',
  challengers: 'Challengers worth a look',
}

const groupOrder: PressureGroup[] = ['holding', 'buying-in', 'outrun', 'challengers']

function positionLabel(position: VendorPosition): string {
  return position.slice(0, 1).toUpperCase() + position.slice(1)
}

export function PlatformPressure() {
  return (
    <section id="platforms" className="pressure" aria-labelledby="platforms-heading">
      <div className="section-heading">
        <p className="eyebrow">Platform pressure</p>
        <h2 id="platforms-heading">Who is holding, who is buying in, who is being outrun</h2>
        <p>
          The partner question. Where an incumbent is still the safe pick, where it is acquiring its
          way into a category, and where a challenger is printing faster inside the same motion.
        </p>
      </div>
      <p className="stamp-label">TRACKED PRINTS · JUDGED READ</p>
      <div className="table-scroll pressure__desktop">
        <table className="pressure-table">
          <caption className="visually-hidden">Platform pressure by vendor position</caption>
          <thead>
            <tr>
              <th scope="col">Vendor</th>
              <th scope="col">Position</th>
              <th scope="col">Latest tracked print</th>
              <th scope="col">Judged read</th>
            </tr>
          </thead>
          {groupOrder.map((group) => (
            <tbody key={group} className={'pressure-table__group pressure-table__group--' + group}>
              <tr>
                <th scope="colgroup" colSpan={4}>
                  {groupCopy[group]}
                </th>
              </tr>
              {platformPressure[group].map((row) => (
                <tr key={row.id}>
                  <th scope="row">{row.vendors.join(' · ')}</th>
                  <td className="mono">{positionLabel(row.position)}</td>
                  <td>
                    <p className="mono">{row.print}</p>
                    {row.provenance.print.layer === 'tracked' ? (
                      <EvidenceLink ids={row.provenance.print.evidenceIds} />
                    ) : null}
                  </td>
                  <td>
                    <p>{row.read}</p>
                    {row.provenance.read.layer === 'judged' ? (
                      <p className="stamp-label">
                        JUDGED{' '}
                        <time dateTime={row.provenance.read.judgedOn}>
                          {formatShortDate(row.provenance.read.judgedOn)}
                        </time>
                      </p>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          ))}
        </table>
      </div>
      <div className="pressure__mobile">
        {groupOrder.map((group) => (
          <div key={group} className={'pressure-stack pressure-stack--' + group}>
            <p className="stamp-label">{groupCopy[group]}</p>
            {platformPressure[group].map((row) => (
              <article key={row.id} className="pressure-stack__row">
                <div className="pressure-stack__top">
                  <h3>{row.vendors.join(' · ')}</h3>
                  <span className="mono">{positionLabel(row.position)}</span>
                </div>
                <p className="mono">{row.print}</p>
                {row.provenance.print.layer === 'tracked' ? (
                  <EvidenceLink ids={row.provenance.print.evidenceIds} />
                ) : null}
                <p>{row.read}</p>
                {row.provenance.read.layer === 'judged' ? (
                  <p className="stamp-label">
                    JUDGED{' '}
                    <time dateTime={row.provenance.read.judgedOn}>
                      {formatShortDate(row.provenance.read.judgedOn)}
                    </time>
                  </p>
                ) : null}
              </article>
            ))}
          </div>
        ))}
      </div>
    </section>
  )
}
