export function money(value: string | number | null | undefined) {
  const numberValue = Number(value ?? 0);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(numberValue);
}

export function percent(value: string | number | null | undefined) {
  return `${Math.round(Number(value ?? 0) * 100)}%`;
}

export function shortId(id: string) {
  return id.slice(0, 8);
}
