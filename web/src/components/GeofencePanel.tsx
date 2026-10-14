import React, { useCallback, useEffect, useState } from "react";
import type { Geofence, GeofenceEventsPage } from "../api/client";
import {
  createGeofence,
  deleteGeofence,
  fetchGeofenceEvents,
  fetchGeofences,
} from "../api/client";

export function GeofencePanel() {
  const [fences, setFences] = useState<Geofence[]>([]);
  const [selected, setSelected] = useState<Geofence | null>(null);
  const [events, setEvents] = useState<GeofenceEventsPage | null>(null);
  const [page, setPage] = useState(1);
  const [name, setName] = useState("");
  const [radius, setRadius] = useState("500");
  const [busy, setBusy] = useState(false);

  const loadFences = useCallback(async () => {
    setFences(await fetchGeofences());
  }, []);

  useEffect(() => {
    void loadFences();
  }, [loadFences]);

  useEffect(() => {
    if (!selected) return;
    void fetchGeofenceEvents(selected.id, page).then(setEvents);
  }, [selected, page]);

  const onCreate = async () => {
    const radiusM = Number(radius);
    if (!name || Number.isNaN(radiusM) || radiusM <= 0) return;
    setBusy(true);
    try {
      const created = await createGeofence({
        name,
        center_latitude: 37.7749,
        center_longitude: -122.4194,
        radius_m: radiusM,
        kind: "inclusion",
      });
      setFences((current) => [created, ...current]);
      setName("");
    } finally {
      setBusy(false);
    }
  };

  const onDelete = async (id: string) => {
    await deleteGeofence(id);
    setFences((current) => current.filter((f) => f.id !== id));
    if (selected?.id === id) setSelected(null);
  };

  return (
    <section className="geofence-panel">
      <h2>Geofences</h2>

      <div className="geofence-form">
        <input
          placeholder="Zone name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="number"
          placeholder="Radius (m)"
          value={radius}
          onChange={(e) => setRadius(e.target.value)}
        />
        <button onClick={() => void onCreate()} disabled={busy}>
          Add zone
        </button>
      </div>

      <ul className="geofence-list">
        {fences.map((f) => (
          <li key={f.id} onClick={() => { setSelected(f); setPage(1); }}>
            <span className="geofence-name">{f.name}</span>
            <span className="geofence-meta">
              {f.kind} · {f.radius_m}m · {new Date(f.created_at).toLocaleString()}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                void onDelete(f.id);
              }}
              className="danger"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>

      {selected && (
        <div className="geofence-events">
          <h3>Breach events — {selected.name}</h3>
          <table>
            <tbody>
              {events?.events.map((e) => (
                <tr key={e.id}>
                  <td>{e.vehicle_id}</td>
                  <td>{e.event_type}</td>
                  <td>{Math.round(e.distance_m)} m</td>
                  <td>{e.occurred_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="pager">
            <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1}>
              Prev
            </button>
            <span>Page {page}</span>
            <button onClick={() => setPage((p) => p + 1)}>Next</button>
          </div>
        </div>
      )}
    </section>
  );
}
