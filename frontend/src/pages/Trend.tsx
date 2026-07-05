import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { getTrend } from "../api/client";
import type { TrendPoint } from "../types";

export default function Trend() {
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTrend()
      .then((res) => setTrend(res.data)) // unwrap { days, data }
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-500">Loading trend...</div>;
  if (error) return <div className="text-tier-block">Error: {error}</div>;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Trend</h1>
        <p className="text-sm text-gray-500">
          Flagged vs. total transactions over time.
        </p>
      </div>

      <div className="bg-surface rounded-xl border border-gray-100 shadow-sm p-6">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="total"
              stroke="#9CA3AF"
              strokeWidth={2}
              name="Total Transactions"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="flagged"
              stroke="#F97316"
              strokeWidth={2}
              name="Flagged Transactions"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
