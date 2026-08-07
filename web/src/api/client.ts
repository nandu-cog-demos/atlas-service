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

export interface Geofence {
  id: string;
  name: string;
  center_latitude: number;
  center_longitude: number;
  radius_m: number;
  kind: string;
  operator_id: string;
  created_at: string;
}

export interface GeofenceEvent {
  id: string;
  geofence_id: string;
  vehicle_id: string;
  event_type: string;
  latitude: number;
  longitude: number;
  distance_m: number;
  occurred_at: string;
}

export interface GeofenceEventsPage {
  geofence_id: string;
  page: number;
  events: GeofenceEvent[];
}

export interface FleetSummary {
  total: number;
  by_status: Record<string, number>;
}

export function fetchVehicles(status?: string): Promise<Vehicle[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request<Vehicle[]>(`/vehicles/${query}`);
}

export function fetchFleetSummary(): Promise<FleetSummary> {
  return request<FleetSummary>("/vehicles/summary");
}

export function fetchGeofences(): Promise<Geofence[]> {
  return request<Geofence[]>("/geofences/");
}

export function createGeofence(
  body: Omit<Geofence, "id" | "operator_id" | "created_at">,
): Promise<Geofence> {
  return request<Geofence>("/geofences/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function deleteGeofence(id: string): Promise<{ status: string; id: string }> {
  return request(`/geofences/${id}`, { method: "DELETE" });
}

export function fetchGeofenceEvents(id: string, page = 1): Promise<GeofenceEventsPage> {
  return request<GeofenceEventsPage>(`/geofences/${id}/events?page=${page}`);
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
