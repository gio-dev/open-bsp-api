import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, describe, expect, it, vi } from "vitest";

/** Compatible com `readErrorMessage` (usa `text()`) e com `r.json()` na inbox. */
function jsonResponse(ok: boolean, status: number, body: unknown): Response {
  const raw = JSON.stringify(body);
  return {
    ok,
    status,
    statusText: ok ? "OK" : "Error",
    text: async () => raw,
    json: async () => JSON.parse(raw) as unknown,
  } as Response;
}

function stubInboxFetch(channelHealthResponse: Response) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((url: string) => {
      if (url.includes("/v1/me/channel-health")) {
        return Promise.resolve(channelHealthResponse);
      }
      if (url.includes("/v1/me/inbox/tags")) {
        return Promise.resolve(jsonResponse(true, 200, { items: [] }));
      }
      if (url.includes("/v1/me/conversations?")) {
        return Promise.resolve(
          jsonResponse(true, 200, {
            header: {
              tenant_display_name: "Acme",
              environment: "production",
              waba: null,
            },
            items: [
              {
                id: "conv-a",
                title: "A",
                contact_wa_id: "1",
                waba_id: "w",
                last_message_at: null,
                tags: [],
              },
            ],
            limit: 50,
            next_cursor: null,
          }),
        );
      }
      return Promise.reject(new Error(`unexpected fetch ${url}`));
    }),
  );
}

const healthyPayload = {
  healthy: true,
  incidents: [] as const,
  counts: {
    outbound_failed_meta: 0,
    outbound_failed_platform: 0,
    outbound_rate_limited: 0,
    outbound_stale_queued: 0,
    handoff_failed: 0,
  },
};

/** ATDD Story 4.4 ? banner e estados de erro de saude do canal na inbox. */
describe("ATDD Epic 4 Story 4.4 inbox channel health banner", () => {
  it("shows Estado do canal banner when API reports unhealthy", async () => {
    stubInboxFetch(
      jsonResponse(true, 200, {
        healthy: false,
        incidents: [
          {
            source: "meta",
            severity: "warning",
            code: "outbound_failed_meta",
            summary: "1 envio(s) falharam na API Meta.",
            next_step: "Confirme templates e limites.",
            count: 1,
          },
        ],
        counts: {
          outbound_failed_meta: 1,
          outbound_failed_platform: 0,
          outbound_rate_limited: 0,
          outbound_stale_queued: 0,
          handoff_failed: 0,
        },
      }),
    );

    const { default: InboxPage } = await import("../features/inbox/InboxPage");
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    const qc = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={qc}>
        <ChakraProvider value={defaultSystem}>
          <InboxPage />
        </ChakraProvider>
      </QueryClientProvider>,
    );

    expect(await screen.findByTestId("inbox-channel-health-banner")).toBeInTheDocument();
    expect(await screen.findByTestId("inbox-channel-health-badge")).toHaveTextContent("1");
    expect(
      await screen.findByTestId("inbox-channel-health-outbound_failed_meta"),
    ).toBeInTheDocument();
  });

  it("does not show channel health banner when healthy", async () => {
    stubInboxFetch(jsonResponse(true, 200, healthyPayload));

    const { default: InboxPage } = await import("../features/inbox/InboxPage");
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    const qc = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={qc}>
        <ChakraProvider value={defaultSystem}>
          <InboxPage />
        </ChakraProvider>
      </QueryClientProvider>,
    );

    await screen.findByTestId("inbox-root");
    expect(screen.queryByTestId("inbox-channel-health-banner")).not.toBeInTheDocument();
    expect(screen.queryByTestId("inbox-channel-health-fetch-error")).not.toBeInTheDocument();
  });

  it("shows fetch-error stub when channel-health request fails", async () => {
    stubInboxFetch(jsonResponse(false, 503, { message: "database unavailable" }));

    const { default: InboxPage } = await import("../features/inbox/InboxPage");
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    const qc = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={qc}>
        <ChakraProvider value={defaultSystem}>
          <InboxPage />
        </ChakraProvider>
      </QueryClientProvider>,
    );

    expect(
      await screen.findByTestId("inbox-channel-health-fetch-error", {}, { timeout: 5000 }),
    ).toBeInTheDocument();
    expect(screen.queryByTestId("inbox-channel-health-banner")).not.toBeInTheDocument();
  });

  it("shows inconsistent-state banner when healthy false but no incidents", async () => {
    stubInboxFetch(
      jsonResponse(true, 200, {
        healthy: false,
        incidents: [],
        counts: { ...healthyPayload.counts },
      }),
    );

    const { default: InboxPage } = await import("../features/inbox/InboxPage");
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    const qc = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={qc}>
        <ChakraProvider value={defaultSystem}>
          <InboxPage />
        </ChakraProvider>
      </QueryClientProvider>,
    );

    expect(await screen.findByTestId("inbox-channel-health-inconsistent")).toBeInTheDocument();
    expect(screen.queryByTestId("inbox-channel-health-banner")).not.toBeInTheDocument();
  });

  it("labels unknown incident source as Outro", async () => {
    stubInboxFetch(
      jsonResponse(true, 200, {
        healthy: false,
        incidents: [
          {
            source: "unknown",
            severity: "warning",
            code: "handoff_failed",
            summary: "1 conversa(s) com handoff em estado falhado.",
            next_step: "Revise filas.",
            count: 1,
          },
        ],
        counts: { ...healthyPayload.counts },
      }),
    );

    const { default: InboxPage } = await import("../features/inbox/InboxPage");
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    const qc = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={qc}>
        <ChakraProvider value={defaultSystem}>
          <InboxPage />
        </ChakraProvider>
      </QueryClientProvider>,
    );

    const row = await screen.findByTestId("inbox-channel-health-handoff_failed");
    expect(row.textContent).toContain("Outro");
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});
