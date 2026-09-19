import Link from "next/link";
import { ProductCharts } from "./ProductCharts";

export const revalidate = 0;

async function getProductAndHistory(id: string) {
  const [productRes, priceRes, stockRes] = await Promise.all([
    fetch(`http://127.0.0.1:8000/api/products`, { cache: 'no-store' }),
    fetch(`http://127.0.0.1:8000/api/products/${id}/price-history`, { cache: 'no-store' }),
    fetch(`http://127.0.0.1:8000/api/products/${id}/stock-history`, { cache: 'no-store' })
  ]);
  
  if (!productRes.ok) throw new Error("Failed to fetch product");
  
  const products = await productRes.json();
  const product = products.find((p: any) => p.id === parseInt(id));
  
  const priceHistory = priceRes.ok ? await priceRes.json() : [];
  const stockHistory = stockRes.ok ? await stockRes.json() : [];
  
  return { product, priceHistory, stockHistory };
}

export default async function ProductPage({ params }: { params: { id: string } }) {
  const { product, priceHistory, stockHistory } = await getProductAndHistory(params.id);

  if (!product) return <div>Product not found</div>;

  return (
    <div>
      <div className="mb-4">
        <Link href="/" className="text-blue-600 hover:underline">
          &larr; Back to Watchlist
        </Link>
      </div>
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">{product.name}</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Source: {product.source} {product.region ? `(${product.region})` : ""}
          </p>
        </div>
      </div>
      
      <ProductCharts priceHistory={priceHistory} stockHistory={stockHistory} />
    </div>
  );
}
