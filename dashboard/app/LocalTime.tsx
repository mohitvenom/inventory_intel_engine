"use client";

import { useEffect, useState } from "react";

export function LocalTime({ timestamp, format = "datetime" }: { timestamp: string | number, format?: "datetime" | "time" | "date" }) {
  const [localTime, setLocalTime] = useState<string>("");

  useEffect(() => {
    const d = new Date(timestamp);
    if (format === "time") {
      setLocalTime(d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    } else if (format === "date") {
      setLocalTime(d.toLocaleDateString());
    } else {
      setLocalTime(d.toLocaleString());
    }
  }, [timestamp, format]);

  // Prevent hydration mismatch by rendering empty or a placeholder on the server
  // or rendering the raw string, but it's safer to just return nothing or the server-rendered UTC until mounted.
  return <span suppressHydrationWarning>{localTime || "---"}</span>;
}
