export function stableStringify(value: unknown): string {
  return JSON.stringify(sortRecursively(value), null, 2);
}

function sortRecursively(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(sortRecursively);
  }

  if (value && typeof value === 'object') {
    const obj = value as Record<string, unknown>;
    const out: Record<string, unknown> = {};
    for (const key of Object.keys(obj).sort()) {
      out[key] = sortRecursively(obj[key]);
    }
    return out;
  }

  return value;
}
