import type { LineItem } from "../lib/api";
import { money } from "../lib/format";

export function LineItemsTable({ items }: { items: LineItem[] }) {
  if (!items.length) {
    return (
      <div className="rounded border border-dashed border-slate-300 p-4 text-sm text-slate-500">
        No line items yet.
      </div>
    );
  }
  return (
    <div className="overflow-auto rounded border border-slate-200 bg-white">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-100 text-xs uppercase text-slate-600">
          <tr>
            <th className="px-3 py-2">Type</th>
            <th className="px-3 py-2">Source</th>
            <th className="px-3 py-2">SKU/Code</th>
            <th className="px-3 py-2">Description</th>
            <th className="px-3 py-2">Qty</th>
            <th className="px-3 py-2">Unit</th>
            <th className="px-3 py-2">Unit Cost</th>
            <th className="px-3 py-2">Unit Sell</th>
            <th className="px-3 py-2">Total Sell</th>
            <th className="px-3 py-2">Notes</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-t border-slate-100">
              <td className="px-3 py-2">{item.line_type}</td>
              <td className="px-3 py-2">{item.source_type}</td>
              <td className="px-3 py-2">{item.sku}</td>
              <td className="px-3 py-2">{item.description}</td>
              <td className="px-3 py-2">{Number(item.quantity).toFixed(3)}</td>
              <td className="px-3 py-2">{item.unit}</td>
              <td className="px-3 py-2">{money(item.unit_cost)}</td>
              <td className="px-3 py-2">{money(item.unit_sell)}</td>
              <td className="px-3 py-2">{money(item.total_sell)}</td>
              <td className="px-3 py-2">{item.notes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
