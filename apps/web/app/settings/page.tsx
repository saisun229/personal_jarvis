"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

type Status = {
  openai_configured: boolean;
  supabase_configured: boolean;
  google_connected: boolean;
  google_account_email: string | null;
  mcp_server: {
    reachable: boolean;
    google_credentials_configured: boolean;
    telegram_configured: boolean;
  };
};

export default function SettingsPage() {
  const [status, setStatus] = useState<Status | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<Status>("/api/status")
      .then(setStatus)
      .catch(() => setError("Could not reach the agent API."));
  }, []);

  if (error) return <p className="text-sm text-red-400">{error}</p>;
  if (!status) return <p className="text-sm text-neutral-400">Loading...</p>;

  const rows = [
    { label: "OpenAI API key", ok: status.openai_configured },
    { label: "Supabase", ok: status.supabase_configured },
    { label: "MCP server reachable", ok: status.mcp_server.reachable },
    { label: "Google OAuth client configured", ok: status.mcp_server.google_credentials_configured },
    {
      label: "Google account connected",
      ok: status.google_connected,
      detail: status.google_account_email ?? undefined,
    },
    { label: "Telegram", ok: status.mcp_server.telegram_configured, detail: status.mcp_server.telegram_configured ? undefined : "deferred" },
  ];

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Settings</h1>
      <ul className="divide-y divide-neutral-800 rounded border border-neutral-800">
        {rows.map((row) => (
          <li key={row.label} className="flex items-center justify-between px-4 py-3 text-sm">
            <span>{row.label}</span>
            <span className="flex items-center gap-2">
              {row.detail && <span className="text-neutral-500">{row.detail}</span>}
              <span className={row.ok ? "text-green-400" : "text-neutral-500"}>{row.ok ? "Connected" : "Not configured"}</span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
