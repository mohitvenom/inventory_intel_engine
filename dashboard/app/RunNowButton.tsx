"use client";

import { useState } from "react";
import { Play } from "lucide-react";
import { useRouter } from "next/navigation";

export function RunNowButton() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "running" | "error">("idle");
  const router = useRouter();

  async function triggerRun() {
    setLoading(true);
    setStatus("idle");
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
      const res = await fetch(`${apiUrl}/runs/trigger`, { method: "POST" });
      if (res.ok) {
        setStatus("running");
        router.refresh();
        setTimeout(() => setStatus("idle"), 5000);
      } else {
        setStatus("error");
        setTimeout(() => setStatus("idle"), 5000);
      }
    } catch (e) {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 5000);
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={triggerRun}
      disabled={loading || status === "running"}
      className="flex items-center gap-1.5 px-2 py-0.5 bg-panel border border-hairline hover:border-accent/50 hover:bg-surface text-text-secondary hover:text-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed uppercase text-xs font-mono rounded-sm"
      title={status === "error" ? "Run failed or overlapped" : "Trigger a manual run"}
    >
      <Play className="w-3 h-3" />
      {loading ? "..." : status === "running" ? "STARTED" : status === "error" ? "ERROR" : "RUN NOW"}
    </button>
  );
}
