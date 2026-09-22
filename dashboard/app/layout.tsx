import type { Metadata } from "next";
import { Space_Grotesk, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { Activity } from "lucide-react";
import { LocalTime } from "./LocalTime";

const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space" });
const plexMono = IBM_Plex_Mono({ weight: ['400', '500', '600', '700'], subsets: ["latin"], variable: "--font-plex" });

export const metadata: Metadata = {
  title: "Inventory Intel Dashboard",
  description: "Operations dashboard for Inventory Intel Agent",
};

export const revalidate = 0;

async function getSystemState() {
  const env = process.env;
  const apiUrl = env.API_URL || "http://127.0.0.1:8000/api";
  try {
    const res = await fetch(`${apiUrl}/runs`, { cache: 'no-store' });
    if (!res.ok) return null;
    const runs = await res.json();
    return runs.length > 0 ? runs[0] : null;
  } catch (e) {
    return null;
  }
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const latestRun = await getSystemState();
  const intervalMinutes = parseInt(process.env.AGENT_RUN_INTERVAL_MINUTES || "30", 10);
  
  let nextRunTimestamp: string | number = "Unknown";
  if (latestRun && latestRun.started_at) {
      const lastRunTime = new Date(latestRun.started_at).getTime();
      nextRunTimestamp = lastRunTime + intervalMinutes * 60000;
  }

  let statusColor = "text-neutral";
  if (latestRun?.status === "success") statusColor = "text-success";
  else if (latestRun?.status === "failed") statusColor = "text-critical";
  else if (latestRun?.status === "running") statusColor = "text-accent";

  return (
    <html lang="en" className={`${spaceGrotesk.variable} ${plexMono.variable}`}>
      <body className="bg-ink text-text-primary font-sans antialiased selection:bg-accent/30 min-h-screen flex flex-col">
        {/* Slim Header Strip */}
        <header className="bg-panel border-b border-hairline flex items-center justify-between px-4 py-2 text-xs sm:text-sm font-mono tracking-tight">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 font-semibold text-text-primary">
              <Activity className={`w-4 h-4 ${statusColor}`} />
              <span>INV_INTEL_AGENT</span>
            </div>
            
            <nav className="hidden sm:flex gap-4 text-text-secondary">
              <Link href="/" className="hover:text-text-primary transition-colors">WATCHLIST</Link>
              <Link href="/alerts" className="hover:text-text-primary transition-colors">ALERTS</Link>
              <Link href="/runs" className="hover:text-text-primary transition-colors">RUNS</Link>
            </nav>
          </div>

          <div className="flex items-center gap-4 sm:gap-6 text-text-secondary">
            {latestRun ? (
              <>
                <div className="flex gap-2 items-center">
                  <span className="opacity-50 hidden sm:inline">LATEST_RUN:</span>
                  <span className={statusColor}>
                    {latestRun.status.toUpperCase()}
                    {latestRun.finished_at && (
                      <> @ <LocalTime timestamp={latestRun.finished_at} format="time" /></>
                    )}
                  </span>
                </div>
                <div className="flex gap-2 items-center">
                  <span className="opacity-50 hidden sm:inline">NEXT_RUN:</span>
                  <span>~<LocalTime timestamp={nextRunTimestamp} format="time" /></span>
                </div>
              </>
            ) : (
              <div className="flex gap-2">
                <span className="opacity-50">SYSTEM_STATE:</span>
                <span className="text-neutral">NO_DATA</span>
              </div>
            )}
          </div>
        </header>

        <main className="flex-1 w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </body>
    </html>
  );
}
