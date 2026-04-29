import {
  Box,
  Button,
  Drawer,
  HStack,
  Input,
  Portal,
  Spinner,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useState } from "react";

import { apiFetchInit } from "../../lib/consoleAuth";
import {
  formatCanonicalError,
  parseCanonicalError,
  parseCanonicalValidationBody,
} from "../../lib/canonicalApiError";

type SandboxRunOut = {
  run_id: string;
  status: string;
  environment: string;
  trace: string[];
  correlation_id: string;
  persisted?: boolean;
  fixture_fingerprint?: string;
};

function bannerLabelForStatus(status: number): string {
  if (status === 401) return "Autenticacao";
  if (status === 403) return "Permissao";
  if (status === 404) return "Recurso nao encontrado";
  if (status === 422) return "Validacao";
  if (status >= 500) return "Servico indisponivel";
  if (status >= 400) return "Erro de API";
  return "Resposta";
}

export default function SandboxFlowDrawer(props: {
  inboxEnvironment: string;
}) {
  const { inboxEnvironment } = props;
  const apiPath = useCallback(
    (path: string) => `${import.meta.env.VITE_API_BASE_URL ?? ""}${path}`,
    [],
  );
  const [flowKey, setFlowKey] = useState("atdd-flow");
  const [fixtureJson, setFixtureJson] = useState(
    JSON.stringify({ type: "text", body: "hi" }, null, 2),
  );
  const [busy, setBusy] = useState(false);
  const [banner, setBanner] = useState<string | null>(null);
  const [result, setResult] = useState<SandboxRunOut | null>(null);

  const copyTrace = useCallback(() => {
    if (!result?.trace?.length) return;
    void navigator.clipboard.writeText(result.trace.join("\n"));
  }, [result]);

  const onRun = useCallback(async () => {
    setBanner(null);
    setResult(null);
    let fixture_message: Record<string, unknown>;
    try {
      fixture_message = JSON.parse(fixtureJson) as Record<string, unknown>;
    } catch (e) {
      const hint =
        e instanceof SyntaxError && e.message
          ? `Fixture JSON invalido (${e.message})`
          : "Fixture JSON invalido.";
      setBanner(`[Dados] ${hint}`);
      return;
    }
    if (inboxEnvironment !== "sandbox") {
      setBanner(
        "[Ambiente] Sandbox so disponivel quando a inbox esta em ambiente sandbox.",
      );
      return;
    }
    setBusy(true);
    try {
      const init = apiFetchInit({ "Content-Type": "application/json" });
      const q = new URLSearchParams({ environment: "sandbox" });
      const r = await fetch(
        `${apiPath(
          `/v1/me/flows/${encodeURIComponent(flowKey)}/sandbox-run`,
        )}?${q}`,
        {
          ...init,
          method: "POST",
          body: JSON.stringify({ fixture_message }),
        },
      );
      const rForErr = r.clone();
      const raw = await r.json().catch(() => null);
      if (r.status === 200) {
        const out = raw as SandboxRunOut;
        setResult(out);
        const persistHint =
          out.persisted === false
            ? " Persistencia na BD nao confirmada (trace util para debug)."
            : "";
        setBanner(
          `[Sucesso] Run ${out.run_id} (${out.status}). Sem envio de producao.${persistHint}`,
        );
        return;
      }
      const prefix = `[${bannerLabelForStatus(r.status)}]`;
      const parsed =
        raw && typeof raw === "object"
          ? parseCanonicalValidationBody(raw as Record<string, unknown>)
          : null;
      if (parsed?.errors?.length) {
        setBanner(
          `${prefix} ${parsed.errors.map((x) => `${x.field}: ${x.message}`).join("; ")}`,
        );
        return;
      }
      const err = await parseCanonicalError(rForErr);
      setBanner(`${prefix} ${formatCanonicalError(err)}`);
    } finally {
      setBusy(false);
    }
  }, [apiPath, fixtureJson, flowKey, inboxEnvironment]);

  if (inboxEnvironment !== "sandbox") {
    return null;
  }

  return (
    <Drawer.Root>
      <Drawer.Trigger asChild>
        <Button
          size="xs"
          variant="outline"
          data-testid="inbox-sandbox-drawer-trigger"
        >
          Preview sandbox (fluxo)
        </Button>
      </Drawer.Trigger>
      <Portal>
        <Drawer.Backdrop />
        <Drawer.Positioner>
          <Drawer.Content>
            <Drawer.Header>
              <Drawer.Title>Inspecao de fluxo (sandbox)</Drawer.Title>
              <Drawer.Description>
                Simula o grafo de regras so neste ambiente; nao altera conversas nem
                dispara envio WhatsApp de producao.
              </Drawer.Description>
              <Drawer.CloseTrigger aria-label="Fechar sandbox" />
            </Drawer.Header>
            <Drawer.Body>
              <VStack align="stretch" gap={4} data-testid="inbox-sandbox-drawer-panel">
                <Text fontSize="sm" fontWeight="medium" color="fg.emphasized">
                  Sem envio de producao ? motor com `environment=sandbox` obrigatorio na
                  API.
                </Text>
                <Text fontSize="sm" color="fg.muted">
                  <strong>Flow id:</strong> UUID do rascunho gravado em Fluxos (5.1), ou
                  a chave dev <code>atdd-flow</code> em CI/stub.
                </Text>
                <Input
                  aria-label="sandbox-flow-key"
                  value={flowKey}
                  placeholder="UUID do draft ou atdd-flow"
                  onChange={(e) => void setFlowKey(e.target.value)}
                  fontFamily="mono"
                />
                <Text fontSize="sm" color="fg.muted">
                  Fixture (mensagem simulada, JSON). O ecra mostra o mesmo JSON que
                  envia; use Copiar trace para ver log completo.
                </Text>
                <Textarea
                  aria-label="sandbox-fixture-json"
                  fontFamily="mono"
                  minH="100px"
                  value={fixtureJson}
                  onChange={(e) => void setFixtureJson(e.target.value)}
                />
                {busy ? (
                  <HStack gap={2}>
                    <Spinner size="sm" />
                    <Text fontSize="sm" role="status">
                      A executar preview...
                    </Text>
                  </HStack>
                ) : null}
                {banner ? (
                  <Box aria-live="polite" role="status">
                    <Text fontSize="sm">{banner}</Text>
                  </Box>
                ) : null}
                {result ? (
                  <VStack align="stretch" gap={2}>
                    {result.fixture_fingerprint ? (
                      <Text fontSize="xs" color="fg.muted">
                        fixture_fingerprint: {result.fixture_fingerprint}
                      </Text>
                    ) : null}
                    <VStack
                      align="stretch"
                      gap={1}
                      data-testid="inbox-sandbox-trace"
                      aria-live="polite"
                    >
                      <Text
                        fontSize="xs"
                        color="fg.muted"
                        aria-label={`ID de correlacao ${result.correlation_id}`}
                      >
                        correlation_id: {result.correlation_id}
                      </Text>
                      {result.trace.length === 0 ? (
                        <Text fontSize="xs" color="fg.muted">
                          Nenhuma linha de trace.
                        </Text>
                      ) : (
                        result.trace.map((line, i) => (
                          <Text
                            key={`${i}-${line.slice(0, 48)}`}
                            fontSize="xs"
                            fontFamily="mono"
                          >
                            {line}
                          </Text>
                        ))
                      )}
                    </VStack>
                    <Button size="xs" variant="outline" onClick={() => void copyTrace()}>
                      Copiar trace
                    </Button>
                  </VStack>
                ) : !busy ? (
                  <Text fontSize="xs" color="fg.muted">
                    Ainda sem trace ? execute um preview.
                  </Text>
                ) : null}
                <Button
                  size="sm"
                  loading={busy}
                  onClick={() => void onRun()}
                  data-testid="inbox-sandbox-run"
                >
                  Executar preview
                </Button>
              </VStack>
            </Drawer.Body>
          </Drawer.Content>
        </Drawer.Positioner>
      </Portal>
    </Drawer.Root>
  );
}
