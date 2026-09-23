import Link from "next/link";
import { ProductCharts } from "./ProductCharts";

export const revalidate = 0;

async function getProductAndHistory(id: string) {
  const env = process.env;
  const apiUrl = env.API_URL || "http://127.0.0.1:8000/api";
  
  try {
    const [productRes, priceRes, stockRes] = await Promise.all([
      fetch(`${apiUrl}/products`, { cache: 'no-store' }),
      fetch(`${apiUrl}/products/${id}/price-history`, { cache: 'no-store' }),
      fetch(`${apiUrl}/products/${id}/stock-history`, { cache: 'no-store' })
    ]);
    
    if (!productRes.ok) throw new Error("Failed to fetch product");
    
    const products = await productRes.json();
    const product = products.find((p: any) => p.id === parseInt(id));
    
    const priceHistory = priceRes.ok ? await priceRes.json() : [];
    const stockHistory = stockRes.ok ? await stockRes.json() : [];
    
    return { product, priceHistory, stockHistory };
  } catch (e) {
    return { product: null, priceHistory: [], stockHistory: [] };
  }
}

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { product, priceHistory, stockHistory } = await getProductAndHistory(id);

  if (!product) {
    return (
      <div className="p-8 text-center text-text-secondary font-mono text-sm">
        PRODUCT_NOT_FOUND
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="mb-4">
        <Link href="/" className="text-text-secondary hover:text-text-primary text-xs font-mono uppercase tracking-wider transition-colors">
          &larr; BACK_TO_WATCHLIST
        </Link>
      </div>
      
      <div className="border border-hairline bg-panel p-4 sm:p-6 rounded-sm">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-xl font-bold text-text-primary">{product.name}</h1>
          {product.url && (
            <a href={product.url} target="_blank" rel="noopener noreferrer" className="text-neutral hover:text-text-primary transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
            </a>
          )}
        </div>
        <div className="flex flex-wrap gap-4 text-xs font-mono text-text-secondary uppercase">
          <span>ID: {product.id}</span>
          <span>SRC: {product.source}</span>
          {product.region && <span>REG: {product.region}</span>}
          {product.price_drop_threshold_pct > 0 && <span>THR: {product.price_drop_threshold_pct}%</span>}
        </div>
      </div>
      
      <ProductCharts priceHistory={priceHistory} stockHistory={stockHistory} />
    </div>
  );
}
