import React, { useEffect, useState } from "react";
import type { OperatorSettings as Settings } from "../api/client";
import { fetchSettings, updateSettings } from "../api/client";

export function OperatorSettings() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSettings()
      .then(setSettings)
      .catch(console.error);
  }, []);

  if (!settings) return <div>Loading settings…</div>;

  const handleThemeChange = async (theme: string) => {
    setSaving(true);
    try {
      const updated = await updateSettings({ theme });
      setSettings(updated);
    } finally {
      setSaving(false);
    }
  };

  const currentTheme = settings.theme ?? "system";

  return (
    <section className="operator-settings">
      <h2>Operator Settings</h2>
      <dl>
        <dt>Display Name</dt>
        <dd>{settings.display_name}</dd>
        <dt>Theme</dt>
        <dd>
          <select
            value={currentTheme}
            onChange={(e) => handleThemeChange(e.target.value)}
            disabled={saving}
          >
            <option value="system">System</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </dd>
        <dt>Notifications</dt>
        <dd>{settings.notifications_enabled ? "Enabled" : "Disabled"}</dd>
        <dt>Default Map Zoom</dt>
        <dd>{settings.default_map_zoom}</dd>
      </dl>
    </section>
  );
}
