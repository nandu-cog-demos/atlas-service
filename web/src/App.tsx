import React, { useState } from "react";
import { FleetDashboard } from "./components/FleetDashboard";
import { TrustCenter } from "./components/TrustCenter";

type View = "dashboard" | "trust";

export function App() {
  const [view, setView] = useState<View>("dashboard");

  return (
    <div className="app">
      <nav className="app-nav">
        <span className="app-brand">Atlas</span>
        <button
          type="button"
          className={view === "dashboard" ? "active" : ""}
          onClick={() => setView("dashboard")}
        >
          Fleet Dashboard
        </button>
        <button
          type="button"
          className={view === "trust" ? "active" : ""}
          onClick={() => setView("trust")}
        >
          Trust Center
        </button>
      </nav>

      <main className="app-main">
        {view === "dashboard" ? <FleetDashboard /> : <TrustCenter />}
      </main>
    </div>
  );
}
