import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { chartEvidenceIds, chartMetricNote, marketLayerSeries } from '../data/market'
import { EvidenceLink } from './EvidenceLink'

const SERIES = [
  { key: 'infrastructure', name: 'Infrastructure (NVIDIA DC)', color: '#1d4ed8' },
  { key: 'hyperscaler', name: 'Hyperscaler capex (median)', color: '#7c3aed' },
  { key: 'security', name: 'Security vendors (median)', color: '#0f766e' },
  { key: 'buyerBudget', name: 'Buyer budget growth (%)', color: '#b45309' },
] as const

export function MarketLayersChart() {
  return (
    <section id="layers" className="chart-section" aria-labelledby="layers-heading">
      <div className="section-heading">
        <h2 id="layers-heading">Market layers</h2>
        <p>
          Descriptive sequence across infrastructure, hyperscaler investment, security vendor
          outcomes, and buyer budgets — not a fitted lag model.
        </p>
      </div>
      <div className="chart-panel" role="img" aria-label="Indexed market layer trends from 2023-Q1 to 2026-Q1">
        <ResponsiveContainer width="100%" height={360}>
          <LineChart data={marketLayerSeries} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="quarter" tick={{ fontSize: 12 }} interval="preserveStartEnd" />
            <YAxis
              yAxisId="index"
              tick={{ fontSize: 12 }}
              label={{ value: 'Index (2023-Q1 = 100)', angle: -90, position: 'insideLeft', offset: 12 }}
            />
            <YAxis
              yAxisId="budget"
              orientation="right"
              tick={{ fontSize: 12 }}
              domain={[0, 12]}
              label={{ value: 'Budget growth %', angle: 90, position: 'insideRight', offset: 12 }}
            />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }}
              formatter={(value, name) => {
                const num = typeof value === 'number' ? value : null
                const label = String(name)
                return [
                  num === null ? '—' : label === 'Buyer budget growth (%)' ? `${num}%` : num,
                  label,
                ]
              }}
            />
            <Legend />
            {SERIES.slice(0, 3).map((series) => (
              <Line
                key={series.key}
                yAxisId="index"
                type="monotone"
                dataKey={series.key}
                name={series.name}
                stroke={series.color}
                strokeWidth={2}
                dot={{ r: 2 }}
                connectNulls={false}
              />
            ))}
            <Line
              yAxisId="budget"
              type="monotone"
              dataKey="buyerBudget"
              name="Buyer budget growth (%)"
              stroke="#b45309"
              strokeWidth={2}
              strokeDasharray="6 4"
              dot={{ r: 3 }}
              connectNulls={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="chart-note">{chartMetricNote}</p>
      <EvidenceLink ids={chartEvidenceIds} label="Chart sources and definitions" />
    </section>
  )
}
