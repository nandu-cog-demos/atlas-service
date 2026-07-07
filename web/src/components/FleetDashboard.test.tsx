import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Vehicle } from "../api/client";
import { FleetDashboard } from "./FleetDashboard";

const truckAlpha: Vehicle = {
  id: "v-001",
  name: "Truck Alpha",
  status: "active",
  last_latitude: 37.7749,
  last_longitude: -122.4194,
  last_seen: "2024-01-15T10:30:00Z",
};

const vanBravo: Vehicle = {
  id: "v-002",
  name: "Van Bravo",
  status: "idle",
  last_latitude: null,
  last_longitude: null,
  last_seen: null,
};

let mockVehicles: Vehicle[] = [truckAlpha, vanBravo];

vi.mock("../hooks/useTelemetry", () => ({
  useTelemetry: () => ({
    vehicles: mockVehicles,
    loading: false,
    error: null,
    refresh: vi.fn(),
  }),
}));

describe("FleetDashboard", () => {
  beforeEach(() => {
    mockVehicles = [truckAlpha, vanBravo];
  });

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

  it("shows the total vehicle count in the header", () => {
    render(<FleetDashboard />);
    expect(screen.getByText("2 vehicles")).toBeInTheDocument();
  });

  it("updates the count when the vehicle data changes", () => {
    const { rerender } = render(<FleetDashboard />);
    expect(screen.getByText("2 vehicles")).toBeInTheDocument();

    mockVehicles = [truckAlpha, vanBravo, { ...truckAlpha, id: "v-003" }];
    rerender(<FleetDashboard />);
    expect(screen.getByText("3 vehicles")).toBeInTheDocument();
  });

  it("uses the singular label for exactly one vehicle", () => {
    mockVehicles = [truckAlpha];
    render(<FleetDashboard />);
    expect(screen.getByText("1 vehicle")).toBeInTheDocument();
  });

  it("uses the plural label when there are no vehicles", () => {
    mockVehicles = [];
    render(<FleetDashboard />);
    expect(screen.getByText("0 vehicles")).toBeInTheDocument();
  });
});
