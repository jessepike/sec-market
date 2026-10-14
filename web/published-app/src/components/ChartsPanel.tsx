import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { chartLayerPoints } from '../data/market'
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

/**
 * Recharts (and BuyerBudgetChart, which also depends on it) is the single
 * largest dependency in the bundle. This component is the only place that
 * imports it, and it is only ever reached through React.lazy() in
 * MarketLayersChart, so it code-splits into its own chunk instead of
 * shipping in the initial bundle.
 */
export default function ChartsPanel() {
  return (
    <>
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
    </>
  )
}
