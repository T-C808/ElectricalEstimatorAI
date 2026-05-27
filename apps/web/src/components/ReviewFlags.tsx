import { AlertTriangle, CheckCircle2, Info } from "lucide-react";

import type { ReviewFlag } from "../lib/api";

const iconBySeverity = {
  info: Info,
  warning: AlertTriangle,
  critical: AlertTriangle,
};

export function ReviewFlags({ flags }: { flags: ReviewFlag[] }) {
  if (!flags.length) {
    return (
      <div className="flex items-center gap-2 rounded border border-green-300 bg-green-50 px-3 py-2 text-sm text-green-800">
        <CheckCircle2 size={16} /> No review flags.
      </div>
    );
  }
  return (
    <div className="space-y-2">
      {flags.map((flag) => {
        const Icon = iconBySeverity[flag.severity];
        const color =
          flag.severity === "critical"
            ? "border-red-300 bg-red-50 text-red-800"
            : flag.severity === "warning"
              ? "border-amber-300 bg-amber-50 text-amber-900"
              : "border-blue-300 bg-blue-50 text-blue-800";
        return (
          <div
            key={flag.id ?? flag.flag_code}
            className={`flex gap-2 rounded border px-3 py-2 text-sm ${color}`}
          >
            <Icon size={16} className="mt-0.5 shrink-0" />
            <div>
              <div className="font-semibold">{flag.severity.toUpperCase()}</div>
              <div>{flag.message}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
