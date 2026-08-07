import React, { useCallback, useEffect, useState } from "react";
import type { Alert, AlertRule } from "../api/client";
import {
  acknowledgeAlert,
  fetchAlertRules,
  fetchAlerts,
  toggleAlertRule,
} from "../api/client";

const REFRESH_INTERVAL_MS = 15_000;

export function AlertsPanel() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [openOnly, setOpenOnly] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [nextRules, nextAlerts] = await Promise.all([
        fetchAlertRules(),
        fetchAlerts({ unacknowledgedOnly: openOnly }),
      ]);
      setRules(nextRules);
      setAlerts(nextAlerts);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load alerts");
    }
  }, [openOnly]);

  useEffect(() => {
    void load();
    const timer = setInterval(() => void load(), REFRESH_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [load]);

  const onToggleRule = async (rule: AlertRule) => {
    try {
      const updated = await toggleAlertRule(rule.id, !rule.enabled);
      setRules((current) => current.map((r) => (r.id === updated.id ? updated : r)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update rule");
    }
  };

  const onAcknowledge = async (alert: Alert) => {
    try {
      const updated = await acknowledgeAlert(alert.id);
      setAlerts((current) =>
        openOnly
          ? current.filter((a) => a.id !== updated.id)
          : current.map((a) => (a.id === updated.id ? updated : a)),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to acknowledge alert");
    }
  };

  const ruleName = (ruleId: string) => rules.find((r) => r.id === ruleId)?.name ?? ruleId;

  return (
    <section className="alerts-panel">
      <header className="alerts-header">
        <h2>Maintenance alerts</h2>
        <label>
          <input
            type="checkbox"
            checked={openOnly}
            onChange={(e) => setOpenOnly(e.target.checked)}
          />
          Unacknowledged only
        </label>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="alert-rules">
        <h3>Rules</h3>
        <ul>
          {rules.map((rule) => (
            <li key={rule.id} className={rule.enabled ? "rule enabled" : "rule disabled"}>
              <span className={`severity severity-${rule.severity}`}>{rule.severity}</span>
              <span className="rule-name">{rule.name}</span>
              <code>
                {rule.metric} {rule.operator} {rule.threshold}
              </code>
              <button onClick={() => void onToggleRule(rule)}>
                {rule.enabled ? "Disable" : "Enable"}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="alert-feed">
        <h3>Feed</h3>
        {alerts.length === 0 ? (
          <p className="empty">No alerts to show.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Vehicle</th>
                <th>Rule</th>
                <th>Value</th>
                <th>Severity</th>
                <th>Fired</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert) => (
                <tr key={alert.id} className={alert.acknowledged ? "acknowledged" : ""}>
                  <td>{alert.vehicle_id}</td>
                  <td>{ruleName(alert.rule_id)}</td>
                  <td>{alert.metric_value}</td>
                  <td>
                    <span className={`severity severity-${alert.severity}`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td>{new Date(alert.fired_at).toLocaleString()}</td>
                  <td>
                    {!alert.acknowledged && (
                      <button onClick={() => void onAcknowledge(alert)}>Ack</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
