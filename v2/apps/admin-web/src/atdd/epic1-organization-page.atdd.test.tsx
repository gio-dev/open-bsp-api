import { afterEach, describe, expect, it, vi } from "vitest";

/**
 * ATDD Story 1.3 - organization settings page (RED until DS).
 * DS: add src/features/organization/OrganizationSettingsPage.tsx (default export).
 */
describe("ATDD Epic 1 Story 1.3 organization page", () => {
  it("exports OrganizationSettingsPage from features/organization", async () => {
    const mod = await import("../features/organization/OrganizationSettingsPage");
    expect(mod.default).toBeTypeOf("function");
  });

  it("exposes data-testid org-settings-heading", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          display_name: "Test Org",
          timezone: "UTC",
          operational_email: "",
        }),
      }),
    );
    const { default: OrganizationSettingsPage } = await import(
      "../features/organization/OrganizationSettingsPage"
    );
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    render(
      <ChakraProvider value={defaultSystem}>
        <OrganizationSettingsPage />
      </ChakraProvider>,
    );
    expect(screen.getByTestId("org-settings-heading")).toBeInTheDocument();
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});
