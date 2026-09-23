"use client";

import { useState } from "react";
import { Play, Settings, Trash2, Check, X, ExternalLink } from "lucide-react";
import { useRouter } from "next/navigation";

export function ProductActions({ product }: { product: any }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const router = useRouter();

  async function checkNow(e: React.MouseEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
      const res = await fetch(`${apiUrl}/products/${product.id}/check-now`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        if (data.price) {
          setSuccess(`$${data.price}`);
        } else {
          setSuccess(data.in_stock ? "In Stock" : "Out of Stock");
        }
        router.refresh();
      } else {
        setError(data.detail || "Check failed");
      }
    } catch (err: any) {
      setError(err.message || "Network error");
    } finally {
      setLoading(false);
      setTimeout(() => { setError(null); setSuccess(null); }, 5000);
    }
  }

  async function deactivate(e: React.MouseEvent) {
    e.preventDefault();
    if (!confirmDelete) {
      setConfirmDelete(true);
      setTimeout(() => setConfirmDelete(false), 3000);
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
      const res = await fetch(`${apiUrl}/products/${product.id}`, { method: "DELETE" });
      if (res.ok) {
        router.refresh();
      } else {
        const data = await res.json();
        setError(data.detail || "Deactivate failed");
      }
    } catch (err: any) {
      setError(err.message || "Network error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex gap-2 items-center justify-end relative">
      {error && (
        <span className="text-[10px] text-critical bg-critical/10 px-1.5 py-0.5 border border-critical/20 absolute right-full mr-2 whitespace-nowrap rounded-sm">
          {error}
        </span>
      )}
      {success && (
        <span className="text-[10px] text-success bg-success/10 px-1.5 py-0.5 border border-success/20 absolute right-full mr-2 whitespace-nowrap rounded-sm flex items-center gap-1">
          <Check className="w-3 h-3" /> {success}
        </span>
      )}
      
      {product.url && (
        <button
          onClick={(e) => {
            e.preventDefault();
            window.open(product.url, '_blank');
          }}
          title="Open in Store"
          className="p-1.5 border border-hairline text-text-secondary hover:text-accent hover:border-accent hover:bg-surface transition-colors rounded-sm"
        >
          <ExternalLink className="w-3.5 h-3.5" />
        </button>
      )}
      
      <button 
        onClick={checkNow} 
        disabled={loading}
        title="Check Now"
        className="p-1.5 border border-hairline text-text-secondary hover:text-accent hover:border-accent hover:bg-surface transition-colors disabled:opacity-50 rounded-sm"
      >
        <Play className="w-3.5 h-3.5" />
      </button>
      <button 
        onClick={(e) => { e.preventDefault(); setError("Edit coming soon"); setTimeout(() => setError(null), 3000); }} 
        title="Settings"
        className="p-1.5 border border-hairline text-text-secondary hover:text-text-primary hover:border-text-primary hover:bg-surface transition-colors rounded-sm"
      >
        <Settings className="w-3.5 h-3.5" />
      </button>
      
      {confirmDelete ? (
        <button 
          onClick={deactivate} 
          disabled={loading}
          title="Confirm Deactivate"
          className="p-1.5 border border-critical text-critical bg-critical/10 hover:bg-critical/20 transition-colors disabled:opacity-50 rounded-sm flex items-center gap-1 text-xs font-bold"
        >
          CONFIRM
        </button>
      ) : (
        <button 
          onClick={deactivate} 
          disabled={loading}
          title="Deactivate"
          className="p-1.5 border border-hairline text-text-secondary hover:text-critical hover:border-critical hover:bg-critical/10 transition-colors disabled:opacity-50 rounded-sm"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
