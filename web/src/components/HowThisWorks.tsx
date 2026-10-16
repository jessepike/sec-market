import { AUTHOR_NAME, INDEPENDENCE_STATEMENT } from '../data/meta'
import { certifiedClaimCount, certifiedCount, certifiedDateDisplay, checkInterval, notCertified } from '../data/tracker/certification'
import { sourcingLadder } from '../data/method'
import { notCoveredByTracker, trackerDomains } from '../data/tracker/domains'
import { trackerSuppliers } from '../data/tracker/suppliers'

/**
 * AUTO-001 fix pass 2 (2026-09-26), item 5: both blind rescores caught
 * live-page judgment text here — this section used to also render two
 * tables from data/method.ts (`signalFamilies`, `reasoningSteps`), framed
 * as "archived analysis" but still served on `/`, not an archive-only
 * route. Those tables carried the exact banned phrases both scorers quoted
 * verbatim ("PREPARE only where the account has a matching live motion",
 * "That is a no-call", "The best check on whether customers actually
 * spent"). They are gone from this component; `data/method.ts` itself is
 * untouched (`signalFamilies`/`reasoningSteps` stay there as the historical
 * record of how the archived `/thesis/` call was reasoned — it is simply
 * not imported here anymore). The sourcing ladder stays: it describes a
 * publishing standard for the live tracker, not a judgment.
 */
const notCertifiedLabels: Record<string, string> = {
  headlineMetric: 'Company-stated metrics',
  ownership: 'Ownership text',
  'events without an sec.gov source': 'Events from press releases and news',
  'event text': 'Written summaries of events',
  growthBasis: 'Reporting-currency notes',
}

export function HowThisWorks() {
  return (
    <section className="method" aria-labelledby="method-heading">
      <div className="section-heading">
        <h2 id="method-heading">How this is built</h2>
        <p>
          The tracker publishes facts only: no stances, rankings, forecasts, or sentences
          interpreting what a fact means. Certified figures publish automatically, with no human
          approval step and no AI involved.
        </p>
      </div>

      <h3 className="method__subhead">Two kinds of figure</h3>
      <p className="method-copy">
        <strong>Certified.</strong> For the {certifiedCount} public companies that report quarterly
        revenue to the SEC in structured form, the site re-derives each figure from the company&rsquo;s
        own SEC filings: name and ticker, quarterly revenue, year-over-year growth, up to eight
        quarters, and the filing and date of SEC-filed events. A check is scheduled {checkInterval}.
        All {certifiedClaimCount} certified claims must pass before anything publishes; if one fails,
        nothing changes on the site. New figures publish only when a value changes. Last certified
        change: {certifiedDateDisplay}.
      </p>
      <p className="method-copy">
        The check that certifies a figure is separate code from the code that produces it, but it
        reads the same SEC data with the same rules for quarters, restatements and revenue tags. It
        confirms the figures reproduce from the filings. It is not a second, independent method.
      </p>
      <p className="method-copy">
        <strong>Not certified.</strong> Filed-event summaries are written by a script from the
        filing&rsquo;s form and item numbers. Everything else was collected from company releases, press and
        company pages, partly with AI assistance, and checked against the sourcing ladder below when
        it was published. It keeps that source and date and is not re-checked automatically:
      </p>
      <ul className="method-copy">
        {Object.entries(notCertified).map(([field, reason]) => (
          <li key={field}>
            <strong>{notCertifiedLabels[field] ?? field}.</strong> {reason}
          </li>
        ))}
        <li>Private, PE-owned and non-US suppliers, and suppliers that report as a segment of a larger company.</li>
      </ul>

      <h3 className="method__subhead">Filed events</h3>
      <p className="method-copy">
        Events from SEC filings are listed one by one, with the filing linked. The same rules apply
        to every company: officer and director changes (8-K Item 5.02), completed acquisitions and
        disposals (2.01), new debt (2.03, quoting the opening of the filing&rsquo;s own description; the
        quote is extracted by a script, not certified, and the linked filing has the full text), exit and restructuring costs (2.05), bankruptcy (1.03), listing notices (3.01 and
        Form 25), merger proxies, and late-filing notices. A change to these rules is dated on the{' '}
        <a href="/corrections/">corrections page</a>.
      </p>

      <h3 className="method__subhead">The sourcing ladder</h3>
      <p className="method-copy">
        Facts that are not from SEC filings were checked against this ladder when they were
        published. A fact resting only on a single trade-press report with no primary document
        behind it does not publish here.
      </p>
      <div className="table-scroll">
        <table className="tempo-table method-table">
          <caption className="visually-hidden">The five-rung sourcing ladder, strongest first</caption>
          <thead>
            <tr>
              <th scope="col">Rung</th>
              <th scope="col">What it is</th>
              <th scope="col">Publishes alone?</th>
            </tr>
          </thead>
          <tbody>
            {sourcingLadder.map((rung) => (
              <tr key={rung.rung}>
                <th scope="row">
                  {rung.rung}. {rung.label}
                </th>
                <td>{rung.description}</td>
                <td>{rung.publishesAlone ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 className="method__subhead">What is not covered</h3>
      <p className="method-copy">
        {trackerDomains.length} domains, {trackerSuppliers.length} tracked suppliers. The full list,
        and what falls outside it, is in <a href="#tracker-coverage">What this site covers</a>.{' '}
        {notCoveredByTracker.length} categories of company and claim are outside this tracker.
      </p>

      <h3 className="method__subhead">Who runs this</h3>
      <p className="method-copy" id="byline">
        Security Market Pulse is run by <a href="https://jessepike.dev">{AUTHOR_NAME}</a>, who works
        in security sales at a technology reseller and runs an independent advisory practice. Some
        tracked suppliers are companies that reseller sells. The same published rules apply to every
        supplier. {INDEPENDENCE_STATEMENT}
      </p>
    </section>
  )
}
