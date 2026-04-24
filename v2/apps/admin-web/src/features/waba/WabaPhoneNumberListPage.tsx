import { Badge, Heading, HStack, Spinner, Text, VStack } from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";

import { apiFetchInit } from "../../lib/consoleAuth";

const listEnvironment = (): string =>
  import.meta.env.VITE_WABA_ENV ?? "production";

const statusPalette: Record<string, "green" | "yellow" | "red" | "gray"> = {
  active: "green",
  pending: "yellow",
  suspended: "red",
};

export default function WabaPhoneNumberListPage() {
  const [items, setItems] = useState<
    Array<{
      id: string;
      display_phone_number: string;
      environment: string;
      status: string;
      waba_id: string;
    }>
  >([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const apiPath = (path: string) =>
    `${import.meta.env.VITE_API_BASE_URL ?? ""}${path}`;

  const load = useCallback(async () => {
    setLoadError(null);
    setLoading(true);
    const env = listEnvironment();
    try {
      const init = apiFetchInit({ "X-Environment": env });
      const r = await fetch(
        apiPath(
          `/v1/me/waba-phone-numbers?environment=${encodeURIComponent(env)}&limit=50`,
        ),
        init,
      );
      if (r.status === 401) {
        setLoadError("Not signed in (use Login or VITE_AUTH_MODE=stub for dev).");
        setLoading(false);
        return;
      }
      if (r.status === 403) {
        setLoadError("Forbidden (org_admin / tenant stub required).");
        setLoading(false);
        return;
      }
      if (!r.ok) {
        setLoadError(`Could not load numbers (${r.status}).`);
        setLoading(false);
        return;
      }
      const data = (await r.json()) as { items?: typeof items };
      setItems(data.items ?? []);
    } catch {
      setLoadError("Network error while loading WABA numbers.");
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const env = listEnvironment();

  return (
    <VStack align="stretch" gap={4} data-testid="waba-list-root">
      <Heading size="lg">WhatsApp numbers</Heading>
      <Text color="fg.muted" data-testid="waba-context-env">
        Environment: {env} (Meta integration may be stubbed in dev.)
      </Text>
      {loadError ? (
        <Text color="red.fg" role="alert">
          {loadError}
        </Text>
      ) : null}
      {loading ? (
        <Spinner />
      ) : (
        <VStack align="stretch" gap={2} data-testid="waba-list">
          {items.map((row) => (
            <HStack
              key={row.id}
              justify="space-between"
              flexWrap="wrap"
              gap={2}
              data-testid={`waba-row-${row.id}`}
            >
              <Text fontWeight="medium">{row.display_phone_number}</Text>
              <Badge variant="outline">{row.environment}</Badge>
              <Badge
                colorPalette={statusPalette[row.status] ?? "gray"}
                data-testid="waba-status-badge"
              >
                {row.status}
              </Badge>
              <Text color="fg.muted" fontSize="sm">
                {row.waba_id}
              </Text>
            </HStack>
          ))}
        </VStack>
      )}
    </VStack>
  );
}
