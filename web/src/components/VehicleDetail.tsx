import React from "react";
import type { Vehicle } from "../api/client";
import { StatusBadge } from "./StatusBadge";

interface Props {
  vehicle: Vehicle;
}

export function VehicleDetail({ vehicle }: Props) {
  return (
    <section className="vehicle-detail">
      <h2>{vehicle.name}</h2>
      <dl>
        <dt>ID</dt>
        <dd>{vehicle.id}</dd>
        <dt>Status</dt>
        <dd>
          <StatusBadge status={vehicle.status} />
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
    </section>
  );
}
