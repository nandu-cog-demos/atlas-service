import React, { useEffect, useState } from "react";
import type { TrustCenter as TrustCenterData } from "../api/client";
import { fetchTrustCenter } from "../api/client";

function statusLabel(status: string): string {
  return status.replace(/_/g, " ");
}

export function TrustCenter() {
  const [data, setData] = useState<TrustCenterData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTrustCenter()
      .then(setData)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Unknown error"),
      );
  }, []);

  if (error) return <div className="error">Error: {error}</div>;
  if (!data) return <div className="loading">Loading Trust Center…</div>;

  const status = data.service_status;

  return (
    <div className="trust-center">
      <header className="trust-hero">
        <h1>Atlas Trust Center</h1>
        <p className="trust-overview">{data.overview}</p>
        <div className="trust-status">
          <span className={`status-dot status-${status.state}`} />
          <span className="trust-status-text">
            {status.state === "operational"
              ? "All systems operational"
              : status.state}
          </span>
          <span className="trust-uptime">
            {status.uptime_90d}% uptime (90d)
          </span>
          <a href={status.status_page_url} target="_blank" rel="noreferrer">
            Status page →
          </a>
        </div>
        <p className="trust-updated">Last updated {data.last_updated}</p>
      </header>

      <section className="trust-section">
        <h2>Compliance &amp; Certifications</h2>
        <div className="cert-grid">
          {data.certifications.map((c) => (
            <div key={c.name} className="cert-card">
              <div className="cert-head">
                <h3>{c.name}</h3>
                <span className={`cert-badge cert-${c.status}`}>
                  {statusLabel(c.status)}
                </span>
              </div>
              <p>{c.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="trust-section">
        <h2>Security Practices</h2>
        <div className="practice-grid">
          {data.security_practices.map((p) => (
            <div key={p.category} className="practice-card">
              <h3>{p.category}</h3>
              <ul>
                {p.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="trust-section">
        <h2>Subprocessors</h2>
        <table className="subprocessor-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Purpose</th>
              <th>Location</th>
            </tr>
          </thead>
          <tbody>
            {data.subprocessors.map((s) => (
              <tr key={s.name}>
                <td>{s.name}</td>
                <td>{s.purpose}</td>
                <td>{s.location}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="trust-section">
        <h2>Resources</h2>
        <ul className="resource-list">
          {data.resources.map((r) => (
            <li key={r.label}>
              <a href={r.url} target="_blank" rel="noreferrer">
                {r.label} →
              </a>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
