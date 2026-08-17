import { useEffect, useState, type ComponentType } from 'react'
import { chartEvidenceIds, chartMetricNote } from '../data/market'
import { derivedPanelRows } from '../data/derivePanel'
import { EvidenceLink } from './EvidenceLink'

// Recharts (and BuyerBudgetChart, which also pulls it in) is the single
// largest dependency in the bundle. It renders inside a collapsed <details>,
// so it is split into its own chunk and fetched only after mount, instead of
// shipping in the initial bundle.
//
// This deliberately does NOT use React.lazy()/Suspense: React's own docs
// note lazy() is not supported by ReactDOMServer, and in practice, against
// this app's synchronous renderToString prerender (not a streaming SSR
// setup), it hydrates fine on a cold cache but throws a real hydration
// error (React #419) whenever the chunk resolves fast enough to beat
// hydration to that boundary — reliably reproducible on localhost. A plain
// useEffect-driven dynamic import never runs during SSR or during the
// initial client render, so both start from the identical fallback markup
// and hydrate cleanly; the swap to the real component happens afterward, as
// an ordinary state update.
function useChartsPanel() {
  const [Panel, setPanel] = useState<ComponentType | null>(null)

  useEffect(() => {
    let cancelled = false
    import('./ChartsPanel').then((mod) => {
      if (!cancelled) setPanel(() => mod.default)
    })
    return () => {
      cancelled = true
    }
  }, [])

  return Panel
}

export function MarketLayersChart() {
  const ChartsPanel = useChartsPanel()

  return (
    <section className="chart-section" aria-labelledby="layers-heading">
      <div className="section-heading">
        <h2 id="layers-heading">Market layers</h2>
        <p>
          Panel window 2023-Q1 through 2026-Q1 (2023-Q1 = 100). Later JUL ’26 scorecard prints are
          not on these charts. Fiscal quarters are mapped into calendar buckets — NVIDIA FY27 Q1
          ended 2026-04-26 sits in 2026-Q1. Descriptive sequence only, not a fitted lag.
        </p>
      </div>

        <p className="chart-shared-scale-caption">
          All three charts use the same log-scale index axis (50–1800; 2023-Q1 = 100) so proportional
          differences are visually honest — e.g. infrastructure near 18× vs. security near 2×.
        </p>

      {ChartsPanel ? <ChartsPanel /> : <p className="chart-loading">Loading charts…</p>}

      <details className="chart-table-details">
        <summary>View data table (accessible alternative)</summary>
        <div className="table-scroll">
          <table className="data-table">
            <caption>Derived panel indices by quarter (2023-Q1 = 100)</caption>
            <thead>
              <tr>
                <th scope="col">Quarter</th>
                <th scope="col">NVIDIA DC</th>
                <th scope="col">MSFT</th>
                <th scope="col">AMZN</th>
                <th scope="col">GOOG</th>
                <th scope="col">Hyperscaler median</th>
                <th scope="col">CRWD</th>
                <th scope="col">OKTA</th>
                <th scope="col">FTNT</th>
                <th scope="col">ZS</th>
                <th scope="col">CHKP</th>
                <th scope="col">Security median</th>
              </tr>
            </thead>
            <tbody>
              {derivedPanelRows.map((row) => (
                <tr key={row.quarter}>
                  <th scope="row">{row.quarter}</th>
                  <td>{fmt(row.nvidiaIndex)}</td>
                  <td>{fmt(row.microsoftIndex)}</td>
                  <td>{fmt(row.amazonIndex)}</td>
                  <td>{fmt(row.alphabetIndex)}</td>
                  <td>{fmt(row.hyperscalerMedianIndex)}</td>
                  <td>{fmt(row.crowdstrikeIndex)}</td>
                  <td>{fmt(row.oktaIndex)}</td>
                  <td>{fmt(row.fortinetIndex)}</td>
                  <td>{fmt(row.zscalerIndex)}</td>
                  <td>{fmt(row.checkpointIndex)}</td>
                  <td>{fmt(row.securityMedianIndex)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>

      <p className="chart-note">{chartMetricNote}</p>
      <EvidenceLink ids={chartEvidenceIds} label="Chart sources" />
    </section>
  )
}

function fmt(value: number | null): string {
  if (value === null) return '—'
  return value.toFixed(1)
}
