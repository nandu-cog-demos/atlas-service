import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FleetDashboard } from "./FleetDashboard";

vi.mock("../hooks/useTelemetry", () => ({
  useTelemetry: () => ({
    vehicles: [
      {
        id: "v-001",
        name: "Truck Alpha",
        status: "active",
        last_latitude: 37.7749,
        last_longitude: -122.4194,
        last_seen: "2024-01-15T10:30:00Z",
      },
      {
        id: "v-002",
        name: "Van Bravo",
        status: "idle",
        last_latitude: null,
        last_longitude: null,
        last_seen: null,
      },
    ],
    loading: false,
    error: null,
    refresh: vi.fn(),
  }),
}));

vi.mock("../hooks/useAlerts", () => ({
  useAlerts: () => ({
    alerts: [],
    unacknowledgedCount: 0,
    loading: false,
    error: null,
    acknowledge: vi.fn(),
    refresh: vi.fn(),
  }),
}));

describe("FleetDashboard", () => {
  it("renders the vehicle list", () => {
    render(<FleetDashboard />);
    expect(screen.getByText("Atlas Fleet Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Truck Alpha")).toBeInTheDocument();
    expect(screen.getByText("Van Bravo")).toBeInTheDocument();
  });

  it("displays vehicle statuses", () => {
    render(<FleetDashboard />);
    expect(screen.getByText("active")).toBeInTheDocument();
    expect(screen.getByText("idle")).toBeInTheDocument();
  });
});
