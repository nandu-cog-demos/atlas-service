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

export interface Alert {
  id: string;
  zone_event_id: string;
  vehicle_id: string;
  zone_id: string;
  created_at: string;
  acknowledged: boolean;
  acknowledged_by: string | null;
  acknowledged_at: string | null;
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

export function fetchAlerts(): Promise<Alert[]> {
  return request<Alert[]>("/alerts/");
}

export function acknowledgeAlert(id: string): Promise<Alert> {
  return request<Alert>(`/alerts/${id}/acknowledge`, {
    method: "POST",
  });
}
