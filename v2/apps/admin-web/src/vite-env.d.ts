/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  /** `stub` (default): X-Dev-* headers. `session`: cookie + /v1/auth/session. */
  readonly VITE_AUTH_MODE?: string;
  readonly VITE_DEV_TENANT_ID?: string;
  readonly VITE_DEV_USER_ID?: string;
  readonly VITE_DEV_ROLES?: string;
  readonly VITE_WABA_ENV?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
