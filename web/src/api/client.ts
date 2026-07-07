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

export interface Certification {
  name: string;
  status: string;
  description: string;
}

export interface SecurityPractice {
  category: string;
  items: string[];
}

export interface Subprocessor {
  name: string;
  purpose: string;
  location: string;
}

export interface ServiceStatus {
  state: string;
  uptime_90d: number;
  status_page_url: string;
}

export interface TrustResource {
  label: string;
  url: string;
}

export interface TrustCenter {
  overview: string;
  last_updated: string;
  certifications: Certification[];
  security_practices: SecurityPractice[];
  subprocessors: Subprocessor[];
  service_status: ServiceStatus;
  resources: TrustResource[];
}

export function fetchVehicles(): Promise<Vehicle[]> {
  return request<Vehicle[]>("/vehicles/");
}

export function fetchTrustCenter(): Promise<TrustCenter> {
  return request<TrustCenter>("/trust/");
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
