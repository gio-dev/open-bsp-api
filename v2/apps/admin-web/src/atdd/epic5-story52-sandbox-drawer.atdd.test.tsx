import { expect, it } from "vitest";

/** ATDD Story 5.2 ? drawer sandbox inbox. */

import SandboxFlowDrawer from "../features/inbox/SandboxFlowDrawer";

it("exports SandboxFlowDrawer", () => {
  expect(SandboxFlowDrawer).toBeTypeOf("function");
});
