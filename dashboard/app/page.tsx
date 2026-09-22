import Link from "next/link";
import { ExternalLink } from "lucide-react";

export const revalidate = 0;

async function getProducts() {
  const env = process.env;
  const apiUrl = env.API_URL || "http://127.0.0.1:8000/api";
  try {
    const res = await fetch(`${apiUrl}/products`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
  } catch (e) {
    return [];
  }
}

export default async function WatchlistPage() {
  const products = await getProducts();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold uppercase tracking-wider text-text-primary">Watchlist</h1>
      </div>
      
      <div className="border border-hairline bg-panel rounded-sm overflow-hidden">
        {/* Table Header */}
        <div className="hidden sm:grid grid-cols-12 gap-4 p-4 border-b border-hairline bg-ink/50 text-xs font-mono text-text-secondary uppercase tracking-wider">
          <div className="col-span-4">Product / Source</div>
          <div className="col-span-2">Price</div>
          <div className="col-span-2">Stock</div>
          <div className="col-span-4 text-right">Triggers</div>
        </div>

        {/* Table Body */}
        <div className="divide-y divide-hairline">
          {products.map((product: any) => {
            const hasPrice = product.latest_price !== null;
            const hasStockData = product.latest_stock !== null;
            const inStock = product.latest_stock === true;
            
            return (
              <Link key={product.id} href={`/products/${product.id}`} className="block hover:bg-ink/30 transition-colors">
                <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 p-4 items-center text-sm">
                  
                  {/* Product Info */}
                  <div className="col-span-1 sm:col-span-4 space-y-1">
                    <div className="font-medium text-text-primary truncate" title={product.name}>
                      {product.name}
                    </div>
                    <div className="text-xs font-mono text-text-secondary uppercase">
                      {product.source} {product.region && `[${product.region}]`}
                    </div>
                  </div>

                  {/* Price */}
                  <div className="col-span-1 sm:col-span-2 font-mono flex sm:block justify-between items-center">
                    <span className="sm:hidden text-xs text-text-secondary uppercase mr-2">Price:</span>
                    {hasPrice ? (
                      <span className="text-text-primary">
                        {product.latest_price} <span className="text-text-secondary">{product.latest_currency}</span>
                      </span>
                    ) : (
                      <span className="text-neutral text-xs uppercase">Null</span>
                    )}
                  </div>

                  {/* Stock */}
                  <div className="col-span-1 sm:col-span-2 font-mono text-xs uppercase flex sm:block justify-between items-center">
                    <span className="sm:hidden text-xs text-text-secondary uppercase mr-2">Stock:</span>
                    {hasStockData ? (
                      inStock ? (
                        <span className="text-success">In Stock</span>
                      ) : (
                        <span className="text-critical">Stockout</span>
                      )
                    ) : (
                      <span className="text-neutral">Unknown</span>
                    )}
                  </div>

                  {/* Triggers */}
                  <div className="col-span-1 sm:col-span-4 text-left sm:text-right font-mono text-xs text-text-secondary flex flex-wrap sm:justify-end gap-2 mt-2 sm:mt-0">
                    {product.price_drop_threshold_pct > 0 && (
                      <span className="bg-ink px-2 py-1 border border-hairline rounded-sm">
                        ▼ {product.price_drop_threshold_pct}%
                      </span>
                    )}
                    {product.notify_on_restock && (
                      <span className="bg-ink px-2 py-1 border border-hairline rounded-sm text-success">
                        Restock
                      </span>
                    )}
                    {product.notify_on_stockout && (
                      <span className="bg-ink px-2 py-1 border border-hairline rounded-sm text-critical">
                        Stockout
                      </span>
                    )}
                  </div>

                </div>
              </Link>
            );
          })}
          
          {products.length === 0 && (
            <div className="p-8 text-center text-text-secondary font-mono text-sm">
              NO_TARGETS_CONFIGURED
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
