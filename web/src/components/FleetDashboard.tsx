import React, { useState } from "react";
import type { Vehicle } from "../api/client";
import { useTelemetry } from "../hooks/useTelemetry";
import { AlertsPanel } from "./AlertsPanel";
import { VehicleDetail } from "./VehicleDetail";

export function FleetDashboard() {
  const { vehicles, loading, error } = useTelemetry();
  const [selected, setSelected] = useState<Vehicle | null>(null);

  if (loading) return <div className="loading">Loading fleet data…</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="dashboard">
      <header>
        <h1>Atlas Fleet Dashboard</h1>
      </header>

      <AlertsPanel />

      <section className="vehicle-list">
        <h2>Vehicles</h2>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {vehicles.map((v) => (
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
    </div>
  );
}
