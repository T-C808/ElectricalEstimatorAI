import type { Estimate } from "../lib/api";
import { money } from "../lib/format";

export function EstimateSummary({ estimate }: { estimate?: Estimate }) {
  if (!estimate) {
    return <div className="text-sm text-slate-500">No estimate selected.</div>;
  }
  const rows = [
    ["Material", estimate.material_subtotal],
    ["Labor", estimate.labor_subtotal],
    ["Overhead", estimate.overhead_total],
    ["Profit", estimate.profit_total],
    ["Contingency", estimate.contingency_total],
    ["Tax", estimate.tax_total],
    ["Total", estimate.grand_total],
  ];
  return (
    <div className="rounded border border-slate-200 bg-white">
      {rows.map(([label, value]) => (
        <div
          key={label}
          className="flex justify-between border-b border-slate-100 px-3 py-2 last:border-b-0"
        >
          <span className={label === "Total" ? "font-semibold" : ""}>
            {label}
          </span>
          <span className={label === "Total" ? "font-semibold" : ""}>
            {money(value)}
          </span>
        </div>
      ))}
    </div>
  );
}
