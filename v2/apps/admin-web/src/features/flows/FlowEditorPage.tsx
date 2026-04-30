import {
  Box,
  Button,
  Dialog,
  Heading,
  Input,
  NativeSelectField,
  NativeSelectRoot,
  Portal,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useMemo, useState } from "react";

import { apiFetchInit } from "../../lib/consoleAuth";
import {
  formatCanonicalError,
  parseCanonicalError,
  parseCanonicalValidationBody,
} from "../../lib/canonicalApiError";

const DEFAULT_GRAPH = `{
  "nodes": [
    { "id": "t1", "kind": "trigger" },
    { "id": "a1", "kind": "action" }
  ],
  "edges": [
    { "source": "t1", "target": "a1" }
  ]
}`;

type FieldErr = { field: string; message: string };

type PublishEnv = "development" | "staging" | "production";

type VersionRow = {
  version_id: string;
  environment: string;
  definition_fingerprint_prefix: string;
  published_at: string;
  published_by_user_id?: string | null;
};

function parseGraphJson(
  graphJson: string,
): { ok: true; value: unknown } | { ok: false; message: string } {
  try {
    return { ok: true, value: JSON.parse(graphJson) as unknown };
  } catch (e) {
    const hint =
      e instanceof SyntaxError && e.message
        ? `JSON invalido (${e.message})`
        : "JSON invalido";
    return { ok: false, message: hint };
  }
}

export default function FlowEditorPage() {
  const apiPath = useCallback(
    (path: string) => `${import.meta.env.VITE_API_BASE_URL ?? ""}${path}`,
    [],
  );
  const [name, setName] = useState("Meu fluxo");
  const [graphJson, setGraphJson] = useState(DEFAULT_GRAPH);
  const [busy, setBusy] = useState<"idle" | "validate" | "save">("idle");
  const [fieldErrors, setFieldErrors] = useState<FieldErr[]>([]);
  const [banner, setBanner] = useState<string | null>(null);
  const [savedDraftId, setSavedDraftId] = useState<string | null>(null);
  const [flowIdForPublish, setFlowIdForPublish] = useState("");
  const [publishEnv, setPublishEnv] = useState<PublishEnv>("staging");
  const [publishDialogOpen, setPublishDialogOpen] = useState(false);
  const [publishBusy, setPublishBusy] = useState(false);
  const [versionsBusy, setVersionsBusy] = useState(false);
  const [versionRows, setVersionRows] = useState<VersionRow[] | null>(null);
  const parsedGraph = useMemo(() => parseGraphJson(graphJson), [graphJson]);

  const onValidate = useCallback(async () => {
    setBanner(null);
    setFieldErrors([]);
    if (!parsedGraph.ok) {
      setFieldErrors([{ field: "definition", message: parsedGraph.message }]);
      return;
    }
    setBusy("validate");
    try {
      const init = apiFetchInit({
        "Content-Type": "application/json",
      });
      const r = await fetch(apiPath("/v1/me/flows/validate"), {
        ...init,
        method: "POST",
        body: JSON.stringify(parsedGraph.value),
      });
      if (r.status === 200) {
        setBanner("Validacao concluida: fluxo valido.");
        setFieldErrors([]);
        return;
      }
      const rForErr = r.clone();
      const body = await r.json().catch(() => null);
      const parsed =
        typeof body === "object" && body !== null
          ? parseCanonicalValidationBody(body as Record<string, unknown>)
          : null;
      if (parsed?.errors?.length) {
        setBanner("Validacao falhou. Veja os erros na lista abaixo.");
        setFieldErrors(
          parsed.errors.map((e) => ({
            field: e.field,
            message: e.message,
          })),
        );
        return;
      }
      const err = await parseCanonicalError(rForErr);
      setBanner(formatCanonicalError(err));
    } finally {
      setBusy("idle");
    }
  }, [apiPath, parsedGraph]);

  const onSave = useCallback(async () => {
    setBanner(null);
    if (!parsedGraph.ok) {
      setFieldErrors([{ field: "definition", message: parsedGraph.message }]);
      return;
    }
    setBusy("save");
    try {
      const init = apiFetchInit({
        "Content-Type": "application/json",
      });
      const r = await fetch(apiPath("/v1/me/flows"), {
        ...init,
        method: "POST",
        body: JSON.stringify({ name, definition: parsedGraph.value }),
      });
      if (r.status === 201) {
        const data = (await r.json()) as { id?: string };
        if (data.id) {
          setSavedDraftId(data.id);
          setFlowIdForPublish(data.id);
        }
        setBanner("Rascunho gravado. O servidor validou a definicao com sucesso.");
        setFieldErrors([]);
        return;
      }
      const rForErr = r.clone();
      const body = await r.json().catch(() => null);
      const parsed =
        typeof body === "object" && body !== null
          ? parseCanonicalValidationBody(body as Record<string, unknown>)
          : null;
      if (parsed?.errors?.length) {
        setBanner("Gravacao rejeitada: definicao invalida. Corrija os erros abaixo.");
        setFieldErrors(
          parsed.errors.map((e) => ({
            field: e.field,
            message: e.message,
          })),
        );
        return;
      }
      const err = await parseCanonicalError(rForErr);
      setBanner(formatCanonicalError(err));
    } finally {
      setBusy("idle");
    }
  }, [apiPath, name, parsedGraph]);

  const requestPublishDialog = useCallback(() => {
    setBanner(null);
    const fid = flowIdForPublish.trim();
    if (!fid) {
      setBanner(
        "Indique o UUID do rascunho gravado (ou grave um rascunho primeiro).",
      );
      return;
    }
    setPublishDialogOpen(true);
  }, [flowIdForPublish]);

  const fetchVersionHistory = useCallback(async () => {
    setBanner(null);
    const fid = flowIdForPublish.trim();
    if (!fid) {
      setBanner(
        "Indique o UUID do fluxo ou chave CI (atdd-flow) para carregar o historico.",
      );
      return;
    }
    setVersionsBusy(true);
    try {
      const init = apiFetchInit({});
      const r = await fetch(
        apiPath(
          `/v1/me/flows/${encodeURIComponent(fid)}/versions?limit=50&offset=0`,
        ),
        { ...init, method: "GET" },
      );
      if (r.status === 200) {
        const data = (await r.json()) as { items?: VersionRow[] };
        setVersionRows(Array.isArray(data.items) ? data.items : []);
        return;
      }
      const rForErr = r.clone();
      const err = await parseCanonicalError(rForErr);
      setBanner(formatCanonicalError(err));
    } finally {
      setVersionsBusy(false);
    }
  }, [apiPath, flowIdForPublish]);

  const executePublish = useCallback(async () => {
    const fid = flowIdForPublish.trim();
    setPublishBusy(true);
    try {
      const init = apiFetchInit({
        "Content-Type": "application/json",
      });
      const r = await fetch(apiPath(`/v1/me/flows/${encodeURIComponent(fid)}/publish`), {
        ...init,
        method: "POST",
        body: JSON.stringify({ environment: publishEnv }),
      });
      if (r.status === 200) {
        const body = (await r.json()) as { idempotent_repeat?: boolean };
        const suffix = body.idempotent_repeat ? " (sem alteracoes)." : ".";
        setBanner(`Publicado para ${publishEnv}${suffix}`);
        setPublishDialogOpen(false);
        setFieldErrors([]);
        void fetchVersionHistory();
        return;
      }
      const rForErr = r.clone();
      const jsonBody = await r.json().catch(() => null);
      const parsed =
        typeof jsonBody === "object" && jsonBody !== null
          ? parseCanonicalValidationBody(jsonBody as Record<string, unknown>)
          : null;
      if (parsed?.errors?.length) {
        setBanner(
          `Publicacao falhou para ambiente ${publishEnv}. Corrija os erros abaixo.`,
        );
        setFieldErrors(
          parsed.errors.map((e) => ({
            field: e.field,
            message: e.message,
          })),
        );
        return;
      }
      const err = await parseCanonicalError(rForErr);
      setBanner(formatCanonicalError(err));
      setPublishDialogOpen(false);
    } finally {
      setPublishBusy(false);
    }
  }, [apiPath, flowIdForPublish, publishEnv, fetchVersionHistory]);

  return (
    <VStack data-testid="flow-editor-root" align="stretch" gap={6} py={6}>
      <Heading size="lg">Fluxos (draft)</Heading>
      {banner ? (
        <Box aria-live="polite" role="status">
          <Text fontWeight="medium">{banner}</Text>
        </Box>
      ) : null}
      <Box>
        <Text fontSize="sm" color="fg.muted">
          Nome
        </Text>
        <Input
          aria-label="flow-name"
          value={name}
          onChange={(e) => void setName(e.target.value)}
        />
      </Box>
      <Box>
        <Text fontSize="sm" color="fg.muted">
          Definicoes (nos e arestas)
        </Text>
        <Textarea
          aria-label="flow-definition-json"
          fontFamily="mono"
          minH="220px"
          value={graphJson}
          onChange={(e) => void setGraphJson(e.target.value)}
        />
      </Box>
      {fieldErrors.length > 0 ? (
        <VStack
          align="stretch"
          gap={2}
          role="list"
          data-testid="flow-field-errors"
          aria-live="assertive"
        >
          {fieldErrors.map((e, i) => (
            <Box key={`${e.field}-${i}`} role="listitem">
              <Text fontWeight="semibold">{e.field}</Text>
              <Text color="fg.muted">{e.message}</Text>
            </Box>
          ))}
        </VStack>
      ) : null}
      <Text fontSize="sm" color="fg.muted" maxW="lg">
        <strong>Validar</strong> so verifica o grafo. <strong>Gravar rascunho</strong>{" "}
        envia para o servidor, que valida antes de persistir; definicoes invalidas
        recebem 422 com erros por campo (igual a Validar).
      </Text>
      <Heading size="md">Publicar (runtime)</Heading>
      {savedDraftId ? (
        <Text fontSize="xs" color="fg.muted">
          Ultimo rascunho gravado: <Text as="span" fontFamily="mono">{savedDraftId}</Text>
        </Text>
      ) : null}
      <Box>
        <Text fontSize="sm" color="fg.muted">
          UUID do rascunho a publicar
        </Text>
        <Input
          aria-label="flow-id-publish"
          fontFamily="mono"
          placeholder="cole o UUID apos gravar"
          value={flowIdForPublish}
          onChange={(e) => void setFlowIdForPublish(e.target.value)}
        />
      </Box>
      <Box>
        <Text fontSize="sm" color="fg.muted" mb={1}>
          Ambiente destino (visivel antes de confirmar)
        </Text>
        <NativeSelectRoot aria-label="publish-environment-root" width="fit-content">
          <NativeSelectField
            aria-label="publish-environment"
            value={publishEnv}
            onChange={(e) =>
              void setPublishEnv(e.target.value as PublishEnv)
            }
          >
            <option value="development">development</option>
            <option value="staging">staging</option>
            <option value="production">production (apenas org_admin)</option>
          </NativeSelectField>
        </NativeSelectRoot>
      </Box>
      <Button
        size="sm"
        width="fit-content"
        data-testid="flow-publish-request"
        onClick={() => void requestPublishDialog()}
      >
        Publicar...
      </Button>
      <Dialog.Root
        open={publishDialogOpen}
        onOpenChange={(e) => setPublishDialogOpen(e.open)}
      >
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content maxW="md">
              <Dialog.Header>
                <Dialog.Title>Confirmar publicacao</Dialog.Title>
              </Dialog.Header>
              <Dialog.Body>
                <Text>
                  Ambiente:&nbsp;
                  <Text as="span" fontWeight="bold" color="fg.error">
                    {publishEnv}
                  </Text>
                </Text>
                <Text fontSize="sm" color="fg.muted" mt={2}>
                  O snapshot actual do rascunho torna-se a versao activa nesse ambiente.
                  Producao exige papel org_admin na API.
                </Text>
              </Dialog.Body>
              <Dialog.Footer>
                <Button
                  variant="outline"
                  me={2}
                  onClick={() => setPublishDialogOpen(false)}
                >
                  Cancelar
                </Button>
                <Button
                  loading={publishBusy}
                  onClick={() => void executePublish()}
                >
                  Confirmar publicacao
                </Button>
              </Dialog.Footer>
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>
      <Heading size="md">Historico de versões (FR25)</Heading>
      <Text fontSize="sm" color="fg.muted" maxW="lg">
        Lista append-only ligada ao identificador de fluxo usado para publicar. Carregue
        após publicar ou para auditoria rapida no tenant.
      </Text>
      <Button
        size="sm"
        width="fit-content"
        loading={versionsBusy}
        onClick={() => void fetchVersionHistory()}
      >
        Carregar lista de versões
      </Button>
      {versionRows !== null && versionRows.length === 0 ? (
        <Text fontSize="sm" color="fg.muted">
          Sem publicações registadas para este fluxo (ou filtros diferentes em ambiente).
        </Text>
      ) : null}
      {versionRows !== null && versionRows.length > 0 ? (
        <VStack align="stretch" gap={2} role="list" data-testid="flow-version-rows">
          {versionRows.map((v) => (
            <Box key={v.version_id} role="listitem">
              <Text fontSize="sm" fontFamily="mono">
                {v.published_at} · {v.environment} · {v.definition_fingerprint_prefix}{" "}
                · ?{String(v.version_id).slice(-8)}
              </Text>
            </Box>
          ))}
        </VStack>
      ) : null}
      <Button
        size="sm"
        width="fit-content"
        loading={busy === "validate"}
        onClick={() => void onValidate()}
      >
        Validar
      </Button>
      <Button
        size="sm"
        width="fit-content"
        loading={busy === "save"}
        onClick={() => void onSave()}
      >
        Gravar rascunho
      </Button>
    </VStack>
  );
}
