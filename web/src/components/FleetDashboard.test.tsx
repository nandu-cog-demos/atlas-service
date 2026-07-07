import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Vehicle } from "../api/client";
import { FleetDashboard } from "./FleetDashboard";

const telemetryState = vi.hoisted(() => ({
  vehicles: [] as Vehicle[],
  loading: false,
  error: null as string | null,
}));

vi.mock("../hooks/useTelemetry", () => ({
  useTelemetry: () => ({
    vehicles: telemetryState.vehicles,
    loading: telemetryState.loading,
    error: telemetryState.error,
    refresh: vi.fn(),
  }),
}));

function makeVehicle(id: string, name: string): Vehicle {
  return {
    id,
    name,
    status: "active",
    last_latitude: null,
    last_longitude: null,
    last_seen: null,
  };
}

beforeEach(() => {
  telemetryState.vehicles = [
    makeVehicle("v-001", "Truck Alpha"),
    makeVehicle("v-002", "Van Bravo"),
  ];
  telemetryState.loading = false;
  telemetryState.error = null;
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
    expect(screen.getAllByText("active")).toHaveLength(2);
  });

  it("shows the total vehicle count badge", () => {
    render(<FleetDashboard />);
    expect(screen.getByText("2 vehicles")).toBeInTheDocument();
  });

  it("uses singular wording for exactly one vehicle", () => {
    telemetryState.vehicles = [makeVehicle("v-001", "Truck Alpha")];
    render(<FleetDashboard />);
    expect(screen.getByText("1 vehicle")).toBeInTheDocument();
  });

  it("uses plural wording when there are no vehicles", () => {
    telemetryState.vehicles = [];
    render(<FleetDashboard />);
    expect(screen.getByText("0 vehicles")).toBeInTheDocument();
  });

  it("updates the count reactively when vehicle data changes", () => {
    const { rerender } = render(<FleetDashboard />);
    expect(screen.getByText("2 vehicles")).toBeInTheDocument();

    telemetryState.vehicles = [
      makeVehicle("v-001", "Truck Alpha"),
      makeVehicle("v-002", "Van Bravo"),
      makeVehicle("v-003", "Car Charlie"),
    ];
    rerender(<FleetDashboard />);
    expect(screen.getByText("3 vehicles")).toBeInTheDocument();
  });
});
