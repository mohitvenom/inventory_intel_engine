import Link from "next/link";
import { LocalTime } from "../LocalTime";

export const revalidate = 0;

async function getRuns() {
  const env = process.env;
  const apiUrl = env.API_URL || "http://127.0.0.1:8000/api";
  try {
    const res = await fetch(`${apiUrl}/runs`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
  } catch (e) {
    return [];
  }
}

export default async function RunsPage() {
  const runs = await getRuns();

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold uppercase tracking-wider text-text-primary">Agent Runs</h1>
      
      <div className="border border-hairline bg-panel rounded-sm overflow-hidden">
        <div className="hidden sm:grid grid-cols-12 gap-4 p-4 border-b border-hairline bg-ink/50 text-xs font-mono text-text-secondary uppercase tracking-wider">
          <div className="col-span-2">Run ID</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-3">Timestamp</div>
          <div className="col-span-5">Summary / Error</div>
        </div>

        <div className="divide-y divide-hairline">
          {runs.map((run: any) => {
            const isSuccess = run.status === 'success';
            const isFailed = run.status === 'failed';
            const isRunning = run.status === 'running';
            
            let statusColor = "text-neutral";
            if (isSuccess) statusColor = "text-success";
            else if (isFailed) statusColor = "text-critical";
            else if (isRunning) statusColor = "text-accent";
            
            return (
              <Link key={run.id} href={`/runs/${run.id}`} className="block hover:bg-ink/30 transition-colors">
                <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 p-4 items-center text-sm">
                  <div className="col-span-1 sm:col-span-2 font-mono text-text-primary">
                    #{run.id}
                  </div>
                  
                  <div className="col-span-1 sm:col-span-2 font-mono text-xs uppercase">
                    <span className={statusColor}>
                      {run.status}
                    </span>
                  </div>
                  
                  <div className="col-span-1 sm:col-span-3 font-mono text-text-secondary text-xs">
                    <LocalTime timestamp={run.started_at} format="datetime" />
                  </div>
                  
                  <div className="col-span-1 sm:col-span-5 font-mono text-xs">
                    {run.error ? (
                      <span className="text-critical truncate block" title={run.error}>ERR: {run.error}</span>
                    ) : (
                      <span className="text-text-secondary truncate block" title={run.summary}>
                        {run.summary || `Targets checked: ${run.products_checked || 0}`}
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            );
          })}
          
          {runs.length === 0 && (
            <div className="p-8 text-center text-text-secondary font-mono text-sm">
              NO_RUNS_RECORDED
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
