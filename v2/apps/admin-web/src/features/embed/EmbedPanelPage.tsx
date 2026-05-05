import { Box, Heading, Spinner, Text, VStack } from "@chakra-ui/react";
import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";

const api = () => `${import.meta.env.VITE_API_BASE_URL ?? ""}/v1`;

const MAIN_ID = "embed-main-content";

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
  const errorAlertRef = useRef<HTMLDivElement>(null);

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
              request_id: r.headers.get("x-request-id") ?? "",
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

  useEffect(() => {
    if (phase === "error" && errorAlertRef.current) {
      errorAlertRef.current.focus();
    }
  }, [phase]);

  let title: string;
  if (phase === "need_token") {
    title = "Embed authentication required";
  } else if (phase === "loading") {
    title = "Validating embed session";
  } else if (phase === "refresh") {
    title = "Session expired";
  } else if (phase === "error") {
    title = "Embed validation error";
  } else {
    title = "Embedded inbox";
  }

  return (
    <>
      <Box
        as="a"
        href={`#${MAIN_ID}`}
        position="absolute"
        width="1px"
        height="1px"
        padding={0}
        margin="-1px"
        overflow="hidden"
        clip="rect(0, 0, 0, 0)"
        whiteSpace="nowrap"
        borderWidth={0}
        zIndex={10}
        css={{
          "&:focus-visible": {
            clip: "auto",
            height: "auto",
            width: "auto",
            margin: 0,
            padding: "0.5rem 0.75rem",
            position: "fixed",
            top: "0.5rem",
            left: "0.5rem",
            overflow: "visible",
            whiteSpace: "normal",
          },
        }}
      >
        Skip to main content
      </Box>

      <Box
        as="main"
        id={MAIN_ID}
        tabIndex={-1}
        p={8}
        maxW="960px"
        outline="none"
        _focusVisible={{
          outline: "2px solid",
          outlineOffset: "3px",
        }}
      >
        <Heading as="h1" size="lg" mb={4}>
          {title}
        </Heading>

        {phase === "need_token" ? (
          <VStack gap={4} align="stretch" data-testid="embed-panel-need-token">
            <Text id="embed-need-token-copy">
              Missing query param <code>?token=</code>. The host must append the JWT
              minted via <code>POST /v1/me/embed/token</code>.
            </Text>
          </VStack>
        ) : null}

        {phase === "loading" ? (
          <Box
            role="status"
            aria-live="polite"
            aria-busy="true"
            aria-label="Validating embed token"
            data-testid="embed-panel-loading"
          >
            <VStack gap={3} align="start">
              <Spinner aria-hidden />
              <Text color="fg.muted" aria-hidden="true">
                Validating embed token.
              </Text>
            </VStack>
          </Box>
        ) : null}

        {phase === "refresh" ? (
          <VStack gap={2} align="stretch" data-testid="embed-panel-refresh">
            <Text>Session expired. Ask the host page to renew your token.</Text>
            <Text fontSize="sm" color="fg.muted">
              Host listens for{" "}
              <code>
                {`postMessage(..., { type: 'openbsp_embed_session', phase: 'refresh' })`}
              </code>
              . Prefer query{" "}
              <code>?pm_target=https://parent.example</code> (or{" "}
              <code>parent_origin</code>) so the target origin is not <code>*</code>.
            </Text>
          </VStack>
        ) : null}

        {phase === "error" ? (
          <Box
            ref={errorAlertRef}
            tabIndex={-1}
            role="alert"
            aria-live="assertive"
            aria-atomic="true"
            data-testid="embed-panel-error"
          >
            <Text fontWeight="medium">{message || "validation failed"}</Text>
          </Box>
        ) : null}

        {phase === "ok" ? (
          <VStack gap={4} align="stretch" data-testid="embed-panel-ok">
            <Text>Open BSP inbox shell (embedded).</Text>
            <Text color="fg.muted" fontSize="sm">
              Add inbox routes nested under <code>/embed/panel</code> when UX is ready.
            </Text>
            <Text fontSize="sm" color="fg.muted" data-testid="embed-mode-glossary">
              Vocabulary FR30 (aligned with console): <strong>Bot active</strong>{" "}
              (automation on); <strong>Human assistance</strong> (handoff pending,
              queued, accepted, or failed). Thread label uses{" "}
              <code>{`GET /v1/me/conversations/{conversation_id}/mode`}</code>.
            </Text>
          </VStack>
        ) : null}
      </Box>
    </>
  );
}
