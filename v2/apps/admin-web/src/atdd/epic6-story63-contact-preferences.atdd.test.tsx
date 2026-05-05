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
          contact_id: "15550009999",
          marketing_opt_in: false,
          transactional_allowed: true,
          disclosure_copy_slug: "baseline-v1",
          marketing_consent_recorded_at: null,
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
          initialEntries={["/privacy/contacts/15550009999/preferences"]}
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
    ).toHaveTextContent(/15550009999/);
  });

  it("PATCH gravacao inclui Content-Type e cabecalhos stub", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          contact_id: "15550009999",
          marketing_opt_in: false,
          transactional_allowed: true,
          disclosure_copy_slug: "baseline-v1",
          marketing_consent_recorded_at: null,
          updated_at: "2026-01-01T00:00:00Z",
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          contact_id: "15550009999",
          marketing_opt_in: false,
          transactional_allowed: true,
          disclosure_copy_slug: "baseline-v1",
          marketing_consent_recorded_at: null,
          updated_at: "2026-01-01T01:00:00Z",
        }),
      });
    vi.stubGlobal("fetch", fetchMock);

    const { default: ContactPreferencesPage } = await import(
      "../features/privacy/ContactPreferencesPage"
    );
    const { fireEvent, render, screen } = await import("@testing-library/react");
    const {
      MemoryRouter,
      Routes,
      Route,
    } = await import("react-router-dom");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");

    render(
      <ChakraProvider value={defaultSystem}>
        <MemoryRouter
          initialEntries={["/privacy/contacts/15550009999/preferences"]}
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

    await screen.findByTestId("contact-prefs-save");
    fireEvent.click(screen.getByTestId("contact-prefs-save"));

    expect(fetchMock).toHaveBeenCalledTimes(2);
    const [, patchInit] = fetchMock.mock.calls[1];
    expect(patchInit).toMatchObject({ method: "PATCH" });
    expect(patchInit.headers).toMatchObject({
      "Content-Type": "application/json",
      "X-Dev-Tenant-Id": expect.any(String),
    });
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});
