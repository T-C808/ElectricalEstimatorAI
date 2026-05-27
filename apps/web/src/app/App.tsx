import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BookOpen,
  Boxes,
  Calculator,
  ClipboardList,
  Home,
  Plus,
  RefreshCw,
  Users,
} from "lucide-react";
import type * as React from "react";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { EstimateSummary } from "../components/EstimateSummary";
import { LineItemsTable } from "../components/LineItemsTable";
import {
  defaultsForParameters,
  ParameterEditor,
  type ParameterValues,
  validateParameters,
} from "../components/ParameterEditor";
import { ReviewFlags } from "../components/ReviewFlags";
import {
  apiFetch,
  downloadUrl,
  type Assembly,
  type AssemblyDetail,
  type Customer,
  type Estimate,
  type EstimateExport,
  type Job,
  type LaborUnit,
  type MarginProfile,
  type Material,
} from "../lib/api";
import { money, percent, shortId } from "../lib/format";

type Page =
  | "dashboard"
  | "customers"
  | "jobs"
  | "catalog"
  | "assemblies"
  | "estimates";

const navItems: Array<{ page: Page; label: string; icon: typeof Home }> = [
  { page: "dashboard", label: "Dashboard", icon: Home },
  { page: "customers", label: "Customers", icon: Users },
  { page: "jobs", label: "Jobs", icon: ClipboardList },
  { page: "catalog", label: "Catalog", icon: Boxes },
  { page: "assemblies", label: "Assemblies", icon: BookOpen },
  { page: "estimates", label: "Estimate Builder", icon: Calculator },
];

export function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const queryClient = useQueryClient();
  const seedMutation = useMutation({
    mutationFn: () =>
      apiFetch<{ status: string }>("/dev/seed", { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries(),
  });

  return (
    <div className="min-h-screen bg-panel text-ink">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white p-4 md:block">
        <div className="mb-8">
          <div className="text-lg font-semibold">Electrical Estimator</div>
          <div className="text-xs text-slate-500">Estimate + BOM V1</div>
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.page}
                className={`focus-ring flex w-full items-center gap-2 rounded px-3 py-2 text-left text-sm ${
                  page === item.page
                    ? "bg-conduit text-white"
                    : "hover:bg-slate-100"
                }`}
                onClick={() => setPage(item.page)}
              >
                <Icon size={16} /> {item.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="md:pl-64">
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3">
          <div>
            <div className="text-sm text-slate-500">Local V1</div>
            <h1 className="text-xl font-semibold">
              {navItems.find((item) => item.page === page)?.label}
            </h1>
          </div>
          <button
            className="focus-ring inline-flex items-center gap-2 rounded bg-copper px-3 py-2 text-sm font-medium text-white"
            onClick={() => seedMutation.mutate()}
          >
            <RefreshCw size={16} /> Seed Data
          </button>
        </header>

        <div className="grid grid-cols-2 gap-2 border-b border-slate-200 bg-white p-2 md:hidden">
          {navItems.map((item) => (
            <button
              key={item.page}
              className={`focus-ring rounded px-3 py-2 text-sm ${page === item.page ? "bg-conduit text-white" : "bg-slate-100"}`}
              onClick={() => setPage(item.page)}
            >
              {item.label}
            </button>
          ))}
        </div>

        <section className="p-4 lg:p-6">
          {page === "dashboard" ? <Dashboard onNavigate={setPage} /> : null}
          {page === "customers" ? <CustomersPage /> : null}
          {page === "jobs" ? <JobsPage /> : null}
          {page === "catalog" ? <CatalogPage /> : null}
          {page === "assemblies" ? <AssembliesPage /> : null}
          {page === "estimates" ? <EstimateBuilder /> : null}
        </section>
      </main>
    </div>
  );
}

function Dashboard({ onNavigate }: { onNavigate: (page: Page) => void }) {
  const jobs = useQuery({
    queryKey: ["jobs"],
    queryFn: () => apiFetch<Job[]>("/jobs"),
  });
  const estimates = useQuery({
    queryKey: ["estimates"],
    queryFn: () => apiFetch<Estimate[]>("/estimates"),
  });
  const reviewCount = (estimates.data ?? []).filter(
    (estimate) => estimate.status === "review_required",
  ).length;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Recent jobs" value={jobs.data?.length ?? 0} />
        <Metric label="Estimates" value={estimates.data?.length ?? 0} />
        <Metric label="Need review" value={reviewCount} tone="warning" />
      </div>
      <div className="flex flex-wrap gap-2">
        <button
          className="focus-ring rounded bg-conduit px-3 py-2 text-sm font-medium text-white"
          onClick={() => onNavigate("jobs")}
        >
          New Job
        </button>
        <button
          className="focus-ring rounded bg-copper px-3 py-2 text-sm font-medium text-white"
          onClick={() => onNavigate("estimates")}
        >
          New Estimate
        </button>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Recent Jobs">
          <SimpleTable
            rows={(jobs.data ?? [])
              .slice(0, 6)
              .map((job) => [job.job_name, job.status, job.site_address ?? ""])}
            empty="No jobs yet."
          />
        </Panel>
        <Panel title="Recent Estimates">
          <SimpleTable
            rows={(estimates.data ?? [])
              .slice(0, 6)
              .map((estimate) => [
                shortId(estimate.id),
                estimate.status,
                money(estimate.grand_total),
              ])}
            empty="No estimates yet."
          />
        </Panel>
      </div>
    </div>
  );
}

function CustomersPage() {
  const queryClient = useQueryClient();
  const customers = useQuery({
    queryKey: ["customers"],
    queryFn: () => apiFetch<Customer[]>("/customers"),
  });
  const form = useForm<CustomerFormValues>({
    resolver: zodResolver(customerSchema),
    defaultValues: {
      company_name: "",
      contact_name: "",
      email: "",
      phone: "",
      billing_address: "",
      notes: "",
    },
  });
  const mutation = useMutation({
    mutationFn: (values: CustomerFormValues) =>
      apiFetch<Customer>("/customers", {
        method: "POST",
        body: JSON.stringify(values),
      }),
    onSuccess: () => {
      form.reset();
      queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
  });

  return (
    <div className="grid gap-4 lg:grid-cols-[360px_1fr]">
      <Panel title="Create Customer">
        <form
          className="space-y-3"
          onSubmit={form.handleSubmit((values) => mutation.mutate(values))}
        >
          <TextInput
            label="Company"
            error={form.formState.errors.company_name?.message}
            {...form.register("company_name")}
          />
          <TextInput label="Contact" {...form.register("contact_name")} />
          <TextInput label="Email" {...form.register("email")} />
          <TextInput label="Phone" {...form.register("phone")} />
          <TextArea
            label="Billing address"
            {...form.register("billing_address")}
          />
          <TextArea label="Notes" {...form.register("notes")} />
          <SubmitButton label="Create Customer" pending={mutation.isPending} />
        </form>
      </Panel>
      <Panel title="Customers">
        <DataTable
          headers={["Company", "Contact", "Phone", "Email", "Updated"]}
          rows={(customers.data ?? []).map((customer) => [
            customer.company_name,
            customer.contact_name ?? "",
            customer.phone ?? "",
            customer.email ?? "",
            new Date(customer.updated_at).toLocaleDateString(),
          ])}
          empty="No customers yet. Create customer."
        />
      </Panel>
    </div>
  );
}

function JobsPage() {
  const queryClient = useQueryClient();
  const customers = useQuery({
    queryKey: ["customers"],
    queryFn: () => apiFetch<Customer[]>("/customers"),
  });
  const jobs = useQuery({
    queryKey: ["jobs"],
    queryFn: () => apiFetch<Job[]>("/jobs"),
  });
  const form = useForm<JobFormValues>({
    resolver: zodResolver(jobSchema),
    defaultValues: {
      customer_id: "",
      job_name: "",
      site_address: "",
      site_contact: "",
      job_type: "",
      status: "draft",
      notes: "",
    },
  });
  const mutation = useMutation({
    mutationFn: (values: JobFormValues) =>
      apiFetch<Job>("/jobs", { method: "POST", body: JSON.stringify(values) }),
    onSuccess: () => {
      form.reset({
        customer_id: "",
        job_name: "",
        site_address: "",
        site_contact: "",
        job_type: "",
        status: "draft",
        notes: "",
      });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  return (
    <div className="grid gap-4 lg:grid-cols-[360px_1fr]">
      <Panel title="Create Job">
        <form
          className="space-y-3"
          onSubmit={form.handleSubmit((values) => mutation.mutate(values))}
        >
          <SelectInput
            label="Customer"
            error={form.formState.errors.customer_id?.message}
            {...form.register("customer_id")}
          >
            <option value="">Select customer</option>
            {(customers.data ?? []).map((customer) => (
              <option key={customer.id} value={customer.id}>
                {customer.company_name}
              </option>
            ))}
          </SelectInput>
          <TextInput
            label="Job name"
            error={form.formState.errors.job_name?.message}
            {...form.register("job_name")}
          />
          <TextInput label="Site address" {...form.register("site_address")} />
          <TextInput label="Site contact" {...form.register("site_contact")} />
          <TextInput label="Job type" {...form.register("job_type")} />
          <SelectInput label="Status" {...form.register("status")}>
            {[
              "draft",
              "estimating",
              "review_required",
              "approved",
              "sent",
              "won",
              "lost",
              "archived",
            ].map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </SelectInput>
          <TextArea label="Notes" {...form.register("notes")} />
          <SubmitButton label="Create Job" pending={mutation.isPending} />
        </form>
      </Panel>
      <Panel title="Jobs">
        <DataTable
          headers={["Job", "Status", "Site", "Updated"]}
          rows={(jobs.data ?? []).map((job) => [
            job.job_name,
            job.status,
            job.site_address ?? "",
            new Date(job.updated_at).toLocaleDateString(),
          ])}
          empty="No jobs yet. Create job."
        />
      </Panel>
    </div>
  );
}

function CatalogPage() {
  const [tab, setTab] = useState<"materials" | "labor" | "margins">(
    "materials",
  );
  const materials = useQuery({
    queryKey: ["materials"],
    queryFn: () => apiFetch<Material[]>("/materials"),
  });
  const labor = useQuery({
    queryKey: ["labor-units"],
    queryFn: () => apiFetch<LaborUnit[]>("/labor-units"),
  });
  const margins = useQuery({
    queryKey: ["margin-profiles"],
    queryFn: () => apiFetch<MarginProfile[]>("/margin-profiles"),
  });

  return (
    <div className="space-y-4">
      <div className="inline-flex rounded border border-slate-200 bg-white p-1">
        {(["materials", "labor", "margins"] as const).map((item) => (
          <button
            key={item}
            className={`focus-ring rounded px-3 py-2 text-sm capitalize ${tab === item ? "bg-conduit text-white" : ""}`}
            onClick={() => setTab(item)}
          >
            {item}
          </button>
        ))}
      </div>
      {tab === "materials" ? (
        <Panel title="Materials">
          <DataTable
            headers={[
              "SKU",
              "Name",
              "Category",
              "Unit",
              "Unit Cost",
              "Markup",
              "Supplier",
              "Active",
            ]}
            rows={(materials.data ?? []).map((item) => [
              item.sku,
              item.name,
              item.category ?? "",
              item.unit,
              money(item.unit_cost),
              percent(item.default_markup_percent),
              item.supplier ?? "",
              item.active ? "Yes" : "No",
            ])}
            empty="No materials seeded."
          />
        </Panel>
      ) : null}
      {tab === "labor" ? (
        <Panel title="Labor Units">
          <DataTable
            headers={[
              "Code",
              "Name",
              "Base Hours",
              "Crew",
              "Difficulty",
              "Active",
            ]}
            rows={(labor.data ?? []).map((item) => [
              item.code,
              item.name,
              item.base_hours,
              item.crew_size,
              item.difficulty_factor,
              item.active ? "Yes" : "No",
            ])}
            empty="No labor units seeded."
          />
        </Panel>
      ) : null}
      {tab === "margins" ? (
        <Panel title="Margin Profiles">
          <DataTable
            headers={[
              "Name",
              "Material Markup",
              "Labor Rate",
              "Overhead",
              "Profit",
              "Contingency",
              "Tax",
              "Active",
            ]}
            rows={(margins.data ?? []).map((item) => [
              item.name,
              percent(item.material_markup_percent),
              money(item.labor_rate_per_hour),
              percent(item.overhead_percent),
              percent(item.profit_percent),
              percent(item.contingency_percent),
              percent(item.tax_percent),
              item.active ? "Yes" : "No",
            ])}
            empty="No margin profiles seeded."
          />
        </Panel>
      ) : null}
    </div>
  );
}

function AssembliesPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const assemblies = useQuery({
    queryKey: ["assemblies"],
    queryFn: () => apiFetch<Assembly[]>("/assemblies"),
  });
  const detail = useQuery({
    queryKey: ["assembly", selectedId],
    queryFn: () => apiFetch<AssemblyDetail>(`/assemblies/${selectedId}`),
    enabled: Boolean(selectedId),
  });

  return (
    <div className="grid gap-4 lg:grid-cols-[420px_1fr]">
      <Panel title="Assembly Library">
        <div className="space-y-2">
          {(assemblies.data ?? []).map((assembly) => (
            <button
              key={assembly.id}
              className={`focus-ring w-full rounded border px-3 py-2 text-left text-sm ${
                selectedId === assembly.id
                  ? "border-conduit bg-blue-50"
                  : "border-slate-200 bg-white"
              }`}
              onClick={() => setSelectedId(assembly.id)}
            >
              <div className="font-semibold">{assembly.code}</div>
              <div className="text-slate-600">
                {assembly.name} · v{assembly.version} · {assembly.category}
              </div>
            </button>
          ))}
        </div>
      </Panel>
      <Panel title="Assembly Detail">
        {detail.data ? (
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold">{detail.data.name}</h2>
              <div className="text-sm text-slate-500">
                {detail.data.code} · version {detail.data.version}
              </div>
            </div>
            <DetailList
              title="Parameters"
              items={detail.data.parameters.map(
                (p) => `${p.name}${p.required ? " *" : ""}`,
              )}
            />
            <DetailList
              title="Base Materials"
              items={detail.data.materials.map(
                (item) =>
                  `${item.material.sku}: ${item.quantity_formula} ${item.unit ?? item.material.unit}`,
              )}
            />
            <DetailList
              title="Base Labor"
              items={detail.data.labor.map(
                (item) => `${item.labor_unit.code}: ${item.hours_formula}`,
              )}
            />
            <DetailList
              title="Rules"
              items={detail.data.rules.map((rule) => rule.name)}
            />
            <DetailList title="Assumptions" items={detail.data.assumptions} />
            <DetailList title="Exclusions" items={detail.data.exclusions} />
          </div>
        ) : (
          <div className="text-sm text-slate-500">
            Select an assembly to inspect its parameters, materials, labor,
            rules, assumptions, and exclusions.
          </div>
        )}
      </Panel>
    </div>
  );
}

function EstimateBuilder() {
  const queryClient = useQueryClient();
  const [estimateId, setEstimateId] = useState<string>("");
  const [selectedAssemblyId, setSelectedAssemblyId] = useState<string>("");
  const [parameterValues, setParameterValues] = useState<ParameterValues>({});
  const [parameterErrors, setParameterErrors] = useState<
    Record<string, string>
  >({});
  const [lastExport, setLastExport] = useState<EstimateExport | null>(null);

  const customers = useQuery({
    queryKey: ["customers"],
    queryFn: () => apiFetch<Customer[]>("/customers"),
  });
  const jobs = useQuery({
    queryKey: ["jobs"],
    queryFn: () => apiFetch<Job[]>("/jobs"),
  });
  const margins = useQuery({
    queryKey: ["margin-profiles"],
    queryFn: () => apiFetch<MarginProfile[]>("/margin-profiles"),
  });
  const assemblies = useQuery({
    queryKey: ["assemblies"],
    queryFn: () => apiFetch<Assembly[]>("/assemblies"),
  });
  const estimates = useQuery({
    queryKey: ["estimates"],
    queryFn: () => apiFetch<Estimate[]>("/estimates"),
  });
  const estimate = useQuery({
    queryKey: ["estimate", estimateId],
    queryFn: () => apiFetch<Estimate>(`/estimates/${estimateId}`),
    enabled: Boolean(estimateId),
  });

  const selectedAssembly = useMemo(
    () =>
      (assemblies.data ?? []).find(
        (assembly) => assembly.id === selectedAssemblyId,
      ),
    [assemblies.data, selectedAssemblyId],
  );

  const createEstimateForm = useForm<CreateEstimateValues>({
    resolver: zodResolver(createEstimateSchema),
    defaultValues: { job_id: "", margin_profile_id: "" },
  });

  useEffect(() => {
    if (!createEstimateForm.getValues("job_id") && jobs.data?.[0]?.id) {
      createEstimateForm.setValue("job_id", jobs.data[0].id);
    }
    if (
      !createEstimateForm.getValues("margin_profile_id") &&
      margins.data?.[0]?.id
    ) {
      createEstimateForm.setValue("margin_profile_id", margins.data[0].id);
    }
  }, [createEstimateForm, jobs.data, margins.data]);

  const createEstimate = useMutation({
    mutationFn: (values: CreateEstimateValues) =>
      apiFetch<Estimate>(`/jobs/${values.job_id}/estimates`, {
        method: "POST",
        body: JSON.stringify({ margin_profile_id: values.margin_profile_id }),
      }),
    onSuccess: (created) => {
      setEstimateId(created.id);
      queryClient.invalidateQueries({ queryKey: ["estimates"] });
    },
  });

  const addAssembly = useMutation({
    mutationFn: () =>
      apiFetch(`/estimates/${estimateId}/assemblies`, {
        method: "POST",
        body: JSON.stringify({
          assembly_id: selectedAssemblyId,
          parameters: coerceParameterValues(parameterValues),
        }),
      }),
    onSuccess: () => {
      setParameterErrors({});
      queryClient.invalidateQueries({ queryKey: ["estimate", estimateId] });
    },
  });

  const calculate = useMutation({
    mutationFn: () =>
      apiFetch(`/estimates/${estimateId}/calculate`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["estimate", estimateId] });
      queryClient.invalidateQueries({ queryKey: ["estimates"] });
    },
  });

  const exportMutation = useMutation({
    mutationFn: (type: "supplier-csv" | "internal-csv" | "client-pdf") =>
      apiFetch<EstimateExport>(`/estimates/${estimateId}/exports/${type}`, {
        method: "POST",
      }),
    onSuccess: (created) => setLastExport(created),
  });

  function handleAssemblyChange(id: string) {
    setSelectedAssemblyId(id);
    const assembly = (assemblies.data ?? []).find((item) => item.id === id);
    setParameterValues(
      assembly ? defaultsForParameters(assembly.parameters) : {},
    );
    setParameterErrors({});
  }

  function handleAddAssembly() {
    if (!selectedAssembly || !estimateId) return;
    const errors = validateParameters(
      selectedAssembly.parameters,
      parameterValues,
    );
    setParameterErrors(errors);
    if (Object.keys(errors).length === 0) {
      addAssembly.mutate();
    }
  }

  const currentJob = (jobs.data ?? []).find(
    (job) => job.id === estimate.data?.job_id,
  );
  const currentCustomer = (customers.data ?? []).find(
    (customer) => customer.id === currentJob?.customer_id,
  );
  const assumptions =
    estimate.data?.notes?.filter((note) => note.note_type === "assumption") ??
    [];
  const exclusions =
    estimate.data?.notes?.filter((note) => note.note_type === "exclusion") ??
    [];

  return (
    <div className="space-y-4">
      <div className="grid gap-4 xl:grid-cols-[360px_1fr_320px]">
        <Panel title="Create or Select Estimate">
          <form
            className="space-y-3"
            onSubmit={createEstimateForm.handleSubmit((values) =>
              createEstimate.mutate(values),
            )}
          >
            <SelectInput
              label="Job"
              error={createEstimateForm.formState.errors.job_id?.message}
              {...createEstimateForm.register("job_id")}
            >
              <option value="">Select job</option>
              {(jobs.data ?? []).map((job) => (
                <option key={job.id} value={job.id}>
                  {job.job_name}
                </option>
              ))}
            </SelectInput>
            <SelectInput
              label="Margin profile"
              error={
                createEstimateForm.formState.errors.margin_profile_id?.message
              }
              {...createEstimateForm.register("margin_profile_id")}
            >
              <option value="">Select margin</option>
              {(margins.data ?? []).map((profile) => (
                <option key={profile.id} value={profile.id}>
                  {profile.name}
                </option>
              ))}
            </SelectInput>
            <SubmitButton
              label="Create Estimate"
              pending={createEstimate.isPending}
            />
          </form>
          <div className="mt-4 space-y-2">
            <div className="text-sm font-semibold">Existing estimates</div>
            {(estimates.data ?? []).map((item) => (
              <button
                key={item.id}
                className={`focus-ring block w-full rounded border px-3 py-2 text-left text-sm ${
                  estimateId === item.id
                    ? "border-conduit bg-blue-50"
                    : "border-slate-200 bg-white"
                }`}
                onClick={() => setEstimateId(item.id)}
              >
                {shortId(item.id)} · {item.status} · {money(item.grand_total)}
              </button>
            ))}
          </div>
        </Panel>

        <Panel title="Selected Assemblies and Parameters">
          <div className="mb-4 rounded border border-slate-200 bg-slate-50 p-3 text-sm">
            <div className="font-semibold">
              {currentJob?.job_name ?? "No job selected"}
            </div>
            <div className="text-slate-600">
              {currentCustomer?.company_name ??
                "Create or select an estimate to begin."}
            </div>
          </div>
          <div className="space-y-3">
            <SelectInput
              label="Assembly"
              value={selectedAssemblyId}
              onChange={(event) => handleAssemblyChange(event.target.value)}
            >
              <option value="">Select assembly</option>
              {(assemblies.data ?? []).map((assembly) => (
                <option key={assembly.id} value={assembly.id}>
                  {assembly.code} · {assembly.name}
                </option>
              ))}
            </SelectInput>
            {selectedAssembly ? (
              <ParameterEditor
                definitions={selectedAssembly.parameters}
                values={parameterValues}
                errors={parameterErrors}
                onChange={setParameterValues}
              />
            ) : null}
            <button
              className="focus-ring inline-flex items-center gap-2 rounded bg-conduit px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
              disabled={
                !estimateId || !selectedAssemblyId || addAssembly.isPending
              }
              onClick={handleAddAssembly}
            >
              <Plus size={16} /> Add Assembly
            </button>
          </div>
          <div className="mt-5 space-y-2">
            {(estimate.data?.assemblies ?? []).length ? (
              estimate.data?.assemblies?.map((item) => (
                <div
                  key={item.id}
                  className="rounded border border-slate-200 bg-white p-3 text-sm"
                >
                  <div className="font-semibold">
                    {item.assembly_code} · v{item.assembly_version}
                  </div>
                  <div className="mt-1 grid gap-1 text-slate-600 md:grid-cols-2">
                    {Object.entries(item.parameters).map(([key, value]) => (
                      <div key={key}>
                        {key}: {String(value)}
                      </div>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded border border-dashed border-slate-300 p-4 text-sm text-slate-500">
                No assemblies selected. Add an assembly to begin estimate.
              </div>
            )}
          </div>
        </Panel>

        <Panel title="Summary and Review">
          <EstimateSummary estimate={estimate.data} />
          <div className="mt-4">
            <ReviewFlags flags={estimate.data?.review_flags ?? []} />
          </div>
          <button
            className="focus-ring mt-4 w-full rounded bg-copper px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
            disabled={!estimateId || calculate.isPending}
            onClick={() => calculate.mutate()}
          >
            Calculate Estimate
          </button>
        </Panel>
      </div>

      <Panel title="Line Items">
        <LineItemsTable items={estimate.data?.line_items ?? []} />
      </Panel>

      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Assumptions">
          <BulletList
            items={assumptions.map((note) => note.note)}
            empty="No assumptions yet."
          />
        </Panel>
        <Panel title="Exclusions">
          <BulletList
            items={exclusions.map((note) => note.note)}
            empty="No exclusions yet."
          />
        </Panel>
        <Panel title="Exports">
          <div className="space-y-2">
            <button
              className="focus-ring w-full rounded border border-slate-300 bg-white px-3 py-2 text-sm"
              disabled={!estimateId}
              onClick={() => exportMutation.mutate("supplier-csv")}
            >
              Supplier BOM CSV
            </button>
            <button
              className="focus-ring w-full rounded border border-slate-300 bg-white px-3 py-2 text-sm"
              disabled={!estimateId}
              onClick={() => exportMutation.mutate("internal-csv")}
            >
              Internal BOM CSV
            </button>
            <button
              className="focus-ring w-full rounded border border-slate-300 bg-white px-3 py-2 text-sm"
              disabled={!estimateId}
              onClick={() => exportMutation.mutate("client-pdf")}
            >
              Client PDF
            </button>
            {lastExport ? (
              <a
                className="block rounded bg-conduit px-3 py-2 text-center text-sm font-medium text-white"
                href={downloadUrl(lastExport.id)}
                target="_blank"
                rel="noreferrer"
              >
                Download {lastExport.file_name}
              </a>
            ) : null}
          </div>
        </Panel>
      </div>
    </div>
  );
}

function coerceParameterValues(values: ParameterValues) {
  return Object.fromEntries(
    Object.entries(values).map(([key, value]) => {
      if (value === "true") return [key, true];
      if (value === "false") return [key, false];
      if (
        typeof value === "string" &&
        value.trim() !== "" &&
        !Number.isNaN(Number(value))
      ) {
        return [key, Number(value)];
      }
      return [key, value];
    }),
  );
}

function Metric({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone?: "warning";
}) {
  return (
    <div
      className={`rounded border bg-white p-4 ${tone === "warning" ? "border-amber-300" : "border-slate-200"}`}
    >
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 text-3xl font-semibold">{value}</div>
    </div>
  );
}

function Panel({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded border border-slate-200 bg-white p-4">
      <h2 className="mb-3 text-base font-semibold">{title}</h2>
      {children}
    </section>
  );
}

function SimpleTable({ rows, empty }: { rows: string[][]; empty: string }) {
  if (!rows.length)
    return <div className="text-sm text-slate-500">{empty}</div>;
  return (
    <div className="space-y-2">
      {rows.map((row, index) => (
        <div
          key={index}
          className="grid grid-cols-3 gap-2 rounded border border-slate-100 p-2 text-sm"
        >
          {row.map((cell, cellIndex) => (
            <div
              key={cellIndex}
              className={cellIndex === 0 ? "font-medium" : "text-slate-600"}
            >
              {cell}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function DataTable({
  headers,
  rows,
  empty,
}: {
  headers: string[];
  rows: string[][];
  empty: string;
}) {
  if (!rows.length)
    return (
      <div className="rounded border border-dashed border-slate-300 p-4 text-sm text-slate-500">
        {empty}
      </div>
    );
  return (
    <div className="overflow-auto rounded border border-slate-200">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-100 text-xs uppercase text-slate-600">
          <tr>
            {headers.map((header) => (
              <th key={header} className="px-3 py-2">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex} className="border-t border-slate-100">
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="px-3 py-2">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DetailList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <div className="mb-1 text-sm font-semibold">{title}</div>
      <BulletList items={items} empty={`No ${title.toLowerCase()}.`} />
    </div>
  );
}

function BulletList({ items, empty }: { items: string[]; empty: string }) {
  if (!items.length)
    return <div className="text-sm text-slate-500">{empty}</div>;
  return (
    <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

const customerSchema = z.object({
  company_name: z.string().min(1, "Company is required"),
  contact_name: z.string().optional(),
  email: z.string().optional(),
  phone: z.string().optional(),
  billing_address: z.string().optional(),
  notes: z.string().optional(),
});
type CustomerFormValues = z.infer<typeof customerSchema>;

const jobSchema = z.object({
  customer_id: z.string().min(1, "Customer is required"),
  job_name: z.string().min(1, "Job name is required"),
  site_address: z.string().optional(),
  site_contact: z.string().optional(),
  job_type: z.string().optional(),
  status: z.string(),
  notes: z.string().optional(),
});
type JobFormValues = z.infer<typeof jobSchema>;

const createEstimateSchema = z.object({
  job_id: z.string().min(1, "Job is required"),
  margin_profile_id: z.string().min(1, "Margin profile is required"),
});
type CreateEstimateValues = z.infer<typeof createEstimateSchema>;

type TextInputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
};
function TextInput({ label, error, ...props }: TextInputProps) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block text-slate-700">{label}</span>
      <input
        className="focus-ring w-full rounded border border-slate-300 px-3 py-2"
        {...props}
      />
      {error ? (
        <span className="mt-1 block text-xs text-red-700">{error}</span>
      ) : null}
    </label>
  );
}

type TextAreaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label: string;
  error?: string;
};
function TextArea({ label, error, ...props }: TextAreaProps) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block text-slate-700">{label}</span>
      <textarea
        className="focus-ring min-h-20 w-full rounded border border-slate-300 px-3 py-2"
        {...props}
      />
      {error ? (
        <span className="mt-1 block text-xs text-red-700">{error}</span>
      ) : null}
    </label>
  );
}

type SelectInputProps = React.SelectHTMLAttributes<HTMLSelectElement> & {
  label: string;
  error?: string;
};
function SelectInput({ label, error, children, ...props }: SelectInputProps) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block text-slate-700">{label}</span>
      <select
        className="focus-ring w-full rounded border border-slate-300 bg-white px-3 py-2"
        {...props}
      >
        {children}
      </select>
      {error ? (
        <span className="mt-1 block text-xs text-red-700">{error}</span>
      ) : null}
    </label>
  );
}

function SubmitButton({ label, pending }: { label: string; pending: boolean }) {
  return (
    <button
      className="focus-ring w-full rounded bg-conduit px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
      disabled={pending}
    >
      {pending ? "Saving..." : label}
    </button>
  );
}
