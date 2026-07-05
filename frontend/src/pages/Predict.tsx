import { useState } from "react";
import VerdictBadge from "../components/VerdictBadge";
import { predictTransaction } from "../api/client";
import type { TransactionInput, PredictResponse } from "../types";

const V_FIELDS: (keyof TransactionInput)[] = [
  "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10",
  "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19", "v20",
  "v21", "v22", "v23", "v24", "v25", "v26", "v27", "v28",
];

const initialForm: TransactionInput = {
  time: 0,
  amount: 0,
  ...Object.fromEntries(V_FIELDS.map((f) => [f, 0])),
} as TransactionInput;

/**
 * Fixed sample vectors for one-click demo testing.
 * These are representative, hand-constructed feature values chosen to sit
 * in low, mid, and high-magnitude regions of the trained model's decision
 * space — they are illustrative, not verbatim rows from the source dataset.
 * Purpose: let a reviewer test the system without typing 30 numeric fields
 * or needing to understand PCA components to produce a meaningful test case.
 */
const SAMPLES: { label: string; description: string; data: TransactionInput }[] = [
  {
    label: "Typical Transaction",
    description: "Small amount, low-magnitude features — expected: Allow",
    data: {
      time: 50000, amount: 25.0,
      v1: -1.2, v2: 0.8, v3: 1.5, v4: 0.3, v5: -0.7, v6: 0.2, v7: -0.5, v8: 0.1,
      v9: 0.4, v10: -0.3, v11: 0.6, v12: -0.9, v13: 0.2, v14: -1.1, v15: 0.5,
      v16: -0.4, v17: 0.3, v18: -0.2, v19: 0.7, v20: -0.1, v21: 0.05, v22: 0.4,
      v23: -0.1, v24: 0.3, v25: 0.2, v26: -0.3, v27: 0.1, v28: 0.02,
    },
  },
  {
    label: "Borderline Transaction",
    description: "Moderate amount, mixed-magnitude features — expected: Allow or Review",
    data: {
      time: 65000, amount: 180.0,
      v1: -3.5, v2: 2.4, v3: -3.8, v4: 2.1, v5: -1.6, v6: 0.6, v7: -2.5, v8: 1.4,
      v9: -1.8, v10: -3.1, v11: 2.2, v12: -3.4, v13: 0.5, v14: -3.6, v15: 0.2,
      v16: -1.7, v17: -3.0, v18: -1.5, v19: 0.6, v20: 0.4, v21: 0.3, v22: -0.2,
      v23: 0.2, v24: -0.1, v25: 0.1, v26: -0.2, v27: 0.4, v28: 0.2,
    },
  },
  {
    label: "High-Risk Transaction",
    description: "Large amount, extreme-magnitude features — expected: Block",
    data: {
      time: 80000, amount: 500.0,
      v1: -8.5, v2: 6.2, v3: -9.1, v4: 5.8, v5: -3.2, v6: 1.1, v7: -6.4, v8: 3.9,
      v9: -4.2, v10: -7.8, v11: 5.6, v12: -8.9, v13: 0.9, v14: -9.5, v15: 0.3,
      v16: -4.1, v17: -8.2, v18: -3.6, v19: 1.2, v20: 0.8, v21: 0.6, v22: -0.3,
      v23: 0.4, v24: -0.2, v25: 0.1, v26: -0.3, v27: 0.9, v28: 0.4,
    },
  },
];

export default function Predict() {
  const [form, setForm] = useState<TransactionInput>(initialForm);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  function handleChange(field: keyof TransactionInput, value: string) {
    setForm((prev) => ({ ...prev, [field]: parseFloat(value) || 0 }));
  }

  function loadSample(data: TransactionInput) {
    setForm(data);
    setResult(null);
    setError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const res = await predictTransaction(form);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Predict</h1>
        <p className="text-sm text-gray-500">
          Load a sample transaction or enter values manually, then run a prediction.
        </p>
      </div>

      <div className="bg-surface rounded-xl border border-gray-100 shadow-sm p-6">
        <h2 className="font-semibold text-gray-900 mb-1">Sample Transactions</h2>
        <p className="text-sm text-gray-500 mb-4">
          Click a card to load pre-built feature values — no manual data entry needed.
        </p>
        <div className="grid grid-cols-3 gap-3">
          {SAMPLES.map((sample) => (
            <button
              key={sample.label}
              type="button"
              onClick={() => loadSample(sample.data)}
              className="text-left border border-gray-200 rounded-lg p-4 hover:border-primary hover:bg-primary/5 transition-colors"
            >
              <div className="font-semibold text-sm text-gray-900">{sample.label}</div>
              <div className="text-xs text-gray-500 mt-1">{sample.description}</div>
              <div className="text-xs text-gray-400 mt-2">
                Amount: ${sample.data.amount.toFixed(2)}
              </div>
            </button>
          ))}
        </div>
      </div>

      <form
        onSubmit={handleSubmit}
        className="bg-surface rounded-xl border border-gray-100 shadow-sm p-6 flex flex-col gap-4"
      >
        <div className="grid grid-cols-2 gap-4">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700">Time</span>
            <input
              type="number"
              step="any"
              value={form.time}
              onChange={(e) => handleChange("time", e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700">Amount</span>
            <input
              type="number"
              step="any"
              value={form.amount}
              onChange={(e) => handleChange("amount", e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </label>
        </div>

        <button
          type="button"
          onClick={() => setShowAdvanced((v) => !v)}
          className="text-sm text-primary font-medium self-start hover:underline"
        >
          {showAdvanced ? "Hide" : "Show"} advanced feature values (V1–V28)
        </button>

        {showAdvanced && (
          <div className="grid grid-cols-4 gap-3">
            {V_FIELDS.map((field) => (
              <label key={field} className="flex flex-col gap-1 text-xs">
                <span className="font-medium text-gray-500 uppercase">{field}</span>
                <input
                  type="number"
                  step="any"
                  value={form[field]}
                  onChange={(e) => handleChange(field, e.target.value)}
                  className="border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary/30"
                />
              </label>
            ))}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="self-start bg-primary hover:bg-primary-hover text-white font-semibold px-5 py-2.5 rounded-lg transition-colors disabled:opacity-50"
        >
          {submitting ? "Predicting..." : "Run Prediction"}
        </button>
      </form>

      {error && <div className="text-tier-block text-sm">{error}</div>}

      {result && (
        <div className="bg-surface rounded-xl border border-gray-100 shadow-sm p-6 flex items-center gap-4">
          <VerdictBadge action={result.action} />
          <span className="text-sm text-gray-600">
            Fraud probability: <strong>{result.fraud_probability.toFixed(4)}</strong>
          </span>
        </div>
      )}
    </div>
  );
}
