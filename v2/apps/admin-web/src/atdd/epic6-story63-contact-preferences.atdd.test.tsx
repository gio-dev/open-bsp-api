import { afterEach, describe, expect, it, vi } from "vitest";

/** ATDD Story 6.3 - consent preferences UI shell. */
describe("ATDD Epic 6 Story 6.3 contact preferences page", () => {
  it("exports ContactPreferencesPage", async () => {
    const mod = await import("../features/privacy/ContactPreferencesPage");
    expect(mod.default).toBeTypeOf("function");
  });

  it("renders heading with mocked preferences GET", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          contact_id: "fixture-a",
          marketing_opt_in: false,
          transactional_allowed: true,
          disclosure_copy_slug: "baseline-v1",
          updated_at: "2026-01-01T00:00:00Z",
        }),
      }),
    );
    const { default: ContactPreferencesPage } = await import(
      "../features/privacy/ContactPreferencesPage"
    );
    const { render, screen } = await import("@testing-library/react");
    const {
      MemoryRouter,
      Routes,
      Route,
    } = await import("react-router-dom");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    render(
      <ChakraProvider value={defaultSystem}>
        <MemoryRouter
          initialEntries={["/privacy/contacts/fixture-a/preferences"]}
        >
          <Routes>
            <Route
              path="/privacy/contacts/:contactId/preferences"
              element={<ContactPreferencesPage />}
            />
          </Routes>
        </MemoryRouter>
      </ChakraProvider>,
    );

    expect(
      await screen.findByTestId("contact-preferences-heading"),
    ).toHaveTextContent(/fixture-a/);
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});
