/** Parse CDA error envelope from failed API response (D4). */

export type CanonicalApiError = {
  message: string;
  code?: string;
  request_id?: string;
};

export async function parseCanonicalError(
  r: Response,
): Promise<CanonicalApiError> {
  const ct = r.headers.get("content-type") ?? "";
  if (ct.includes("application/json")) {
    try {
      const j = (await r.json()) as Record<string, unknown>;
      const message =
        typeof j.message === "string" ? j.message : `Request failed (HTTP ${r.status})`;
      return {
        message,
        code: typeof j.code === "string" ? j.code : undefined,
        request_id: typeof j.request_id === "string" ? j.request_id : undefined,
      };
    } catch {
      // ignore
    }
  }
  return { message: `Request failed (HTTP ${r.status})` };
}

export function formatCanonicalError(e: CanonicalApiError): string {
  const id = e.request_id ? ` · ref ${e.request_id}` : "";
  const code = e.code ? ` [${e.code}]` : "";
  return `${e.message}${code}${id}`;
}
