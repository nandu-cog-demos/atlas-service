import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { FleetDashboard } from "./FleetDashboard";

const telemetry = vi.hoisted(() => ({ vehicles: [] as unknown[] }));

vi.mock("../hooks/useTelemetry", () => ({
  useTelemetry: () => ({
    vehicles: telemetry.vehicles,
    loading: false,
    error: null,
    refresh: () => {},
  }),
}));

const baseVehicles = [
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
];

describe("FleetDashboard", () => {
  beforeEach(() => {
    telemetry.vehicles = baseVehicles;
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

  it("keeps the selected vehicle detail in sync with refreshed data", () => {
    const { rerender } = render(<FleetDashboard />);
    fireEvent.click(screen.getByText("Van Bravo"));
    expect(screen.getAllByText("Low fuel")).toHaveLength(2);

    telemetry.vehicles = baseVehicles.map((v) =>
      v.id === "v-002" ? { ...v, fuel_level: 80, low_fuel: false } : v,
    );
    rerender(<FleetDashboard />);
    expect(screen.queryByText("Low fuel")).not.toBeInTheDocument();
    expect(screen.getAllByText("80%")).toHaveLength(2);
  });
});
