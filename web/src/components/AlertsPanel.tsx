import React, { useState } from "react";
import { useAlerts } from "../hooks/useAlerts";

export function AlertsPanel() {
  const { alerts, unacknowledgedCount, loading, error, acknowledge } = useAlerts();
  const [acknowledgingId, setAcknowledgingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const handleAcknowledge = async (id: string) => {
    setAcknowledgingId(id);
    setActionError(null);
    try {
      await acknowledge(id);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setAcknowledgingId(null);
    }
  };

  return (
    <section className="alerts-panel">
      <header>
        <h2>
          Alerts{" "}
          <span className="alert-count" aria-label={`${unacknowledgedCount} unacknowledged alerts`}>
            {unacknowledgedCount}
          </span>
        </h2>
      </header>

      {error && <div className="error">Error: {error}</div>}
      {actionError && <div className="error">Error: {actionError}</div>}
      {loading && <div className="loading">Loading alerts…</div>}
      {!loading && alerts.length === 0 && <div className="empty">No alerts</div>}

      {!loading && alerts.length > 0 && (
        <ul className="alert-list">
          {alerts.map((alert) => (
            <li
              key={alert.id}
              className={`alert-item${alert.acknowledged ? " acknowledged" : ""}`}
            >
              <div className="alert-details">
                <strong>Vehicle {alert.vehicle_id}</strong>
                <span>Zone {alert.zone_id}</span>
                <time dateTime={alert.created_at}>
                  {new Date(alert.created_at).toLocaleString()}
                </time>
                <span className="alert-state">
                  {alert.acknowledged ? "Acknowledged" : "Unacknowledged"}
                </span>
              </div>
              {!alert.acknowledged && (
                <button
                  type="button"
                  onClick={() => handleAcknowledge(alert.id)}
                  disabled={acknowledgingId === alert.id}
                >
                  Acknowledge
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
