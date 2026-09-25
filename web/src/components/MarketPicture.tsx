import { securityDomains } from '../data/domains'
import {
  DOMAIN_PRINT_GROUP,
  MAX_VISIBLE_VENDORS_PER_DOMAIN,
  marketPictureVendorEntries,
} from '../data/marketPicture'
import { LAST_UPDATED_ISO } from '../data/meta'
import { vendorPrints } from '../data/prints'
import type { SecurityDomain } from '../data/types'
import { EvidenceLink } from './EvidenceLink'

// Exact wording from the coordinator's spec change for T6-2 (2026-09-20,
// after external review) — replaces design-spec v0.3 §3.3's original
// caption. Do not paraphrase; the wording is what keeps this table from
// reading as a ranking.
const MARKET_PICTURE_CAPTION =
  'These are figures the companies themselves reported, listed alphabetically. They measure ' +
  'different things over different periods, so they are labelled and not ranked. Being listed ' +
  'is not a recommendation, and being absent is not a criticism. Private companies that publish ' +
  'no comparable figures are tracked through funding and acquisitions instead.'

function DomainRow({ domain }: { domain: SecurityDomain }) {
  const group = DOMAIN_PRINT_GROUP[domain.id]
  const groupPrints = group ? vendorPrints.filter((print) => print.group === group) : []
  const entries = marketPictureVendorEntries(groupPrints, LAST_UPDATED_ISO)
  const visible = entries.slice(0, MAX_VISIBLE_VENDORS_PER_DOMAIN)
  const overflow = entries.length - visible.length

  return (
    <article id={`domain-${domain.id}`} className="market-picture__domain">
      <div className="market-picture__stance">
        <h3 className="market-picture__domain-name">{domain.name}</h3>
      </div>

      <div className="market-picture__vendors">
        <p className="stamp-label">Tracked suppliers and what they last reported</p>
        {visible.length === 0 ? (
          <p className="market-picture__empty">
            No comparable public growth figures yet. Tracked through{' '}
            <a href="#prints">funding and acquisitions</a>.
          </p>
        ) : (
          <ul className="market-picture__vendor-list">
            {visible.map((entry) => (
              <li
                key={entry.print.id}
                id={`vendor-${domain.id}-${entry.print.vendorSlug ?? entry.print.id}`}
                className="market-picture__vendor"
              >
                <p className="market-picture__vendor-top">
                  <span className="market-picture__vendor-name">{entry.print.name}</span>
                  {/* Fix pass T6-7 item 1: no green/red tone here — the caption right above
                      says these are labelled, not ranked, and a colour cue reintroduces the
                      ranking the coordinator's spec change removed. The scorecard (PrintGrid)
                      keeps its own tone colouring; this component never reads .tone at all. */}
                  <span className="market-picture__vendor-value">{entry.print.value}</span>
                </p>
                <div className="market-picture__vendor-metaRow">
                  <p className="market-picture__vendor-meta">
                    {entry.print.metric} &middot; {entry.print.period}
                    {entry.isOlderFigure ? (
                      <span className="market-picture__older-figure"> &middot; older figure</span>
                    ) : null}
                    {entry.isSegment ? (
                      <span className="market-picture__segment-tag">
                        {' '}
                        &middot; product line, not the whole company
                      </span>
                    ) : null}
                  </p>
                  <EvidenceLink ids={entry.print.evidenceIds} className="market-picture__evidence" />
                </div>
                {entry.previous ? (
                  <p className="market-picture__previous">
                    Previously {entry.previous.value} ({entry.previous.period})
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
        {overflow > 0 ? (
          <p className="market-picture__show-all">
            <a href="#prints">Show all {entries.length}</a>
          </p>
        ) : null}
      </div>
    </article>
  )
}

/**
 * "The market by domain" — design-spec v0.3 §3.3, revised by the
 * coordinator's spec change for T6-2 (2026-09-20, after external review):
 * every domain's tracked suppliers are listed alphabetically, never ranked
 * by figure size. Built strictly from domains.ts (the judged stance) and
 * prints.ts (the tracked figures) — no new data.
 */
export function MarketPicture() {
  return (
    <section id="market" className="market-picture" aria-labelledby="market-heading">
      <div className="section-heading">
        <h2 id="market-heading">The market by domain</h2>
        <p className="market-picture__caption">{MARKET_PICTURE_CAPTION}</p>
      </div>
      <div className="market-picture__domains">
        {securityDomains.map((domain) => (
          <DomainRow key={domain.id} domain={domain} />
        ))}
      </div>
    </section>
  )
}
