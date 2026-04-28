import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, describe, expect, it, vi } from "vitest";

/** ATDD Story 4.2 ? etiquetas na inbox. */
describe("ATDD Epic 4 Story 4.2 inbox tags UI", () => {
  it("renders tag row when thread returns tags", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((url: string) => {
        if (url.includes("/v1/me/inbox/tags")) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: async () => ({
              items: [{ id: "tag-1", name: "vip" }],
            }),
          });
        }
        if (url.includes("/v1/me/conversations?")) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: async () => ({
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
                  tags: [{ id: "tag-1", name: "vip" }],
                },
              ],
              limit: 50,
              next_cursor: null,
            }),
          });
        }
        if (url.includes("/handoff")) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: async () => ({
              conversation_id: "conv-a",
              intent_summary: "Resumo",
              bot_last_output: "Olá",
              handoff_state: "queued",
              queue_id: "q1",
              claimed_by_user_id: null,
              updated_at: "2026-01-01T00:00:00Z",
            }),
          });
        }
        if (url.includes("/messages")) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: async () => ({
              conversation_id: "conv-a",
              header: {
                tenant_display_name: "Acme",
                environment: "production",
                waba: null,
              },
              items: [],
              tags: [{ id: "tag-1", name: "vip" }],
            }),
          });
        }
        return Promise.reject(new Error(`unexpected fetch ${url}`));
      }),
    );

    const { default: InboxPage } = await import("../features/inbox/InboxPage");
    const { render, screen, fireEvent } = await import("@testing-library/react");
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

    fireEvent.click(await screen.findByTestId("inbox-conv-conv-a"));
    expect(await screen.findByTestId("inbox-tags-row")).toBeInTheDocument();
    expect(await screen.findByTestId("inbox-tag-chip-tag-1")).toHaveTextContent(
      "vip",
    );
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});
