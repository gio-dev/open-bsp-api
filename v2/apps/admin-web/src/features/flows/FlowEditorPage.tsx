import {
  Box,
  Button,
  Heading,
  Input,
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
