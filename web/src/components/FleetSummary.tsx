import React, { useEffect, useState } from "react";
import type { FleetSummary as FleetSummaryData } from "../api/client";
import { fetchFleetSummary } from "../api/client";

const REFRESH_INTERVAL_MS = 10_000;

interface Props {
  refreshKey?: number;
}

export function FleetSummary({ refreshKey = 0 }: Props) {
  const [summary, setSummary] = useState<FleetSummaryData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const data = await fetchFleetSummary();
        if (!cancelled) {
          setSummary(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unknown error");
        }
      }
    };
    load();
    const id = setInterval(load, REFRESH_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [refreshKey]);

  if (error) return <div className="error">Summary unavailable: {error}</div>;
  if (!summary) return <div className="loading">Loading summary…</div>;

  const fmt = (n: number | null, unit: string) =>
    n == null ? "—" : `${n.toFixed(1)} ${unit}`;

  return (
    <section className="fleet-summary" aria-label="Fleet summary">
      <div className="summary-card">
        <span className="summary-label">Total vehicles</span>
        <span className="summary-value" data-testid="summary-total">
          {summary.total_vehicles}
        </span>
      </div>
      <div className="summary-card">
        <span className="summary-label">Active</span>
        <span className="summary-value" data-testid="summary-active">
          {summary.by_status.active}
        </span>
      </div>
      <div className="summary-card">
        <span className="summary-label">Idle</span>
        <span className="summary-value">{summary.by_status.idle}</span>
      </div>
      <div className="summary-card">
        <span className="summary-label">Maintenance</span>
        <span className="summary-value">{summary.by_status.maintenance}</span>
      </div>
      <div className="summary-card">
        <span className="summary-label">Offline</span>
        <span className="summary-value">{summary.by_status.offline}</span>
      </div>
      <div className="summary-card">
        <span className="summary-label">Avg fuel</span>
        <span className="summary-value">{fmt(summary.average_fuel_level, "%")}</span>
      </div>
      <div className="summary-card">
        <span className="summary-label">Avg speed</span>
        <span className="summary-value">{fmt(summary.average_speed_kmh, "km/h")}</span>
      </div>
      <div className="summary-card summary-warning">
        <span className="summary-label">
          Stale (&gt;{summary.stale_threshold_minutes} min)
        </span>
        <span className="summary-value" data-testid="summary-stale">
          {summary.stale_vehicles}
        </span>
      </div>
    </section>
  );
}
