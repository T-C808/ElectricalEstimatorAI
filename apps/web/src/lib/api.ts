export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export type Customer = {
  id: string;
  company_name: string;
  contact_name?: string;
  email?: string;
  phone?: string;
  billing_address?: string;
  notes?: string;
  updated_at: string;
};

export type Job = {
  id: string;
  customer_id: string;
  job_name: string;
  site_address?: string;
  site_contact?: string;
  job_type?: string;
  status: string;
  notes?: string;
  updated_at: string;
};

export type Material = {
  id: string;
  sku: string;
  name: string;
  category?: string;
  unit: string;
  unit_cost: string;
  default_markup_percent: string;
  supplier?: string;
  manufacturer?: string;
  active: boolean;
};

export type LaborUnit = {
  id: string;
  code: string;
  name: string;
  description?: string;
  base_hours: string;
  crew_size: string;
  difficulty_factor: string;
  active: boolean;
};

export type MarginProfile = {
  id: string;
  name: string;
  material_markup_percent: string;
  labor_rate_per_hour: string;
  overhead_percent: string;
  profit_percent: string;
  contingency_percent: string;
  tax_percent: string;
  minimum_margin_percent: string;
  active: boolean;
};

export type Assembly = {
  id: string;
  code: string;
  name: string;
  version: number;
  category?: string;
  parameters: ParameterDefinition[];
  assumptions: string[];
  exclusions: string[];
  active: boolean;
};

export type AssemblyDetail = Assembly & {
  materials: Array<{
    id: string;
    quantity_formula: string;
    unit?: string;
    material: Material;
  }>;
  labor: Array<{ id: string; hours_formula: string; labor_unit: LaborUnit }>;
  rules: Array<{
    id: string;
    name: string;
    rule_json: Record<string, unknown>;
    active: boolean;
  }>;
};

export type ParameterDefinition = {
  name: string;
  type: "number" | "boolean" | "enum" | "text";
  required?: boolean;
  default?: string | number | boolean;
  options?: string[];
};

export type EstimateAssembly = {
  id: string;
  assembly_code: string;
  assembly_version: number;
  parameters: Record<string, unknown>;
  assembly: Assembly;
};

export type LineItem = {
  id: string;
  source_type: string;
  line_type: string;
  sku?: string;
  description: string;
  quantity: string;
  unit?: string;
  unit_cost: string;
  unit_sell: string;
  total_sell: string;
  labor_hours?: string;
  notes?: string;
};

export type EstimateNote = {
  id: string;
  note_type:
    | "assumption"
    | "exclusion"
    | "internal_note"
    | "client_note"
    | "disclaimer";
  note: string;
};

export type ReviewFlag = {
  id: string;
  flag_code: string;
  severity: "info" | "warning" | "critical";
  message: string;
};

export type Estimate = {
  id: string;
  job_id: string;
  margin_profile_id: string;
  status: string;
  material_subtotal: string;
  labor_subtotal: string;
  overhead_total: string;
  profit_total: string;
  contingency_total: string;
  tax_total: string;
  grand_total: string;
  assemblies?: EstimateAssembly[];
  line_items?: LineItem[];
  notes?: EstimateNote[];
  review_flags?: ReviewFlag[];
};

export type EstimateExport = {
  id: string;
  export_type: string;
  file_name: string;
  storage_key?: string;
};

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(
      typeof error.detail === "string" ? error.detail : "Request failed",
    );
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const downloadUrl = (exportId: string) =>
  `${API_BASE_URL}/exports/${exportId}/download`;
