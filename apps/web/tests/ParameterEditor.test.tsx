import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EstimateSummary } from "../src/components/EstimateSummary";
import { defaultsForParameters, validateParameters } from "../src/components/ParameterEditor";
import { ReviewFlags } from "../src/components/ReviewFlags";
import type { Estimate } from "../src/lib/api";

describe("estimate builder support components", () => {
  it("validates required assembly parameters", () => {
    const definitions = [
      { name: "feeder_length_ft", type: "number" as const, required: true },
      { name: "conduit_type", type: "enum" as const, required: true, options: ["EMT", "PVC"] },
      { name: "shutdown_required", type: "boolean" as const, required: true, default: false }
    ];
    const values = defaultsForParameters(definitions);
    const errors = validateParameters(definitions, values);
    expect(errors).toEqual({ feeder_length_ft: "Required", conduit_type: "Required" });
  });

  it("renders calculation totals", () => {
    render(<EstimateSummary estimate={{ grand_total: "1234.56", material_subtotal: "500", labor_subtotal: "400", overhead_total: "90", profit_total: "150", contingency_total: "94.56", tax_total: "0" } as Estimate} />);
    expect(screen.getByText("$1,234.56")).toBeInTheDocument();
  });

  it("renders review flags", () => {
    render(
      <ReviewFlags
        flags={[
          {
            id: "1",
            flag_code: "SHUTDOWN_REQUIRED",
            severity: "warning",
            message: "Shutdown required. Confirm schedule and utility requirements."
          }
        ]}
      />
    );
    expect(screen.getByText(/Shutdown required/)).toBeInTheDocument();
  });
});
