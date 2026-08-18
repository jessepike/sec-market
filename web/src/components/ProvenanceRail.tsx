import { formatShortDate } from '../data/dates'
import { LAST_UPDATED_ISO, PRODUCT_TITLE } from '../data/meta'

export function ProvenanceRail() {
  return (
    <div className="rail" role="region" aria-label="Provenance">
      <div className="rail__inner">
        <p className="rail__brand">{PRODUCT_TITLE}</p>
        <span className="rail__rule" aria-hidden="true" />
        <p className="rail__asof">
          AS OF <time dateTime={LAST_UPDATED_ISO}>{formatShortDate(LAST_UPDATED_ISO)}</time>
        </p>
        <ul className="rail__legend">
          <li className="rail__state rail__state--tracked">
            <span className="rail__swatch" aria-hidden="true" />
            <span>TRACKED · refreshed weekly</span>
          </li>
          <li className="rail__state rail__state--judged">
            <span className="rail__swatch" aria-hidden="true" />
            <span>JUDGED · signed and dated by a person</span>
          </li>
          <li className="rail__state rail__state--unsourced">
            <span className="rail__swatch" aria-hidden="true" />
            <span>NEEDS A SOURCE</span>
          </li>
        </ul>
      </div>
    </div>
  )
}
