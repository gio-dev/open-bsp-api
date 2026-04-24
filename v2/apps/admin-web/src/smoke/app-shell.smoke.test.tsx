import { ChakraProvider, defaultSystem } from "@chakra-ui/react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "../App";

describe("smoke: admin shell", () => {
  it("renders root heading", () => {
    render(
      <ChakraProvider value={defaultSystem}>
        <App />
      </ChakraProvider>,
    );
    expect(screen.getByRole("heading", { name: /open bsp admin/i })).toBeInTheDocument();
  });
});
