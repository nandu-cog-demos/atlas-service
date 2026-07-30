import React, { useState } from "react";
import type { Vehicle } from "../api/client";
import { useTelemetry } from "../hooks/useTelemetry";
import { GeofencePanel } from "./GeofencePanel";
import { VehicleDetail } from "./VehicleDetail";

const STATUS_FILTERS = ["all", "active", "idle", "maintenance", "offline"] as const;

export function FleetDashboard() {
  const { vehicles, loading, error } = useTelemetry();
  const [selected, setSelected] = useState<Vehicle | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  if (loading) return <div className="loading">Loading fleet data…</div>;
  if (error) return <div className="error">Error: {error}</div>;

  const visible =
    statusFilter === "all"
      ? vehicles
      : vehicles.filter((v) => v.status === statusFilter);

  return (
    <div className="dashboard">
      <header>
        <h1>Atlas Fleet Dashboard</h1>
      </header>

      <section className="vehicle-list">
        <div className="vehicle-list-header">
          <h2>Vehicles</h2>
          <label>
            Status:{" "}
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              {STATUS_FILTERS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
        </div>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((v) => (
              <tr
                key={v.id}
                onClick={() => setSelected(v)}
                className={selected?.id === v.id ? "selected" : ""}
              >
                <td>{v.name}</td>
                <td>
                  <span className={`status-badge status-${v.status}`}>
                    {v.status}
                  </span>
                </td>
                <td>{v.last_seen ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {selected && <VehicleDetail vehicle={selected} />}

      <GeofencePanel />
    </div>
  );
}
