import {
  Badge,
  Box,
  Button,
  Heading,
  HStack,
  Input,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";

import { apiFetchInit } from "../../lib/consoleAuth";
import {
  formatCanonicalError,
  parseCanonicalError,
} from "../../lib/canonicalApiError";

type ApiKeyRow = {
  id: string;
  name: string;
  key_prefix: string;
  created_at: string;
  expires_at: string | null;
  revoked_at: string | null;
  status: string;
};

const statusPalette: Record<string, "green" | "yellow" | "red" | "gray"> = {
  active: "green",
  scheduled_revocation: "yellow",
  expired: "gray",
  revoked: "red",
};

type WebhookSecretRow = {
  id: string;
  created_at: string;
  invalid_after: string | null;
  status: string;
};

const wvStatusPalette: Record<string, "green" | "yellow" | "gray"> = {
  active: "green",
  coexisting: "yellow",
  expired: "gray",
};

export default function IntegrationsPage() {
  const [loadError, setLoadError] = useState<string | null>(null);
  const [items, setItems] = useState<ApiKeyRow[]>([]);
  const [whItems, setWhItems] = useState<WebhookSecretRow[]>([]);
  const [whLoadError, setWhLoadError] = useState<string | null>(null);
  const [whLoading, setWhLoading] = useState(true);
  const [whOnceToken, setWhOnceToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [newName, setNewName] = useState("integration");
  const [onceSecret, setOnceSecret] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const apiPath = (path: string) =>
    `${import.meta.env.VITE_API_BASE_URL ?? ""}${path}`;

  const load = useCallback(async () => {
    setLoadError(null);
    setLoading(true);
    try {
      const init = apiFetchInit();
      const r = await fetch(apiPath("/v1/me/api-keys"), init);
      if (r.status === 401) {
        setLoadError("Not signed in (use Login or VITE_AUTH_MODE=stub for dev).");
        setLoading(false);
        return;
      }
      if (r.status === 403) {
        setLoadError(
          "Forbidden (org_admin or operator required for API keys).",
        );
        setLoading(false);
        return;
      }
      if (r.status === 503) {
        setLoadError(
          "API database unavailable in this environment (expected in some local runs).",
        );
        setLoading(false);
        return;
      }
      if (!r.ok) {
        const err = await parseCanonicalError(r);
        setLoadError(formatCanonicalError(err));
        setLoading(false);
        return;
      }
      const data = (await r.json()) as { items?: ApiKeyRow[] };
      setItems(data.items ?? []);
    } catch {
      setLoadError("Network error while loading API keys.");
    }
    setLoading(false);
  }, []);

  const loadWebhookSecrets = useCallback(async () => {
    setWhLoadError(null);
    setWhLoading(true);
    try {
      const init = apiFetchInit();
      const r = await fetch(apiPath("/v1/me/webhook-secrets"), init);
      if (r.status === 403) {
        setWhLoadError("Forbidden (org_admin or operator).");
        setWhLoading(false);
        return;
      }
      if (r.status === 503) {
        setWhLoadError("Database unavailable in this run.");
        setWhLoading(false);
        return;
      }
      if (!r.ok) {
        const err = await parseCanonicalError(r);
        setWhLoadError(formatCanonicalError(err));
        setWhLoading(false);
        return;
      }
      const data = (await r.json()) as { items?: WebhookSecretRow[] };
      setWhItems(data.items ?? []);
    } catch {
      setWhLoadError("Network error (webhook secrets).");
    }
    setWhLoading(false);
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    void loadWebhookSecrets();
  }, [loadWebhookSecrets]);

  const createKey = async () => {
    setActionError(null);
    setOnceSecret(null);
    try {
      const init = {
        ...apiFetchInit(),
        method: "POST",
        headers: {
          ...(apiFetchInit().headers as Record<string, string>),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: newName.trim() || "integration" }),
      };
      const r = await fetch(apiPath("/v1/me/api-keys"), init);
      if (r.status === 403) {
        setActionError("Forbidden: org_admin or operator required.");
        return;
      }
      if (r.status === 503) {
        setActionError("Database unavailable; cannot create key here.");
        return;
      }
      if (r.status === 409) {
        setActionError(
          "Prefix collision (rare); try Create again.",
        );
        return;
      }
      if (!r.ok) {
        const err = await parseCanonicalError(r);
        setActionError(formatCanonicalError(err));
        return;
      }
      const body = (await r.json()) as { secret?: string };
      if (body.secret) {
        setOnceSecret(body.secret);
      }
      await load();
    } catch {
      setActionError("Network error on create.");
    }
  };

  const scheduleRevoke = async (id: string) => {
    setActionError(null);
    try {
      const init = {
        ...apiFetchInit(),
        method: "PATCH",
        headers: {
          ...(apiFetchInit().headers as Record<string, string>),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ schedule_revoke_in_seconds: 3600 }),
      };
      const r = await fetch(apiPath(`/v1/me/api-keys/${id}`), init);
      if (!r.ok) {
        const err = await parseCanonicalError(r);
        setActionError(formatCanonicalError(err));
        return;
      }
      await load();
    } catch {
      setActionError("Network error on schedule revoke.");
    }
  };

  const revokeNow = async (id: string) => {
    setActionError(null);
    try {
      const init = {
        ...apiFetchInit(),
        method: "PATCH",
        headers: {
          ...(apiFetchInit().headers as Record<string, string>),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ revoke_immediately: true }),
      };
      const r = await fetch(apiPath(`/v1/me/api-keys/${id}`), init);
      if (!r.ok) {
        const err = await parseCanonicalError(r);
        setActionError(formatCanonicalError(err));
        return;
      }
      await load();
    } catch {
      setActionError("Network error on revoke now.");
    }
  };

  const rotateWebhook = async () => {
    setActionError(null);
    setWhOnceToken(null);
    try {
      const init = {
        ...apiFetchInit(),
        method: "POST",
        headers: {
          ...(apiFetchInit().headers as Record<string, string>),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      };
      const r = await fetch(apiPath("/v1/me/webhook-secrets/rotate"), init);
      if (r.status === 403) {
        setActionError("Forbidden: org_admin or operator required.");
        return;
      }
      if (r.status === 503) {
        setActionError("Database unavailable.");
        return;
      }
      if (!r.ok) {
        const err = await parseCanonicalError(r);
        setActionError(formatCanonicalError(err));
        return;
      }
      const body = (await r.json()) as { verify_token?: string };
      if (body.verify_token) {
        setWhOnceToken(body.verify_token);
      }
      await loadWebhookSecrets();
    } catch {
      setActionError("Network error on webhook rotate.");
    }
  };

  const tenantIdForMeta =
    import.meta.env.VITE_DEV_TENANT_ID ??
    "11111111-1111-4111-8111-111111111111";

  return (
    <VStack align="stretch" gap={4} data-testid="integrations-root">
      <Heading size="lg" data-testid="integrations-heading">
        Integrations / API keys
      </Heading>
      <Text color="fg.muted">
        Secret is shown only once after creation. Store it safely; the API never
        returns it again (Story 2.3).
      </Text>
      {loadError ? (
        <Text color="red.fg" role="alert">
          {loadError}
        </Text>
      ) : null}
      {onceSecret ? (
        <Box
          p={3}
          borderWidth="1px"
          borderRadius="md"
          borderColor="orange.fg"
          data-testid="integrations-secret-once"
        >
          <Text fontWeight="bold" color="orange.fg">
            Copy this secret now. It will not be shown again.
          </Text>
          <Text fontFamily="mono" fontSize="sm" wordBreak="break-all">
            {onceSecret}
          </Text>
        </Box>
      ) : null}
      {actionError ? (
        <Text color="red.fg" role="alert">
          {actionError}
        </Text>
      ) : null}
      <HStack flexWrap="wrap" gap={2}>
        <Input
          maxW="sm"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Key label"
          data-testid="integrations-new-name"
        />
        <Button onClick={() => void createKey()} data-testid="integrations-create">
          Create API key
        </Button>
      </HStack>
      {loading ? (
        <Spinner />
      ) : (
        <VStack align="stretch" gap={2} data-testid="integrations-list">
          {items.map((row) => (
            <HStack
              key={row.id}
              justify="space-between"
              flexWrap="wrap"
              gap={2}
              data-testid={`integrations-row-${row.id}`}
            >
              <Text fontWeight="medium">
                {row.name}{" "}
                <Text as="span" fontFamily="mono" fontSize="sm" color="fg.muted">
                  {row.key_prefix}
                </Text>
              </Text>
              <Badge
                colorPalette={statusPalette[row.status] ?? "gray"}
                data-testid="integrations-status-badge"
              >
                {row.status}
              </Badge>
              <HStack flexWrap="wrap" gap={1}>
                <Button
                  size="xs"
                  variant="outline"
                  onClick={() => void scheduleRevoke(row.id)}
                  disabled={
                    row.status === "revoked" || row.status === "expired"
                  }
                  data-testid={`integrations-schedule-revoke-${row.id}`}
                >
                  Schedule revoke (+1h)
                </Button>
                <Button
                  size="xs"
                  variant="surface"
                  colorPalette="red"
                  onClick={() => void revokeNow(row.id)}
                  disabled={
                    row.status === "revoked" || row.status === "expired"
                  }
                  data-testid={`integrations-revoke-now-${row.id}`}
                >
                  Revoke now
                </Button>
              </HStack>
            </HStack>
          ))}
        </VStack>
      )}
      <Heading size="md" mt={4} data-testid="integrations-waba-heading">
        Meta webhook verify token
      </Heading>
      {whOnceToken ? (
        <Box
          p={3}
          borderWidth="1px"
          borderRadius="md"
          borderColor="blue.fg"
          data-testid="integrations-webhook-token-once"
        >
          <Text fontWeight="bold" color="blue.fg">
            Copy this Meta verify token now. It will not be shown again.
          </Text>
          <Text fontFamily="mono" fontSize="sm" wordBreak="break-all">
            {whOnceToken}
          </Text>
          <Text fontSize="sm" color="fg.muted" mt={2}>
            Add query{" "}
            <Text as="span" fontFamily="mono">
              tenant_id={tenantIdForMeta}
            </Text>{" "}
            to the callback URL (with hub.* params) so the API can resolve the
            tenant (Story 2.4).
          </Text>
        </Box>
      ) : null}
      {whLoadError ? (
        <Text color="fg.muted" data-testid="integrations-webhook-error">
          Webhook verify: {whLoadError}
        </Text>
      ) : null}
      <HStack
        flexWrap="wrap"
        gap={2}
        data-testid="integrations-waba-verify-section"
      >
        <Button
          onClick={() => void rotateWebhook()}
          data-testid="integrations-webhook-rotate"
        >
          Rotate Meta verify token
        </Button>
        {whLoading ? <Spinner size="sm" /> : null}
      </HStack>
      {!whLoading && whItems.length > 0 ? (
        <VStack
          align="stretch"
          gap={1}
          data-testid="integrations-webhook-list"
        >
          {whItems.map((w) => (
            <HStack
              key={w.id}
              flexWrap="wrap"
              justify="space-between"
              data-testid={`integrations-webhook-row-${w.id}`}
            >
              <Text fontSize="sm" fontFamily="mono" color="fg.muted">
                {w.id.slice(0, 8)}?
              </Text>
              <Badge colorPalette={wvStatusPalette[w.status] ?? "gray"}>
                {w.status}
              </Badge>
              <Text fontSize="xs" color="fg.muted">
                {w.invalid_after
                  ? `previous token until ${w.invalid_after}`
                  : "current"}
              </Text>
            </HStack>
          ))}
        </VStack>
      ) : null}
    </VStack>
  );
}
