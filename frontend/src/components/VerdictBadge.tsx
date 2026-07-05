import type { ActionTier } from "../types";

const STYLES: Record<ActionTier, string> = {
  allow: "bg-tier-allow/10 text-tier-allow border-tier-allow/30",
  review: "bg-tier-review/10 text-tier-review border-tier-review/30",
  block: "bg-tier-block/10 text-tier-block border-tier-block/30",
};

const LABELS: Record<ActionTier, string> = {
  allow: "Allowed",
  review: "Flagged for Review",
  block: "Blocked",
};

export default function VerdictBadge({ action }: { action: ActionTier }) {
  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${STYLES[action]}`}
    >
      {LABELS[action]}
    </span>
  );
}
