import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AlertsPanel } from "./AlertsPanel";

const rule = {
  id: "rule-1",
  name: "Low fuel",
  metric: "fuel_level",
  operator: "lt" as const,
  threshold: 15,
  severity: "warning" as const,
  enabled: true,
  created_by: "op-001",
  created_at: "2024-01-15T10:00:00Z",
};

const alert = {
  id: "alert-1",
  rule_id: "rule-1",
  vehicle_id: "v-001",
  metric_value: 9.5,
  severity: "warning" as const,
  acknowledged: false,
  fired_at: "2024-01-15T10:30:00Z",
};

const mocks = vi.hoisted(() => ({
  fetchAlertRules: vi.fn(),
  fetchAlerts: vi.fn(),
  toggleAlertRule: vi.fn(),
  acknowledgeAlert: vi.fn(),
}));

vi.mock("../api/client", () => mocks);

describe("AlertsPanel", () => {
  beforeEach(() => {
    mocks.fetchAlertRules.mockResolvedValue([rule]);
    mocks.fetchAlerts.mockResolvedValue([alert]);
    mocks.toggleAlertRule.mockResolvedValue({ ...rule, enabled: false });
    mocks.acknowledgeAlert.mockResolvedValue({ ...alert, acknowledged: true });
  });

  it("renders rules and the alert feed", async () => {
    render(<AlertsPanel />);
    expect(await screen.findAllByText("Low fuel")).toHaveLength(2);
    expect(screen.getByText("v-001")).toBeInTheDocument();
    expect(screen.getByText("9.5")).toBeInTheDocument();
  });

  it("toggles a rule and reflects the new state", async () => {
    render(<AlertsPanel />);
    fireEvent.click(await screen.findByRole("button", { name: "Disable" }));
    await waitFor(() => expect(mocks.toggleAlertRule).toHaveBeenCalledWith("rule-1", false));
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Enable" })).toBeInTheDocument(),
    );
  });

  it("removes an acknowledged alert from the unacknowledged view", async () => {
    render(<AlertsPanel />);
    fireEvent.click(await screen.findByRole("button", { name: "Ack" }));
    await waitFor(() => expect(mocks.acknowledgeAlert).toHaveBeenCalledWith("alert-1"));
    await waitFor(() =>
      expect(screen.getByText("No alerts to show.")).toBeInTheDocument(),
    );
  });
});
