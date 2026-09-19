import Link from "next/link";
import { ExternalLink } from "lucide-react";

export const revalidate = 0; // Disable static rendering for this page

async function getProducts() {
  const res = await fetch("http://127.0.0.1:8000/api/products", { cache: 'no-store' });
  if (!res.ok) {
    throw new Error("Failed to fetch products");
  }
  return res.json();
}

export default async function WatchlistPage() {
  const products = await getProducts();

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Watchlist</h1>
      </div>
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {products.map((product: any) => (
            <li key={product.id}>
              <Link href={`/products/${product.id}`} className="block hover:bg-gray-50">
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-blue-600 truncate">{product.name}</p>
                    <div className="ml-2 flex-shrink-0 flex">
                      <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        {product.source} {product.region ? `(${product.region})` : ""}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2 sm:flex sm:justify-between">
                    <div className="sm:flex">
                      <p className="flex items-center text-sm text-gray-500">
                        Price:{" "}
                        <span className="ml-1 font-semibold text-gray-900">
                          {product.latest_price !== null 
                            ? `${product.latest_price} ${product.latest_currency}` 
                            : "price unavailable"}
                        </span>
                      </p>
                      <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                        Stock:{" "}
                        <span className="ml-1 font-semibold text-gray-900">
                          {product.latest_stock !== null 
                            ? (product.latest_stock ? "In Stock" : "Out of Stock") 
                            : "unknown"}
                        </span>
                      </p>
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                      <p>
                        Drops {">="}{product.price_drop_threshold_pct}%
                        {product.notify_on_restock ? " | Restock" : ""}
                        {product.notify_on_stockout ? " | Stockout" : ""}
                      </p>
                    </div>
                  </div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
