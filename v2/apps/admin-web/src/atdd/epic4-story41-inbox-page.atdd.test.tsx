import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, describe, expect, it, vi } from "vitest";

/** ATDD Story 4.1 ? inbox split (lista + thread). */
describe("ATDD Epic 4 Story 4.1 inbox page", () => {
  it("exports InboxPage", async () => {
    const mod = await import("../features/inbox/InboxPage");
    expect(mod.default).toBeTypeOf("function");
  });

  it("shows header and conversation from list query", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((url: string) => {
        if (url.includes("/v1/me/inbox/tags")) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: async () => ({ items: [] }),
          });
        }
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            header: {
              tenant_display_name: "Acme",
              environment: "sandbox",
              waba: {
                waba_id: "w1",
                phone_number_id: "p1",
                display_phone_number: "+1 555",
              },
            },
            items: [
              {
                id: "conv-a",
                title: "Support",
                contact_wa_id: "15551234567",
                waba_id: "w1",
                last_message_at: "2026-01-01T12:00:00Z",
                tags: [],
              },
            ],
            limit: 50,
            next_cursor: null,
          }),
        });
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

    expect(await screen.findByTestId("inbox-root")).toBeInTheDocument();
    expect(await screen.findByTestId("inbox-header")).toHaveTextContent("Acme");
    expect(await screen.findByTestId("inbox-conv-conv-a")).toBeInTheDocument();
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});
