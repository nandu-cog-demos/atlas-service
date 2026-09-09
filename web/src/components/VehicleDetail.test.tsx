import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { updateVehicleStatus } from "../api/client";
import { VehicleDetail } from "./VehicleDetail";

vi.mock("../api/client", () => ({
  updateVehicleStatus: vi.fn(),
}));

describe("VehicleDetail", () => {
  it("updates status via the API and notifies the parent", async () => {
    const vehicle = {
      id: "v-001",
      name: "Truck Alpha",
      status: "active" as const,
      last_latitude: 37.7749,
      last_longitude: -122.4194,
      last_seen: "2024-01-15T10:30:00Z",
    };
    const updated = { ...vehicle, status: "maintenance" as const };
    vi.mocked(updateVehicleStatus).mockResolvedValue(updated);
    const onStatusChanged = vi.fn();

    render(<VehicleDetail vehicle={vehicle} onStatusChanged={onStatusChanged} />);
    fireEvent.change(screen.getByLabelText("Set vehicle status"), {
      target: { value: "maintenance" },
    });

    await waitFor(() => expect(onStatusChanged).toHaveBeenCalledWith(updated));
    expect(updateVehicleStatus).toHaveBeenCalledWith("v-001", "maintenance");
  });

  it("hides the status control when no handler is provided", () => {
    const vehicle = {
      id: "v-001",
      name: "Truck Alpha",
      status: "active" as const,
      last_latitude: null,
      last_longitude: null,
      last_seen: null,
    };
    render(<VehicleDetail vehicle={vehicle} />);
    expect(screen.queryByLabelText("Set vehicle status")).not.toBeInTheDocument();
  });

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
