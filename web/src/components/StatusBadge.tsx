import React from "react";

type VehicleStatus = "active" | "idle" | "maintenance" | "offline";

interface StatusBadgeProps {
  status: VehicleStatus;
}

const STATUS_COLORS: Record<VehicleStatus, string> = {
  active: "#22c55e",
  idle: "#eab308",
  maintenance: "#f97316",
  offline: "#94a3b8",
};

const STATUS_LABELS: Record<VehicleStatus, string> = {
  active: "Active",
  idle: "Idle",
  maintenance: "Maintenance",
  offline: "Offline",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const color = STATUS_COLORS[status];
  const label = STATUS_LABELS[status];

  return (
    <span
      className="status-badge"
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "6px",
        padding: "2px 10px",
        borderRadius: "12px",
        fontSize: "13px",
        fontWeight: 500,
        backgroundColor: `${color}1a`,
        color,
      }}
    >
      <span
        style={{
          width: "8px",
          height: "8px",
          borderRadius: "50%",
          backgroundColor: color,
        }}
      />
      {label}
    </span>
  );
}
