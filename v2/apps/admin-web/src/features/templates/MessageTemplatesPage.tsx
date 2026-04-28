import {
  Badge,
  Button,
  Heading,
  HStack,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useEffect, useRef, useState } from "react";

import { apiFetchInit } from "../../lib/consoleAuth";

const listEnvironment = (): string =>
  import.meta.env.VITE_WABA_ENV ?? "production";

const phoneIdStorageKey = (env: string) =>
  `open-bsp:msg-templates:phone_number_id:${env}`;

function readStoredPhoneNumberId(env: string): string | null {
  try {
    return sessionStorage.getItem(phoneIdStorageKey(env));
  } catch {
    return null;
  }
}

type WabaLine = {
  id: string;
  waba_id: string;
  phone_number_id: string;
  display_phone_number: string;
  environment: string;
  status: string;
};

const tplStatusPalette: Record<string, "green" | "yellow" | "red" | "gray"> = {
  approved: "green",
  submitted: "yellow",
  paused: "red",
  rejected: "red",
  draft: "gray",
};

type TemplateRow = {
  id: string;
  name: string;
  language: string;
  display_status: string;
  meta_status: string;
  status_detail?: string | null;
};

type Signals = {
  source: string;
  quality_rating?: string | null;
  messaging_limit_tier?: string | null;
  notes?: string | null;
  volume_incidents_crossref?: boolean;
};

export default function MessageTemplatesPage() {
  const [items, setItems] = useState<TemplateRow[]>([]);
  const [signals, setSignals] = useState<Signals | null>(null);
  const [wabaId, setWabaId] = useState<string | null>(null);
  const [lastSync, setLastSync] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [phoneNumberId, setPhoneNumberId] = useState<string | null>(() =>
    typeof window !== "undefined"
      ? readStoredPhoneNumberId(listEnvironment())
      : null,
  );
  const [lineChoices, setLineChoices] = useState<WabaLine[]>([]);
  const phoneNumberIdRef = useRef(phoneNumberId);
  phoneNumberIdRef.current = phoneNumberId;

  const apiPath = useCallback(
    (path: string) => `${import.meta.env.VITE_API_BASE_URL ?? ""}${path}`,
    [],
  );

  const load = useCallback(
    async (
      refresh: boolean,
      opts?: { phoneNumberId?: string | null },
    ) => {
      setLoadError(null);
      if (refresh) {
        setSyncing(true);
      } else {
        setLoading(true);
      }
      const env = listEnvironment();
      const pid =
        opts?.phoneNumberId !== undefined
          ? opts.phoneNumberId
          : phoneNumberIdRef.current;

      const templatesUrl = (phoneId: string | null) => {
        const qs = new URLSearchParams({
          environment: env,
          ...(refresh ? { refresh: "true" } : {}),
        });
        if (phoneId) {
          qs.set("phone_number_id", phoneId);
        }
        return apiPath(`/v1/me/message-templates?${qs.toString()}`);
      };

      try {
        const init = apiFetchInit({ "X-Environment": env });
        let r = await fetch(templatesUrl(pid), init);

        if (r.status === 409) {
          let conflictMsg =
            "Varias linhas WhatsApp neste ambiente; escolha o numero de envio.";
          try {
            const body = (await r.json()) as { message?: string };
            if (body?.message) {
              conflictMsg = body.message;
            }
          } catch {
            /* ignore */
          }

          const wabaR = await fetch(
            apiPath(
              `/v1/me/waba-phone-numbers?environment=${encodeURIComponent(env)}&limit=100`,
            ),
            init,
          );
          if (!wabaR.ok) {
            setLoadError(
              `${conflictMsg} (falha ao listar numeros WABA: HTTP ${wabaR.status}).`,
            );
            return;
          }
          const wabaData = (await wabaR.json()) as { items?: WabaLine[] };
          const lines = wabaData.items ?? [];

          if (lines.length === 1) {
            const onlyId = lines[0].phone_number_id;
            try {
              sessionStorage.setItem(phoneIdStorageKey(env), onlyId);
            } catch {
              /* ignore */
            }
            setPhoneNumberId(onlyId);
            setLineChoices([]);
            r = await fetch(templatesUrl(onlyId), init);
          } else if (lines.length > 1) {
            setLineChoices(lines);
            setLoadError(conflictMsg);
            return;
          } else {
            setLineChoices([]);
            setLoadError(
              `${conflictMsg} Nenhum numero WABA registado para listar.`,
            );
            return;
          }
        }

        if (r.status === 401) {
          setLoadError("Not signed in (use Login or VITE_AUTH_MODE=stub for dev).");
          return;
        }
        if (r.status === 403) {
          setLoadError(
            refresh
              ? "So org_admin pode sincronizar com Meta (?refresh=true)."
              : "Forbidden (tenant stub required).",
          );
          return;
        }
        if (r.status === 503) {
          const t = await r.text();
          setLoadError(
            `Servico indisponivel (503). ${t.slice(0, 200) || "Base ou credenciais Meta."}`,
          );
          return;
        }
        if (!r.ok) {
          setLoadError(`Could not load templates (${r.status}).`);
          return;
        }
        setLineChoices([]);
        const data = (await r.json()) as {
          items?: TemplateRow[];
          channel_signals?: Signals;
          waba_id?: string | null;
          last_sync_at?: string | null;
        };
        setItems(data.items ?? []);
        setSignals(data.channel_signals ?? null);
        setWabaId(data.waba_id ?? null);
        setLastSync(data.last_sync_at ?? null);
      } catch {
        setLoadError("Network error while loading templates.");
      } finally {
        setLoading(false);
        setSyncing(false);
      }
    },
    [apiPath],
  );

  useEffect(() => {
    void load(false);
  }, [load]);

  const env = listEnvironment();

  return (
    <VStack align="stretch" gap={4} data-testid="msg-templates-root">
      <Heading size="lg">Message templates</Heading>
      <Text color="fg.muted" data-testid="msg-templates-env">
        Environment: {env}. Sinais de canal refletem a ultima sincronizacao (sem
        vanity: podem estar indisponiveis).
      </Text>
      {wabaId ? (
        <Text fontSize="sm" color="fg.muted">
          WABA: {wabaId}
        </Text>
      ) : (
        <Text fontSize="sm" color="fg.muted" role="status">
          Nenhum numero WABA neste ambiente; registe em WhatsApp numbers.
        </Text>
      )}
      {phoneNumberId ? (
        <Text
          fontSize="xs"
          color="fg.muted"
          data-testid="msg-templates-phone-ref"
        >
          Meta phone_number_id: {phoneNumberId}
        </Text>
      ) : null}
      {lineChoices.length > 1 ? (
        <VStack align="stretch" gap={2} data-testid="msg-templates-line-picker">
          <Text fontSize="sm" fontWeight="medium">
            Linha de envio (obrigatoria neste ambiente)
          </Text>
          <select
            aria-label="Escolher linha WhatsApp para templates"
            value={phoneNumberId ?? ""}
            onChange={(e) => {
              const v = e.target.value;
              const next = v.length > 0 ? v : null;
              setPhoneNumberId(next);
              if (next) {
                try {
                  sessionStorage.setItem(phoneIdStorageKey(env), next);
                } catch {
                  /* ignore */
                }
              } else {
                try {
                  sessionStorage.removeItem(phoneIdStorageKey(env));
                } catch {
                  /* ignore */
                }
              }
              void load(false, { phoneNumberId: next });
            }}
          >
            <option value="">Selecione o numero...</option>
            {lineChoices.map((ln) => (
              <option key={ln.id} value={ln.phone_number_id}>
                {ln.display_phone_number} / {ln.waba_id}
              </option>
            ))}
          </select>
        </VStack>
      ) : null}
      <HStack>
        <Button
          size="sm"
          loading={syncing}
          onClick={() => void load(true)}
          data-testid="msg-templates-sync"
        >
          Sync from Meta
        </Button>
        {lastSync ? (
          <Text fontSize="xs" color="fg.muted">
            Ultima sync: {lastSync}
          </Text>
        ) : null}
      </HStack>
      {signals ? (
        <VStack
          align="stretch"
          gap={1}
          p={3}
          borderWidth="1px"
          borderRadius="md"
          data-testid="msg-templates-signals"
        >
          <Text fontWeight="medium">Channel signals</Text>
          <Text fontSize="sm">
            source: <Badge variant="outline">{signals.source}</Badge>
          </Text>
          {signals.quality_rating ? (
            <Text fontSize="sm">quality_rating: {signals.quality_rating}</Text>
          ) : (
            <Text fontSize="sm" color="fg.muted">
              quality_rating: (n/d)
            </Text>
          )}
          {signals.messaging_limit_tier ? (
            <Text fontSize="sm">tier: {signals.messaging_limit_tier}</Text>
          ) : null}
          {signals.notes ? (
            <Text fontSize="sm" color="fg.muted">
              {signals.notes}
            </Text>
          ) : null}
          {!signals.volume_incidents_crossref ? (
            <Text fontSize="xs" color="fg.muted">
              Cruzamento incidentes/volume: nao disponivel neste piloto.
            </Text>
          ) : null}
        </VStack>
      ) : null}
      {loadError ? (
        <Text color="red.fg" role="alert" data-testid="msg-templates-error">
          {loadError}
        </Text>
      ) : null}
      {loading ? (
        <Spinner />
      ) : (
        <VStack align="stretch" gap={2} data-testid="msg-templates-list">
          {items.length === 0 ? (
            <Text color="fg.muted">
              Sem templates em cache. Use Sync (org_admin) ou aguarde backend.
            </Text>
          ) : null}
          {items.map((row) => (
            <HStack
              key={row.id}
              justify="space-between"
              flexWrap="wrap"
              gap={2}
              data-testid={`msg-templates-row-${row.id}`}
            >
              <Text fontWeight="medium">{row.name}</Text>
              <Badge variant="outline">{row.language}</Badge>
              <Badge
                colorPalette={
                  tplStatusPalette[row.display_status] ?? "gray"
                }
                data-testid="msg-templates-status"
              >
                {row.display_status}
              </Badge>
              {row.status_detail ? (
                <Text fontSize="xs" color="fg.muted" maxW="sm">
                  {row.status_detail}
                </Text>
              ) : null}
            </HStack>
          ))}
        </VStack>
      )}
    </VStack>
  );
}
