import { Spinner, Text, VStack } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

const api = () => `${import.meta.env.VITE_API_BASE_URL ?? ""}/v1`;

/** Segundo argumento de postMessage: `*` ou origem absoluta do parent (ex. integrador). */
function postMessageTarget(raw: string | null): string {
  if (!raw || raw.trim() === "" || raw.trim() === "*") {
    return "*";
  }
  try {
    const u = new URL(raw.trim());
    if (!u.protocol.startsWith("http")) {
      return "*";
    }
    return `${u.protocol}//${u.host}`;
  } catch {
    return "*";
  }
}

export default function EmbedPanelPage() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const pmTarget = postMessageTarget(
    params.get("pm_target") ?? params.get("parent_origin"),
  );
  const [phase, setPhase] = useState<
    "need_token" | "loading" | "ok" | "refresh" | "error"
  >(() => (token ? "loading" : "need_token"));
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const r = await fetch(`${api()}/embed/session/validate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
          credentials: "omit",
        });
        if (cancelled) return;
        if (r.status === 401) {
          setPhase("refresh");
          window.parent.postMessage(
            {
              type: "openbsp_embed_session",
              phase: "refresh",
              request_id:
                r.headers.get("x-request-id") ??
                "",
            },
            pmTarget,
          );
          return;
        }
        if (!r.ok) {
          const body = await r.json().catch(() => null);
          setPhase("error");
          setMessage(body?.message ?? r.statusText);
          return;
        }
        await r.json();
        setPhase("ok");
      } catch {
        if (!cancelled) {
          setPhase("error");
          setMessage("network error");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token, pmTarget]);

  if (phase === "need_token") {
    return (
      <VStack p={8} gap={4} align="stretch" data-testid="embed-panel-need-token">
        <Text>Missing query param <code>?token=</code> ...</Text>
      </VStack>
    );
  }

  if (phase === "loading") {
    return (
      <VStack p={8} data-testid="embed-panel-loading">
        <Spinner />
        <Text color="fg.muted">Validating embed token...</Text>
      </VStack>
    );
  }

  if (phase === "refresh") {
    return (
      <VStack p={8} gap={2} data-testid="embed-panel-refresh">
        <Text>Session expired. Ask host to renew token.</Text>
        <Text fontSize="sm" color="fg.muted">
          Host listens for{" "}
          <code>{`postMessage(..., { type: 'openbsp_embed_session', phase: 'refresh' })`}</code>
          . Prefer query{" "}
          <code>?pm_target=https://parent.example</code> (or{" "}
          <code>parent_origin</code>) so the target origin is not <code>*</code>.
        </Text>
      </VStack>
    );
  }

  if (phase === "error") {
    return (
      <VStack p={8} gap={2} data-testid="embed-panel-error">
        <Text>{message || "validation failed"}</Text>
      </VStack>
    );
  }

  return (
    <VStack p={8} gap={4} align="stretch" data-testid="embed-panel-ok">
      <Text>Open BSP inbox shell (embedded).</Text>
      <Text color="fg.muted" fontSize="sm">
        Add inbox routes nested under{" "}
        <code>/embed/panel</code> when UX is ready...
      </Text>
      <Text fontSize="sm" color="fg.muted" data-testid="embed-mode-glossary">
        Vocabulario FR30 (alinhado com a consola): <strong>Bot ativo</strong> - automacao
        ligada; <strong>Assistencia humana</strong> - handoff pendente, em fila, aceite ou
        falhado. O rotulo na thread usa{" "}
        <code>{`GET /v1/me/conversations/{conversation_id}/mode`}</code>.
      </Text>
    </VStack>
  );
}
