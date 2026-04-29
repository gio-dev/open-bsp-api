import { afterEach, describe, expect, it, vi } from "vitest";

/** ATDD Epic 5 Story 5.1 ? editor fluxos + validate. */

describe("ATDD Epic 5 Story 5.1 flow editor", () => {
  it("exports FlowEditorPage", async () => {
    const mod = await import("../features/flows/FlowEditorPage");
    expect(mod.default).toBeTypeOf("function");
  });

  it("renders flow editor root after validate mocked", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ valid: true, errors: [] }),
      }),
    );
    const { default: FlowEditorPage } = await import(
      "../features/flows/FlowEditorPage"
    );
    const { render, screen } = await import("@testing-library/react");
    const { ChakraProvider, defaultSystem } = await import("@chakra-ui/react");
    render(
      <ChakraProvider value={defaultSystem}>
        <FlowEditorPage />
      </ChakraProvider>,
    );
    expect(screen.getByTestId("flow-editor-root")).toBeInTheDocument();
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});
