import { Spinner, Text, VStack } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

const apiPath = (path: string) =>
  `${import.meta.env.VITE_API_BASE_URL ?? ""}${path}`;

export default function TenantShell() {
  const mode = import.meta.env.VITE_AUTH_MODE ?? "stub";
  const navigate = useNavigate();
  const loc = useLocation();
  const [gate, setGate] = useState<"loading" | "ok" | "redirecting">(() =>
    mode === "session" ? "loading" : "ok",
  );

  useEffect(() => {
    if (mode !== "session") {
      return;
    }
    let cancelled = false;
    setGate("loading");
    (async () => {
      try {
        const r = await fetch(apiPath("/v1/auth/session"), {
          credentials: "include",
        });
        if (cancelled) return;
        if (r.status === 401) {
          setGate("redirecting");
          navigate("/login", { replace: true, state: { from: loc.pathname } });
          return;
        }
        if (!r.ok) {
          setGate("redirecting");
          navigate("/login?auth_error=session_unavailable", { replace: true });
          return;
        }
        setGate("ok");
      } catch {
        if (!cancelled) {
          setGate("redirecting");
          navigate("/login?auth_error=session_unavailable", { replace: true });
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [mode, navigate, loc.pathname]);

  if (mode === "session" && gate === "loading") {
    return (
      <VStack p={8} data-testid="tenant-shell-loading">
        <Spinner />
        <Text color="fg.muted">Loading session?</Text>
      </VStack>
    );
  }
  if (mode === "session" && gate === "redirecting") {
    return null;
  }
  return <Outlet />;
}
