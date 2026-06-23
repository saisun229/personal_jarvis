"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";

type Brief = {
  brief_date?: string;
  summary?: string;
  payload?: {
    important_emails?: string[];
    needs_reply?: string[];
    top_3_priorities?: string[];
    suggested_focus_blocks?: string[];
    risks_or_warnings?: string[];
  };
};

export default function DashboardPage() {
  const [brief, setBrief] = useState<Brief | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadBrief = async () => {
    try {
      const data = await apiGet<Brief>("/api/briefs/latest");
      setBrief(data);
    } catch {
      setError("Could not reach the agent API.");
    }
  };

  useEffect(() => {
    loadBrief();
  }, []);

  const runGoodMorning = async () => {
    setLoading(true);
    setError(null);
    try {
      await apiPost("/api/run/good-morning");
      await loadBrief();
    } catch {
      setError("Run failed — check the agent API logs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Dashboard</h1>
        <button
          onClick={runGoodMorning}
          disabled={loading}
          className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500 disabled:opacity-50"
        >
          {loading ? "Running..." : "Run good morning"}
        </button>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {!brief?.summary && !error && (
        <p className="text-sm text-neutral-400">No brief yet — click &quot;Run good morning&quot;.</p>
      )}

      {brief?.summary && (
        <div className="space-y-4 rounded border border-neutral-800 p-4">
          <div>
            <p className="text-xs uppercase text-neutral-500">{brief.brief_date}</p>
            <p className="mt-1">{brief.summary}</p>
          </div>

          <Section title="Top 3 priorities" items={brief.payload?.top_3_priorities} />
          <Section title="Needs reply" items={brief.payload?.needs_reply} />
          <Section title="Important emails" items={brief.payload?.important_emails} />
          <Section title="Suggested focus blocks" items={brief.payload?.suggested_focus_blocks} />
          <Section title="Risks / warnings" items={brief.payload?.risks_or_warnings} />
        </div>
      )}
    </div>
  );
}

function Section({ title, items }: { title: string; items?: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <p className="text-xs uppercase text-neutral-500">{title}</p>
      <ul className="mt-1 list-disc pl-5 text-sm space-y-1">
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
