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

export default async function ProductPage({ params }: { params: { id: string } }) {
  const { product, priceHistory, stockHistory } = await getProductAndHistory(params.id);

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
        <h1 className="text-xl font-bold text-text-primary mb-2">{product.name}</h1>
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
