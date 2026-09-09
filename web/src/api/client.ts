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

export type VehicleStatus = Vehicle["status"];

export interface FleetSummary {
  total_vehicles: number;
  by_status: Record<VehicleStatus, number>;
  average_fuel_level: number | null;
  average_speed_kmh: number | null;
  stale_vehicles: number;
  stale_threshold_minutes: number;
}

export function fetchVehicles(status?: VehicleStatus): Promise<Vehicle[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request<Vehicle[]>(`/vehicles/${query}`);
}

export function fetchFleetSummary(): Promise<FleetSummary> {
  return request<FleetSummary>("/vehicles/summary");
}

export function updateVehicleStatus(
  id: string,
  status: VehicleStatus,
): Promise<Vehicle> {
  return request<Vehicle>(`/vehicles/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
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
