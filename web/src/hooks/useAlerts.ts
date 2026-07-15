import { useCallback, useEffect, useRef, useState } from "react";
import type { Alert } from "../api/client";
import { acknowledgeAlert, fetchAlerts } from "../api/client";

const POLL_INTERVAL_MS = 10_000;

export function useAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await fetchAlerts();
      setAlerts(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  const acknowledge = useCallback(async (id: string) => {
    const updated = await acknowledgeAlert(id);
    setAlerts((current) =>
      current.map((alert) => (alert.id === id ? updated : alert)),
    );
    return updated;
  }, []);

  useEffect(() => {
    load();
    intervalRef.current = setInterval(load, POLL_INTERVAL_MS);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [load]);

  const unacknowledgedCount = alerts.filter((alert) => !alert.acknowledged).length;

  return {
    alerts,
    unacknowledgedCount,
    loading,
    error,
    acknowledge,
    refresh: load,
  };
}
