import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AlertsPanel } from "./AlertsPanel";

const alerts = [
  {
    id: "alert-001",
    zone_event_id: "event-001",
    vehicle_id: "v-001",
    zone_id: "zone-001",
    created_at: "2024-03-01T10:00:00Z",
    acknowledged: false,
    acknowledged_by: null,
    acknowledged_at: null,
  },
  {
    id: "alert-002",
    zone_event_id: "event-002",
    vehicle_id: "v-002",
    zone_id: "zone-002",
    created_at: "2024-03-01T09:00:00Z",
    acknowledged: true,
    acknowledged_by: "op-001",
    acknowledged_at: "2024-03-01T09:30:00Z",
  },
];

const fetchMock = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

function response(data: unknown) {
  return Promise.resolve({
    ok: true,
    json: async () => data,
  });
}

describe("AlertsPanel", () => {
  it("renders alerts and the unacknowledged count", async () => {
    fetchMock.mockReturnValue(response(alerts));

    render(<AlertsPanel />);

    await waitFor(() => {
      expect(screen.getByText("Vehicle v-001")).toBeInTheDocument();
    });
    expect(screen.getByText("Zone zone-001")).toBeInTheDocument();
    expect(screen.getByText("Zone zone-002")).toBeInTheDocument();
    expect(screen.getByLabelText("1 unacknowledged alerts")).toHaveTextContent("1");
    expect(screen.getByText("Acknowledged")).toBeInTheDocument();
    expect(screen.getByText("Unacknowledged")).toBeInTheDocument();
  });

  it("acknowledges an alert and updates without waiting for a reload", async () => {
    const acknowledgedAlert = {
      ...alerts[0],
      acknowledged: true,
      acknowledged_by: "op-001",
      acknowledged_at: "2024-03-01T10:01:00Z",
    };
    fetchMock
      .mockReturnValueOnce(response(alerts))
      .mockReturnValueOnce(response(acknowledgedAlert));

    render(<AlertsPanel />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Acknowledge" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Acknowledge" }));

    await waitFor(() => {
      expect(screen.queryByRole("button", { name: "Acknowledge" })).not.toBeInTheDocument();
    });
    expect(screen.getByLabelText("0 unacknowledged alerts")).toHaveTextContent("0");
    expect(screen.getAllByText("Acknowledged")).toHaveLength(2);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/alerts/alert-001/acknowledge",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("renders an empty state when there are no alerts", async () => {
    fetchMock.mockReturnValue(response([]));

    render(<AlertsPanel />);

    await waitFor(() => {
      expect(screen.getByText("No alerts")).toBeInTheDocument();
    });
    expect(screen.getByLabelText("0 unacknowledged alerts")).toHaveTextContent("0");
  });
});
