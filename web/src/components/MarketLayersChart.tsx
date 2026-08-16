import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { chartEvidenceIds, chartLayerPoints, chartMetricNote } from '../data/market'
import { derivedPanelRows } from '../data/derivePanel'
import { EvidenceLink } from './EvidenceLink'
import { BuyerBudgetChart } from './BuyerBudgetChart'

const SHARED_LOG_DOMAIN: [number, number] = [50, 1800]

const SMALL_MULTIPLES = [
  {
    key: 'infrastructure' as const,
    dataKey: 'infrastructure' as const,
    title: 'Infrastructure',
    subtitle: 'NVIDIA Data Center revenue',
    color: '#1d4ed8',
  },
  {
    key: 'hyperscaler' as const,
    dataKey: 'hyperscalerMedian' as const,
    title: 'Hyperscaler capex',
    subtitle: 'Median of Microsoft, Amazon, Alphabet',
    color: '#7c3aed',
  },
  {
    key: 'security' as const,
    dataKey: 'securityMedian' as const,
    title: 'Security vendors',
    subtitle: 'Median of CRWD, OKTA, FTNT, ZS, CHKP',
    color: '#0f766e',
  },
]

export function MarketLayersChart() {
  return (
    <section id="layers" className="chart-section" aria-labelledby="layers-heading">
      <div className="section-heading">
        <h2 id="layers-heading">Market layers</h2>
        <p>
          Quarterly indexed series (2023-Q1 = 100) derived from the frozen sparse panel — descriptive
          sequence only, not a fitted lag model.
        </p>
      </div>

        <p className="chart-shared-scale-caption">
          All three charts use the same log-scale index axis (50–1800; 2023-Q1 = 100) so proportional
          differences are visually honest — e.g. infrastructure near 18× vs. security near 2×.
        </p>

      <div className="chart-multiples" role="img" aria-label="Indexed quarterly market layers">
        {SMALL_MULTIPLES.map((series) => (
          <figure key={series.key} className="chart-multiple">
            <figcaption>
              <strong>{series.title}</strong>
              <span>{series.subtitle}</span>
            </figcaption>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartLayerPoints} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="quarter" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                <YAxis
                  scale="log"
                  domain={SHARED_LOG_DOMAIN}
                  tick={{ fontSize: 10 }}
                  allowDataOverflow
                  label={{
                    value: 'Index (log)',
                    angle: -90,
                    position: 'insideLeft',
                    offset: 4,
                    style: { fontSize: 10 },
                  }}
                />
                <Tooltip
                  contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
                  formatter={(value) => {
                    const num = typeof value === 'number' ? value : null
                    return [num === null ? '—' : num.toFixed(1), 'Index']
                  }}
                />
                <Line
                  type="monotone"
                  dataKey={series.dataKey}
                  name={series.title}
                  stroke={series.color}
                  strokeWidth={2}
                  dot={{ r: 2 }}
                  connectNulls={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </figure>
        ))}
      </div>

      <BuyerBudgetChart />

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
