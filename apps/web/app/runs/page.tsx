"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

type Run = {
  id: string;
  run_type: string;
  status: string;
  error?: string | null;
  created_at: string;
};

export default function RunsPage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<{ runs: Run[] }>("/api/runs")
      .then((data) => setRuns(data.runs))
      .catch(() => setError("Could not reach the agent API."));
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Runs</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <table className="w-full text-sm">
        <thead className="text-left text-neutral-500">
          <tr>
            <th className="py-1 pr-4">Created</th>
            <th className="py-1 pr-4">Type</th>
            <th className="py-1 pr-4">Status</th>
            <th className="py-1">Error</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.id} className="border-t border-neutral-800">
              <td className="py-1 pr-4 text-neutral-400">{new Date(run.created_at).toLocaleString()}</td>
              <td className="py-1 pr-4">{run.run_type}</td>
              <td className="py-1 pr-4">{run.status}</td>
              <td className="py-1 text-red-400">{run.error ?? ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {runs.length === 0 && !error && <p className="text-sm text-neutral-400">No runs yet.</p>}
    </div>
  );
}
