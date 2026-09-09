import { fireEvent, render, screen, waitFor } from "@testing-library/react";
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

vi.mock("../api/client", () => ({
  fetchFleetSummary: vi.fn().mockResolvedValue({
    total_vehicles: 2,
    by_status: { active: 1, idle: 1, maintenance: 0, offline: 0 },
    average_fuel_level: 72.5,
    average_speed_kmh: 55,
    stale_vehicles: 1,
    stale_threshold_minutes: 30,
  }),
  updateVehicleStatus: vi.fn(),
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
    expect(screen.getByText("active", { selector: ".status-badge" })).toBeInTheDocument();
    expect(screen.getByText("idle", { selector: ".status-badge" })).toBeInTheDocument();
  });

  it("renders the fleet summary", async () => {
    render(<FleetDashboard />);
    await waitFor(() => {
      expect(screen.getByTestId("summary-total")).toHaveTextContent("2");
    });
    expect(screen.getByTestId("summary-active")).toHaveTextContent("1");
    expect(screen.getByTestId("summary-stale")).toHaveTextContent("1");
    expect(screen.getByText("72.5 %")).toBeInTheDocument();
  });

  it("filters vehicles by status", () => {
    render(<FleetDashboard />);
    fireEvent.change(screen.getByLabelText("Filter by status"), {
      target: { value: "idle" },
    });
    expect(screen.queryByText("Truck Alpha")).not.toBeInTheDocument();
    expect(screen.getByText("Van Bravo")).toBeInTheDocument();
    expect(screen.getByText("1 of 2")).toBeInTheDocument();
  });

  it("filters vehicles by search text", () => {
    render(<FleetDashboard />);
    fireEvent.change(screen.getByLabelText("Search vehicles"), {
      target: { value: "alpha" },
    });
    expect(screen.getByText("Truck Alpha")).toBeInTheDocument();
    expect(screen.queryByText("Van Bravo")).not.toBeInTheDocument();
  });

  it("shows an empty state when nothing matches", () => {
    render(<FleetDashboard />);
    fireEvent.change(screen.getByLabelText("Filter by status"), {
      target: { value: "offline" },
    });
    expect(
      screen.getByText("No vehicles match the current filters."),
    ).toBeInTheDocument();
  });

  it("shows vehicle detail when a row is clicked", () => {
    render(<FleetDashboard />);
    fireEvent.click(screen.getByText("Truck Alpha"));
    expect(screen.getByText("v-001")).toBeInTheDocument();
    expect(screen.getByLabelText("Set vehicle status")).toBeInTheDocument();
  });
});
