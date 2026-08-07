const BASE_URL = "/api/v1";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("atlas_token") ?? "";
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export interface Vehicle {
  id: string;
  name: string;
  status: "active" | "idle" | "maintenance" | "offline";
  last_latitude: number | null;
  last_longitude: number | null;
  last_seen: string | null;
}

export interface OperatorSettings {
  operator_id: string;
  display_name: string;
  theme: string;
  notifications_enabled: boolean;
  default_map_zoom: number;
}

export type AlertSeverity = "info" | "warning" | "critical";
export type AlertOperator = "lt" | "lte" | "gt" | "gte";

export interface AlertRule {
  id: string;
  name: string;
  metric: string;
  operator: AlertOperator;
  threshold: number;
  severity: AlertSeverity;
  enabled: boolean;
  created_by: string;
  created_at: string;
}

export interface Alert {
  id: string;
  rule_id: string;
  vehicle_id: string;
  metric_value: number;
  severity: AlertSeverity;
  acknowledged: boolean;
  fired_at: string;
}

export function fetchAlertRules(enabledOnly = false): Promise<AlertRule[]> {
  return request<AlertRule[]>(`/alerts/rules?enabled_only=${enabledOnly}`);
}

export function createAlertRule(
  body: Pick<AlertRule, "name" | "metric" | "operator" | "threshold" | "severity">,
): Promise<AlertRule> {
  return request<AlertRule>("/alerts/rules", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function toggleAlertRule(id: string, enabled: boolean): Promise<AlertRule> {
  return request<AlertRule>(`/alerts/rules/${id}/enabled?enabled=${enabled}`, {
    method: "PATCH",
  });
}

export function fetchAlerts(
  opts: { vehicleId?: string; unacknowledgedOnly?: boolean; limit?: number } = {},
): Promise<Alert[]> {
  const params = new URLSearchParams();
  if (opts.vehicleId) params.set("vehicle_id", opts.vehicleId);
  if (opts.unacknowledgedOnly) params.set("unacknowledged_only", "true");
  if (opts.limit) params.set("limit", String(opts.limit));
  const query = params.toString();
  return request<Alert[]>(`/alerts/${query ? `?${query}` : ""}`);
}

export function acknowledgeAlert(id: string): Promise<Alert> {
  return request<Alert>(`/alerts/${id}/acknowledge`, { method: "POST" });
}

export function fetchVehicles(): Promise<Vehicle[]> {
  return request<Vehicle[]>("/vehicles/");
}

export function fetchVehicle(id: string): Promise<Vehicle> {
  return request<Vehicle>(`/vehicles/${id}`);
}

export function fetchSettings(): Promise<OperatorSettings> {
  return request<OperatorSettings>("/settings/");
}

export function updateSettings(
  updates: Partial<Omit<OperatorSettings, "operator_id">>,
): Promise<OperatorSettings> {
  return request<OperatorSettings>("/settings/", {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
}
