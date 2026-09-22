import Link from "next/link";
import { LocalTime } from "../LocalTime";

export const revalidate = 0;

async function getAlerts() {
  const env = process.env;
  const apiUrl = env.API_URL || "http://127.0.0.1:8000/api";
  try {
    const res = await fetch(`${apiUrl}/alerts`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
  } catch (e) {
    return [];
  }
}

async function getProducts() {
  const env = process.env;
  const apiUrl = env.API_URL || "http://127.0.0.1:8000/api";
  try {
    const res = await fetch(`${apiUrl}/products`, { cache: 'no-store' });
    if (!res.ok) return {};
    const products = await res.json();
    const map: Record<number, string> = {};
    products.forEach((p: any) => { map[p.id] = p.name; });
    return map;
  } catch (e) {
    return {};
  }
}

export default async function AlertsPage() {
  const [alerts, productMap] = await Promise.all([getAlerts(), getProducts()]);

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold uppercase tracking-wider text-text-primary">Alerts Log</h1>
      
      <div className="border border-hairline bg-panel rounded-sm overflow-hidden">
        <div className="hidden sm:grid grid-cols-12 gap-4 p-4 border-b border-hairline bg-ink/50 text-xs font-mono text-text-secondary uppercase tracking-wider">
          <div className="col-span-3">Timestamp</div>
          <div className="col-span-2">Type</div>
          <div className="col-span-3">Product</div>
          <div className="col-span-4">Message Segment</div>
        </div>

        <div className="divide-y divide-hairline">
          {alerts.map((alert: any) => {
            const isPriceDrop = alert.alert_type === 'price_drop';
            const isStockout = alert.alert_type === 'stockout';
            
            return (
              <div key={alert.id} className="grid grid-cols-1 sm:grid-cols-12 gap-4 p-4 items-center text-sm hover:bg-ink/30 transition-colors">
                <div className="col-span-1 sm:col-span-3 font-mono text-text-secondary text-xs">
                  <LocalTime timestamp={alert.timestamp} format="datetime" />
                </div>
                
                <div className="col-span-1 sm:col-span-2 font-mono text-xs uppercase">
                  <span className={isPriceDrop ? 'text-success' : isStockout ? 'text-critical' : 'text-accent'}>
                    {alert.alert_type}
                  </span>
                </div>
                
                <div className="col-span-1 sm:col-span-3 font-medium text-text-primary truncate">
                  {productMap[alert.product_id] || `Product ${alert.product_id}`}
                </div>
                
                <div className="col-span-1 sm:col-span-4 font-mono text-xs text-text-secondary truncate" title={alert.message}>
                  {alert.message?.split('\\n')?.slice(2, 4)?.join(' ') || alert.message}
                </div>
              </div>
            );
          })}
          
          {alerts.length === 0 && (
            <div className="p-8 text-center text-text-secondary font-mono text-sm">
              NO_ALERTS_RECORDED
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
