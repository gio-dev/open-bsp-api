/** Dev stub headers vs cookie session (Story 2.1). */

export const authMode = import.meta.env.VITE_AUTH_MODE ?? "stub";

export function defaultStubHeaders(): HeadersInit {
  return {
    "X-Dev-Tenant-Id":
      import.meta.env.VITE_DEV_TENANT_ID ??
      "11111111-1111-4111-8111-111111111111",
    "X-Dev-User-Id":
      import.meta.env.VITE_DEV_USER_ID ??
      "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "X-Dev-Roles": import.meta.env.VITE_DEV_ROLES ?? "org_admin",
  };
}

export function apiFetchInit(baseHeaders?: HeadersInit): {
  headers: HeadersInit;
  credentials: RequestCredentials;
} {
  if (authMode === "session") {
    return { headers: baseHeaders ?? {}, credentials: "include" };
  }
  return {
    headers: { ...defaultStubHeaders(), ...baseHeaders },
    credentials: "same-origin",
  };
}
