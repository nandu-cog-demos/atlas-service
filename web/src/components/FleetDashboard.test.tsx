import { fireEvent, render, screen } from "@testing-library/react";
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
        fuel_level: 62.5,
        low_fuel: false,
      },
      {
        id: "v-002",
        name: "Van Bravo",
        status: "idle",
        last_latitude: null,
        last_longitude: null,
        last_seen: null,
        fuel_level: 11,
        low_fuel: true,
      },
    ],
    loading: false,
    error: null,
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

  it("shows fuel levels and flags low fuel vehicles", () => {
    render(<FleetDashboard />);
    expect(screen.getByText("63%")).toBeInTheDocument();
    expect(screen.getByText("11%")).toBeInTheDocument();
    expect(screen.getByText("Low fuel")).toBeInTheDocument();
    expect(screen.getByText("1 low fuel")).toBeInTheDocument();
  });

  it("filters to low fuel vehicles only", () => {
    render(<FleetDashboard />);
    fireEvent.click(screen.getByLabelText("Low fuel only"));
    expect(screen.queryByText("Truck Alpha")).not.toBeInTheDocument();
    expect(screen.getByText("Van Bravo")).toBeInTheDocument();
  });
});
