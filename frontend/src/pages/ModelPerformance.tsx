import { useEffect, useState } from "react";
import StatCard from "../components/StatCard";
import { getModelPerformance } from "../api/client";
import type { ModelPerformanceResponse } from "../types";

export default function ModelPerformance() {
  const [data, setData] = useState<ModelPerformanceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getModelPerformance()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-500">Loading model performance...</div>;
  if (error) return <div className="text-tier-block">Error: {error}</div>;
  if (!data) return null;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Model Performance</h1>
        <p className="text-sm text-gray-500">Model version: {data.model_version}</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Precision" value={data.precision.toFixed(3)} />
        <StatCard label="Recall" value={data.recall.toFixed(3)} />
        <StatCard label="F1 Score" value={data.f1.toFixed(3)} />
        <StatCard label="ROC AUC" value={data.roc_auc.toFixed(3)} />
      </div>

      <div className="bg-surface rounded-xl border border-gray-100 shadow-sm p-6 text-sm text-gray-500">
        Note: seed data used for demo purposes is deliberately oversampled for
        fraud representation relative to the true population rate (~0.17%),
        to support visible testing across all three action tiers. Production
        traffic distribution would differ significantly.
      </div>
    </div>
  );
}
