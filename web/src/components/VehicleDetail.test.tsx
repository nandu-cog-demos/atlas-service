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
    };
    render(<VehicleDetail vehicle={vehicle} />);
    expect(screen.getByText("Truck Alpha")).toBeInTheDocument();
    expect(screen.getByText("v-001")).toBeInTheDocument();
    expect(screen.getByText("37.7749, -122.4194")).toBeInTheDocument();
  });

  it("renders unknown position when coordinates are null", () => {
    const vehicle = {
      id: "v-003",
      name: "Truck Charlie",
      status: "maintenance" as const,
      last_latitude: null,
      last_longitude: null,
      last_seen: null,
    };
    render(<VehicleDetail vehicle={vehicle} />);
    expect(screen.getByText("Unknown")).toBeInTheDocument();
    expect(screen.getByText("Never")).toBeInTheDocument();
  });
});
