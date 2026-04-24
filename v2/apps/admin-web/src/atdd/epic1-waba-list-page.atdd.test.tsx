import { afterEach, describe, expect, it, vi } from "vitest";

/**
 * ATDD Story 1.4 - WABA / phone list.
 */
describe("ATDD Epic 1 Story 1.4 WABA list", () => {
  it("exports WabaPhoneNumberListPage from features/waba", async () => {
    const mod = await import("../features/waba/WabaPhoneNumberListPage");
    expect(mod.default).toBeTypeOf("function");
  });

  it("exposes data-testid waba-list-root and status badge", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              id: "00000000-0000-4000-8000-000000000001",
              waba_id: "waba_1",
              phone_number_id: "pn_1",
              display_phone_number: "+10000000001",
              environment: "production",
              status: "pending",
            },
          ],
          limit: 50,
        }),
      }),
    );
    const { default: WabaPhoneNumberListPage } = await import(
      "../features/waba/WabaPhoneNumberListPage"
    );
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    render(
      <ChakraProvider value={defaultSystem}>
        <WabaPhoneNumberListPage />
      </ChakraProvider>,
    );
    expect(screen.getByTestId("waba-list-root")).toBeInTheDocument();
    expect(await screen.findByTestId("waba-status-badge")).toHaveTextContent(
      "pending",
    );
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});
