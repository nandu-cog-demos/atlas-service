import React, { useState } from "react";
import type { Vehicle, VehicleStatus } from "../api/client";
import { updateVehicleStatus } from "../api/client";

const STATUSES: VehicleStatus[] = ["active", "idle", "maintenance", "offline"];

interface Props {
  vehicle: Vehicle;
  onStatusChanged?: (vehicle: Vehicle) => void;
}

export function VehicleDetail({ vehicle, onStatusChanged }: Props) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStatusChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const next = e.target.value as VehicleStatus;
    if (next === vehicle.status) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await updateVehicleStatus(vehicle.id, next);
      onStatusChanged?.(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="vehicle-detail">
      <h2>{vehicle.name}</h2>
      <dl>
        <dt>ID</dt>
        <dd>{vehicle.id}</dd>
        <dt>Status</dt>
        <dd>
          <span className={`status-badge status-${vehicle.status}`}>
            {vehicle.status}
          </span>
        </dd>
        <dt>Position</dt>
        <dd>
          {vehicle.last_latitude != null && vehicle.last_longitude != null
            ? `${vehicle.last_latitude.toFixed(4)}, ${vehicle.last_longitude.toFixed(4)}`
            : "Unknown"}
        </dd>
        <dt>Last Seen</dt>
        <dd>{vehicle.last_seen ?? "Never"}</dd>
      </dl>
      {onStatusChanged && (
        <div className="status-control">
          <label>
            Set status{" "}
            <select
              aria-label="Set vehicle status"
              value={vehicle.status}
              disabled={saving}
              onChange={handleStatusChange}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          {saving && <span className="loading">Saving…</span>}
          {error && <span className="error">Failed to update: {error}</span>}
        </div>
      )}
    </section>
  );
}
