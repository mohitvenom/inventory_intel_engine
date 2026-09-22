import Link from "next/link";

export const revalidate = 0;

async function getRun(id: string) {
  const apiUrl = process.env.API_URL || "http://127.0.0.1:8000/api";
  const res = await fetch(`${apiUrl}/runs/${id}`, { cache: 'no-store' });
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error("Failed to fetch run");
  }
  return res.json();
}

export default async function RunDetailPage({ params }: { params: { id: string } }) {
  const run = await getRun(params.id);

  if (!run) return <div>Run not found</div>;

  return (
    <div>
      <div className="mb-4">
        <Link href="/runs" className="text-blue-600 hover:underline">
          &larr; Back to Agent Runs
        </Link>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Agent Run #{run.id}</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Started: {new Date(run.started_at).toLocaleString()} | Status: {run.status}
          </p>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          <h4 className="text-md font-medium text-gray-900 mb-2">LLM Summary</h4>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">
            {run.trace?.summary || "No summary available."}
          </p>
        </div>
      </div>

      <div className="bg-white shadow sm:rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Full Execution Trace</h3>
        </div>
        <div className="p-4 bg-gray-900 text-green-400 font-mono text-sm overflow-x-auto">
          <pre>{JSON.stringify(run.trace?.results, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
}
