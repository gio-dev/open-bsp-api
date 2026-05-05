import type { RunOptions } from "axe-core";
import { ChakraProvider, defaultSystem } from "@chakra-ui/react";
import { render, screen, waitFor } from "@testing-library/react";
import { axe } from "jest-axe";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import EmbedPanelPage from "../features/embed/EmbedPanelPage";

/**
 * JSDOM nao calcula estilos reais; color-contrast fica para o checklist browser
 * (Story 6.4 AC2).
 */
const AXE_JSDOM: RunOptions = {
  rules: { "color-contrast": { enabled: false } },
};

function renderEmbedAt(path: string) {
  return render(
    <ChakraProvider value={defaultSystem}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/embed/panel" element={<EmbedPanelPage />} />
        </Routes>
      </MemoryRouter>
    </ChakraProvider>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("ATDD Epic 6 Story 6.4 embed a11y", () => {
  it("need_token: h1, landmark main, skip link (tab order baseline)", () => {
    renderEmbedAt("/embed/panel");
    expect(screen.getByTestId("embed-panel-need-token")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      /Embed authentication required/i,
    );
    expect(screen.getByRole("main")).toHaveAttribute("id", "embed-main-content");
    expect(
      screen.getByRole("link", { name: /skip to main content/i }),
    ).toHaveAttribute("href", "#embed-main-content");
  });

  it("need_token: jest-axe sem violacoes (regras compativeis com JSDOM)", async () => {
    const { container } = renderEmbedAt("/embed/panel");
    expect(await axe(container, AXE_JSDOM)).toHaveNoViolations();
  });

  it("loading: jest-axe enquanto valida token", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => new Promise<Response>(() => {})),
    );
    const { container } = renderEmbedAt("/embed/panel?token=pending");
    await waitFor(() => {
      expect(screen.getByTestId("embed-panel-loading")).toBeInTheDocument();
    });
    expect(await axe(container, AXE_JSDOM)).toHaveNoViolations();
  });

  it("ok: jest-axe apos validacao bem-sucedida", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ tenant_id: "t" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    const { container } = renderEmbedAt("/embed/panel?token=ok-token");
    await waitFor(() => {
      expect(screen.getByTestId("embed-panel-ok")).toBeInTheDocument();
    });
    expect(await axe(container, AXE_JSDOM)).toHaveNoViolations();
  });

  it("error: jest-axe na mensagem de erro", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ message: "validation failed" }), {
          status: 422,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    const { container } = renderEmbedAt("/embed/panel?token=bad-token");
    await waitFor(() => {
      expect(screen.getByTestId("embed-panel-error")).toBeInTheDocument();
    });
    expect(await axe(container, AXE_JSDOM)).toHaveNoViolations();
  });

  it("refresh: jest-axe quando sessao expira (401)", async () => {
    vi.stubGlobal("fetch", () =>
      Promise.resolve(
        new Response(null, {
          status: 401,
          headers: { "x-request-id": "req-embed-401" },
        }),
      ),
    );

    const { container } = renderEmbedAt("/embed/panel?token=expired");
    await waitFor(() => {
      expect(screen.getByTestId("embed-panel-refresh")).toBeInTheDocument();
    });
    expect(await axe(container, AXE_JSDOM)).toHaveNoViolations();
  });
});
