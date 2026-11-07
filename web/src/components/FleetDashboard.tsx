import React, { useState } from "react";
import { useTelemetry } from "../hooks/useTelemetry";
import { FuelBadge } from "./FuelBadge";
import { VehicleDetail } from "./VehicleDetail";

export function FleetDashboard() {
  const { vehicles, loading, error } = useTelemetry();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [lowFuelOnly, setLowFuelOnly] = useState(false);

  if (loading) return <div className="loading">Loading fleet data…</div>;
  if (error) return <div className="error">Error: {error}</div>;

  const selected = vehicles.find((v) => v.id === selectedId) ?? null;
  const lowFuelCount = vehicles.filter((v) => v.low_fuel).length;
  const visible = lowFuelOnly ? vehicles.filter((v) => v.low_fuel) : vehicles;

  return (
    <div className="dashboard">
      <header>
        <h1>Atlas Fleet Dashboard</h1>
      </header>

      <section className="vehicle-list">
        <h2>Vehicles</h2>
        <div className="vehicle-filters">
          <label>
            <input
              type="checkbox"
              checked={lowFuelOnly}
              onChange={(e) => setLowFuelOnly(e.target.checked)}
            />
            Low fuel only
          </label>
          <span className="low-fuel-count">{lowFuelCount} low fuel</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th>Fuel</th>
              <th>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((v) => (
              <tr
                key={v.id}
                onClick={() => setSelectedId(v.id)}
                className={[
                  selectedId === v.id ? "selected" : "",
                  v.low_fuel ? "low-fuel-row" : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
              >
                <td>{v.name}</td>
                <td>
                  <span className={`status-badge status-${v.status}`}>
                    {v.status}
                  </span>
                </td>
                <td>
                  <FuelBadge fuelLevel={v.fuel_level} lowFuel={v.low_fuel} />
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
