import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VehicleDetail } from "./VehicleDetail";

describe("VehicleDetail", () => {
  it("renders vehicle information", () => {
    const vehicle = {
      id: "v-001",
      name: "Truck Alpha",
      status: "active" as const,
      last_latitude: 37.7749,
      last_longitude: -122.4194,
      last_seen: "2024-01-15T10:30:00Z",
      fuel_level: 62.5,
      low_fuel: false,
    };
    render(<VehicleDetail vehicle={vehicle} />);
    expect(screen.getByText("Truck Alpha")).toBeInTheDocument();
    expect(screen.getByText("v-001")).toBeInTheDocument();
    expect(screen.getByText("37.7749, -122.4194")).toBeInTheDocument();
    expect(screen.getByText("63%")).toBeInTheDocument();
    expect(screen.queryByText("Low fuel")).not.toBeInTheDocument();
  });

  it("flags low fuel", () => {
    const vehicle = {
      id: "v-002",
      name: "Van Bravo",
      status: "idle" as const,
      last_latitude: 37.3382,
      last_longitude: -121.8863,
      last_seen: "2024-01-15T09:15:00Z",
      fuel_level: 11,
      low_fuel: true,
    };
    render(<VehicleDetail vehicle={vehicle} />);
    expect(screen.getByText("11%")).toBeInTheDocument();
    expect(screen.getByText("Low fuel")).toBeInTheDocument();
  });

  it("renders unknown position when coordinates are null", () => {
    const vehicle = {
      id: "v-003",
      name: "Truck Charlie",
      status: "maintenance" as const,
      last_latitude: null,
      last_longitude: null,
      last_seen: null,
      fuel_level: null,
      low_fuel: false,
    };
    render(<VehicleDetail vehicle={vehicle} />);
    expect(screen.getByText("Unknown")).toBeInTheDocument();
    expect(screen.getByText("Never")).toBeInTheDocument();
  });
});
