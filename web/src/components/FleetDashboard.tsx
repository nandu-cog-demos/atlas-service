import React, { useMemo, useState } from "react";
import type { Vehicle, VehicleStatus } from "../api/client";
import { useTelemetry } from "../hooks/useTelemetry";
import { FleetSummary } from "./FleetSummary";
import { VehicleDetail } from "./VehicleDetail";

const STATUS_OPTIONS: Array<VehicleStatus | "all"> = [
  "all",
  "active",
  "idle",
  "maintenance",
  "offline",
];

export function FleetDashboard() {
  const { vehicles, loading, error, refresh } = useTelemetry();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<VehicleStatus | "all">("all");
  const [search, setSearch] = useState("");
  const [summaryVersion, setSummaryVersion] = useState(0);

  const visible = useMemo(() => {
    const q = search.trim().toLowerCase();
    return vehicles.filter(
      (v) =>
        (statusFilter === "all" || v.status === statusFilter) &&
        (q === "" || v.name.toLowerCase().includes(q) || v.id.toLowerCase().includes(q)),
    );
  }, [vehicles, statusFilter, search]);

  const selected: Vehicle | null =
    vehicles.find((v) => v.id === selectedId) ?? null;

  const handleVehicleChanged = () => {
    refresh();
    setSummaryVersion((n) => n + 1);
  };

  if (loading) return <div className="loading">Loading fleet data…</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="dashboard">
      <header>
        <h1>Atlas Fleet Dashboard</h1>
      </header>

      <FleetSummary refreshKey={summaryVersion} />

      <section className="vehicle-list">
        <h2>Vehicles</h2>
        <div className="vehicle-filters">
          <label>
            Status{" "}
            <select
              aria-label="Filter by status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as VehicleStatus | "all")}
            >
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {s === "all" ? "All" : s}
                </option>
              ))}
            </select>
          </label>
          <input
            type="search"
            aria-label="Search vehicles"
            placeholder="Search by name or ID"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <span className="vehicle-count">
            {visible.length} of {vehicles.length}
          </span>
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
            {visible.length === 0 ? (
              <tr>
                <td colSpan={3} className="empty">
                  No vehicles match the current filters.
                </td>
              </tr>
            ) : (
              visible.map((v) => (
                <tr
                  key={v.id}
                  onClick={() => setSelectedId(v.id)}
                  className={selectedId === v.id ? "selected" : ""}
                >
                  <td>{v.name}</td>
                  <td>
                    <span className={`status-badge status-${v.status}`}>
                      {v.status}
                    </span>
                  </td>
                  <td>{v.last_seen ?? "—"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>

      {selected && (
        <VehicleDetail vehicle={selected} onStatusChanged={handleVehicleChanged} />
      )}
    </div>
  );
}
