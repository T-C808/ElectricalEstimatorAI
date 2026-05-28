import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { App } from "../src/app/App";

function renderApp() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>,
  );
}

describe("customer form", () => {
  it("submits the populated company field without required validation", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/customers") && init?.method === "POST") {
        return Response.json({
          id: "customer-1",
          company_name: "Demo Customer",
          contact_name: "",
          email: "",
          phone: "",
          billing_address: "",
          notes: "",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      }
      if (url.endsWith("/customers")) return Response.json([]);
      if (url.endsWith("/jobs")) return Response.json([]);
      if (url.endsWith("/estimates")) return Response.json([]);
      return Response.json([]);
    });
    vi.stubGlobal("fetch", fetchMock);

    renderApp();

    fireEvent.click(screen.getAllByRole("button", { name: "Customers" })[0]);
    fireEvent.change(screen.getByLabelText("Company"), {
      target: { value: "Demo Customer" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create Customer" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/customers"),
        expect.objectContaining({
          method: "POST",
          body: expect.stringContaining("Demo Customer"),
        }),
      );
    });
    expect(screen.queryByText("Company is required")).not.toBeInTheDocument();
  });
});
