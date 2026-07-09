import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Vehicle } from "../api/client";
import { FleetDashboard } from "./FleetDashboard";

const useTelemetryMock = vi.fn();

vi.mock("../hooks/useTelemetry", () => ({
  useTelemetry: () => useTelemetryMock(),
}));

const vehicleA: Vehicle = {
  id: "v-001",
  name: "Truck Alpha",
  status: "active",
  last_latitude: 37.7749,
  last_longitude: -122.4194,
  last_seen: "2024-01-15T10:30:00Z",
};

const vehicleB: Vehicle = {
  id: "v-002",
  name: "Van Bravo",
  status: "idle",
  last_latitude: null,
  last_longitude: null,
  last_seen: null,
};

function mockTelemetry(vehicles: Vehicle[]) {
  useTelemetryMock.mockReturnValue({
    vehicles,
    loading: false,
    error: null,
    refresh: vi.fn(),
  });
}

beforeEach(() => {
  useTelemetryMock.mockReset();
  mockTelemetry([vehicleA, vehicleB]);
});

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

  it("renders the vehicle count badge with the correct count", () => {
    render(<FleetDashboard />);
    expect(screen.getByText("2 vehicles")).toBeInTheDocument();
  });

  it("updates the count when vehicle data changes", () => {
    const { rerender } = render(<FleetDashboard />);
    expect(screen.getByText("2 vehicles")).toBeInTheDocument();

    mockTelemetry([vehicleA, vehicleB, { ...vehicleA, id: "v-003" }]);
    rerender(<FleetDashboard />);
    expect(screen.getByText("3 vehicles")).toBeInTheDocument();
  });

  it("uses the singular label for a single vehicle", () => {
    mockTelemetry([vehicleA]);
    render(<FleetDashboard />);
    expect(screen.getByText("1 vehicle")).toBeInTheDocument();
  });

  it("shows a zero count with the plural label", () => {
    mockTelemetry([]);
    render(<FleetDashboard />);
    expect(screen.getByText("0 vehicles")).toBeInTheDocument();
  });
});
