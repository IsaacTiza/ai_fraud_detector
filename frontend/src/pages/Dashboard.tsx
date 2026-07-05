import { useEffect, useState } from "react";
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";
import StatCard from "../components/StatCard";
import { getSummary, getTrend } from "../api/client";
import type { SummaryResponse, TrendPoint } from "../types";

export default function Dashboard() {
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getSummary(), getTrend()])
      .then(([s, t]) => {
        setSummary(s);
        setTrend(t.data); // backend returns { days, data: TrendPoint[] }, unwrap here
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-500">Loading dashboard...</div>;
  if (error) return <div className="text-tier-block">Error: {error}</div>;
  if (!summary) return null;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500">
          Overview of transaction monitoring and fraud detection.
        </p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Transactions" value={summary.total_transactions.toLocaleString()} />
        <StatCard label="Flagged Count" value={summary.flagged_count.toLocaleString()} />
        <StatCard label="Fraud Rate" value={`${(summary.fraud_rate * 100).toFixed(2)}%`} />
        <StatCard
          label="Avg Fraud Probability"
          value={summary.avg_fraud_probability.toFixed(3)}
        />
      </div>

      <div className="bg-surface rounded-xl border border-gray-100 shadow-sm p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Flagged Transactions Over Time</h2>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={trend}>
            <defs>
              <linearGradient id="fillFlagged" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#F97316" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#F97316" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Area
              type="monotone"
              dataKey="flagged"
              stroke="#F97316"
              fill="url(#fillFlagged)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
