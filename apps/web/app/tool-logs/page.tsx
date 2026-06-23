"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

type ToolCall = {
  id: string;
  tool_name: string;
  risk_level: string;
  status: string;
  error?: string | null;
  created_at: string;
};

export default function ToolLogsPage() {
  const [calls, setCalls] = useState<ToolCall[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<{ tool_calls: ToolCall[] }>("/api/tool-calls")
      .then((data) => setCalls(data.tool_calls))
      .catch(() => setError("Could not reach the agent API."));
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Tool Logs</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <table className="w-full text-sm">
        <thead className="text-left text-neutral-500">
          <tr>
            <th className="py-1 pr-4">Time</th>
            <th className="py-1 pr-4">Tool</th>
            <th className="py-1 pr-4">Risk</th>
            <th className="py-1 pr-4">Status</th>
            <th className="py-1">Error</th>
          </tr>
        </thead>
        <tbody>
          {calls.map((call) => (
            <tr key={call.id} className="border-t border-neutral-800">
              <td className="py-1 pr-4 text-neutral-400">{new Date(call.created_at).toLocaleString()}</td>
              <td className="py-1 pr-4">{call.tool_name}</td>
              <td className="py-1 pr-4">{call.risk_level}</td>
              <td className="py-1 pr-4">{call.status}</td>
              <td className="py-1 text-red-400">{call.error ?? ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {calls.length === 0 && !error && <p className="text-sm text-neutral-400">No tool calls yet.</p>}
    </div>
  );
}
