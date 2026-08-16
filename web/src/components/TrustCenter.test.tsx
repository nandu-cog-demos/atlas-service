import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TrustCenter } from "./TrustCenter";

vi.mock("../api/client", () => ({
  fetchTrustCenter: () =>
    Promise.resolve({
      overview: "Atlas keeps your data safe.",
      last_updated: "2026-07-01",
      certifications: [
        { name: "SOC 2 Type II", status: "certified", description: "Audited." },
        { name: "HIPAA", status: "in_progress", description: "Underway." },
      ],
      security_practices: [
        { category: "Data Protection", items: ["AES-256 at rest"] },
      ],
      subprocessors: [
        { name: "Amazon Web Services", purpose: "Hosting", location: "US" },
      ],
      service_status: {
        state: "operational",
        uptime_90d: 99.98,
        status_page_url: "https://status.example.com",
      },
      resources: [
        { label: "Privacy Policy", url: "https://example.com/privacy" },
      ],
    }),
}));

describe("TrustCenter", () => {
  it("renders trust center content", async () => {
    render(<TrustCenter />);

    expect(await screen.findByText("Atlas Trust Center")).toBeInTheDocument();
    expect(screen.getByText("SOC 2 Type II")).toBeInTheDocument();
    expect(screen.getByText("Data Protection")).toBeInTheDocument();
    expect(screen.getByText("Amazon Web Services")).toBeInTheDocument();
    expect(screen.getByText("Privacy Policy →")).toBeInTheDocument();
  });

  it("shows operational service status", async () => {
    render(<TrustCenter />);
    await waitFor(() =>
      expect(screen.getByText("All systems operational")).toBeInTheDocument(),
    );
    expect(screen.getByText("99.98% uptime (90d)")).toBeInTheDocument();
  });
});
