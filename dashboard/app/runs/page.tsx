import Link from "next/link";

export const revalidate = 0;

async function getRuns() {
  const res = await fetch("http://127.0.0.1:8000/api/runs", { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch runs");
  return res.json();
}

export default async function RunsPage() {
  const runs = await getRuns();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Agent Runs</h1>
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {runs.map((run: any) => (
            <li key={run.id}>
              <Link href={`/runs/${run.id}`} className="block hover:bg-gray-50">
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-blue-600 truncate">Run #{run.id}</p>
                    <div className="ml-2 flex-shrink-0 flex">
                      <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${run.status === 'success' ? 'bg-green-100 text-green-800' : 
                          run.status === 'failed' ? 'bg-red-100 text-red-800' : 
                          run.status === 'running' ? 'bg-blue-100 text-blue-800' :
                          'bg-yellow-100 text-yellow-800'}`}>
                        {run.status}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2 sm:flex sm:justify-between">
                    <div className="sm:flex">
                      <p className="flex items-center text-sm text-gray-500">
                        Started: {new Date(run.started_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                      <p>Products checked: {run.products_checked || 0}</p>
                    </div>
                  </div>
                  {run.summary && (
                    <div className="mt-2 text-sm text-gray-700">
                      <p className="line-clamp-2">{run.summary}</p>
                    </div>
                  )}
                  {run.error && (
                    <div className="mt-2 text-sm text-red-600 font-semibold">
                      Error: {run.error}
                    </div>
                  )}
                </div>
              </Link>
            </li>
          ))}
          {runs.length === 0 && (
            <li className="px-4 py-8 text-center text-gray-500">No agent runs recorded yet.</li>
          )}
        </ul>
      </div>
    </div>
  );
}
