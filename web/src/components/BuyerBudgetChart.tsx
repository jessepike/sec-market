import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { buyerBudgetAnnual } from '../data/market'
import { EvidenceLink } from './EvidenceLink'

export function BuyerBudgetChart() {
  return (
    <figure className="buyer-chart" aria-labelledby="buyer-chart-caption">
      <figcaption id="buyer-chart-caption">
        <strong>Buyer budgets (annual)</strong>
        <span>IANS average security-budget growth and security share of IT — separate from quarterly panel</span>
      </figcaption>
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={buyerBudgetAnnual} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} />
          <YAxis
            tick={{ fontSize: 12 }}
            domain={[0, 14]}
            label={{ value: 'Percent', angle: -90, position: 'insideLeft', offset: 8 }}
          />
          <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }} />
          <Legend />
          <Bar
            dataKey="budgetGrowth"
            name="Avg. security-budget growth"
            fill="#b45309"
            radius={[4, 4, 0, 0]}
          />
          <Line
            type="monotone"
            dataKey="securityShareIt"
            name="Security share of IT"
            stroke="#0f766e"
            strokeWidth={2}
            dot={{ r: 4 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
      <EvidenceLink ids="D1" />
    </figure>
  )
}
