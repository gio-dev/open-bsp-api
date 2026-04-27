import { afterEach, describe, expect, it, vi } from "vitest";

describe("ATDD Epic 2 Story 2.3 integrations page", () => {
  it("exports IntegrationsPage from features/integrations", async () => {
    const mod = await import("../features/integrations/IntegrationsPage");
    expect(mod.default).toBeTypeOf("function");
  });

  it("exposes data-testid integrations-heading", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ items: [] }),
      }),
    );
    const { default: IntegrationsPage } = await import(
      "../features/integrations/IntegrationsPage"
    );
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    render(
      <ChakraProvider value={defaultSystem}>
        <IntegrationsPage />
      </ChakraProvider>,
    );
    expect(screen.getByTestId("integrations-heading")).toBeInTheDocument();
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});
