export const revalidate = 0;

async function getAlerts() {
  const res = await fetch("http://127.0.0.1:8000/api/alerts", { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch alerts");
  return res.json();
}

async function getProducts() {
  const res = await fetch("http://127.0.0.1:8000/api/products", { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch products");
  const products = await res.json();
  const map: Record<number, string> = {};
  products.forEach((p: any) => { map[p.id] = p.name; });
  return map;
}

export default async function AlertsPage() {
  const [alerts, productMap] = await Promise.all([getAlerts(), getProducts()]);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Recent Alerts</h1>
      <div className="flex flex-col">
        <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {alerts.map((alert: any) => (
                    <tr key={alert.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(alert.timestamp).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                          ${alert.alert_type === 'price_drop' ? 'bg-green-100 text-green-800' : 
                            alert.alert_type === 'stockout' ? 'bg-red-100 text-red-800' : 
                            'bg-blue-100 text-blue-800'}`}>
                          {alert.alert_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {productMap[alert.product_id] || `Product ${alert.product_id}`}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {alert.message.split('\n')[2]} {alert.message.split('\n')[3]}
                      </td>
                    </tr>
                  ))}
                  {alerts.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">No alerts recorded yet.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
