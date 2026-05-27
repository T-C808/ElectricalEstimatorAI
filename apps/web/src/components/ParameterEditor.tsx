import type { ParameterDefinition } from "../lib/api";

export type ParameterValues = Record<
  string,
  string | number | boolean | undefined
>;

export function defaultsForParameters(definitions: ParameterDefinition[]) {
  return definitions.reduce<ParameterValues>((values, definition) => {
    values[definition.name] =
      definition.default ?? (definition.type === "boolean" ? false : "");
    return values;
  }, {});
}

export function validateParameters(
  definitions: ParameterDefinition[],
  values: ParameterValues,
) {
  return definitions.reduce<Record<string, string>>((errors, definition) => {
    const value = values[definition.name];
    if (
      definition.required &&
      (value === "" || value === undefined || value === null)
    ) {
      errors[definition.name] = "Required";
    }
    return errors;
  }, {});
}

export function ParameterEditor({
  definitions,
  values,
  errors,
  onChange,
}: {
  definitions: ParameterDefinition[];
  values: ParameterValues;
  errors: Record<string, string>;
  onChange: (values: ParameterValues) => void;
}) {
  if (!definitions.length) {
    return (
      <div className="text-sm text-slate-500">No parameters required.</div>
    );
  }
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {definitions.map((definition) => {
        const value = values[definition.name];
        const label = definition.name.replace(/_/g, " ");
        if (definition.type === "boolean") {
          return (
            <label
              key={definition.name}
              className="flex items-center gap-2 rounded border border-slate-200 bg-white px-3 py-2 text-sm"
            >
              <input
                type="checkbox"
                checked={Boolean(value)}
                onChange={(event) =>
                  onChange({
                    ...values,
                    [definition.name]: event.target.checked,
                  })
                }
              />
              <span className="capitalize">{label}</span>
            </label>
          );
        }
        return (
          <label key={definition.name} className="text-sm">
            <span className="mb-1 block capitalize text-slate-700">
              {label}
            </span>
            {definition.type === "enum" ? (
              <select
                className="focus-ring w-full rounded border border-slate-300 bg-white px-3 py-2"
                value={String(value ?? "")}
                onChange={(event) =>
                  onChange({ ...values, [definition.name]: event.target.value })
                }
              >
                <option value="">Select</option>
                {(definition.options ?? []).map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            ) : (
              <input
                className="focus-ring w-full rounded border border-slate-300 px-3 py-2"
                type={definition.type === "number" ? "number" : "text"}
                value={String(value ?? "")}
                onChange={(event) =>
                  onChange({ ...values, [definition.name]: event.target.value })
                }
              />
            )}
            {errors[definition.name] ? (
              <span className="mt-1 block text-xs text-red-700">
                {errors[definition.name]}
              </span>
            ) : null}
          </label>
        );
      })}
    </div>
  );
}
