import { afterEach, describe, expect, it, vi } from "vitest";

/**
 * ATDD Story 3.3 - Message templates + channel signals (admin skeleton).
 */
describe("ATDD Epic 3 Story 3.3 message templates page", () => {
  it("exports MessageTemplatesPage", async () => {
    const mod = await import("../features/templates/MessageTemplatesPage");
    expect(mod.default).toBeTypeOf("function");
  });

  it("renders signals block and template row after fetch", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          waba_id: "waba_x",
          environment: "production",
          items: [
            {
              id: "00000000-0000-4000-8000-000000000099",
              name: "hello",
              language: "pt_PT",
              display_status: "approved",
              meta_status: "APPROVED",
            },
          ],
          last_sync_at: "2026-01-01T00:00:00+00:00",
          channel_signals: {
            source: "stub",
            quality_rating: "GREEN",
            volume_incidents_crossref: false,
          },
        }),
      }),
    );
    const { default: MessageTemplatesPage } = await import(
      "../features/templates/MessageTemplatesPage"
    );
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    render(
      <ChakraProvider value={defaultSystem}>
        <MessageTemplatesPage />
      </ChakraProvider>,
    );
    expect(screen.getByTestId("msg-templates-root")).toBeInTheDocument();
    expect(await screen.findByTestId("msg-templates-signals")).toBeInTheDocument();
    expect(await screen.findByTestId("msg-templates-status")).toHaveTextContent(
      "approved",
    );
  });

  it("retries templates with phone_number_id after 409 when only one WABA line exists", async () => {
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce({
        ok: false,
        status: 409,
        json: async () => ({
          message: "multiple whatsapp numbers match",
          code: "http_409",
          request_id: "r1",
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: "line-1",
              waba_id: "waba_only",
              phone_number_id: "pn_auto",
              display_phone_number: "+351 910000000",
              environment: "production",
              status: "active",
            },
          ],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          waba_id: "waba_only",
          environment: "production",
          items: [
            {
              id: "tpl-1",
              name: "hello",
              language: "pt_PT",
              display_status: "approved",
              meta_status: "APPROVED",
            },
          ],
          last_sync_at: null,
          channel_signals: { source: "stub", volume_incidents_crossref: false },
        }),
      });
    vi.stubGlobal("fetch", fetchMock);

    const { default: MessageTemplatesPage } = await import(
      "../features/templates/MessageTemplatesPage"
    );
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    render(
      <ChakraProvider value={defaultSystem}>
        <MessageTemplatesPage />
      </ChakraProvider>,
    );

    expect(await screen.findByTestId("msg-templates-phone-ref")).toHaveTextContent(
      "pn_auto",
    );
    expect(fetchMock).toHaveBeenCalledTimes(3);
    const secondTemplatesCall = fetchMock.mock.calls[2][0] as string;
    expect(secondTemplatesCall).toContain("phone_number_id=pn_auto");
  });

  it("shows line picker after 409 when several WABA lines exist", async () => {
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce({
        ok: false,
        status: 409,
        json: async () => ({
          message: "narrow with phone_number_id",
          code: "http_409",
          request_id: "r1",
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: "a",
              waba_id: "w1",
              phone_number_id: "pn_a",
              display_phone_number: "+1",
              environment: "production",
              status: "active",
            },
            {
              id: "b",
              waba_id: "w1",
              phone_number_id: "pn_b",
              display_phone_number: "+2",
              environment: "production",
              status: "active",
            },
          ],
        }),
      });
    vi.stubGlobal("fetch", fetchMock);

    const { default: MessageTemplatesPage } = await import(
      "../features/templates/MessageTemplatesPage"
    );
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    render(
      <ChakraProvider value={defaultSystem}>
        <MessageTemplatesPage />
      </ChakraProvider>,
    );

    expect(await screen.findByTestId("msg-templates-line-picker")).toBeInTheDocument();
    expect(screen.getByTestId("msg-templates-error")).toHaveTextContent(
      "narrow with phone_number_id",
    );
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
  try {
    sessionStorage.clear();
  } catch {
    /* ignore */
  }
});
