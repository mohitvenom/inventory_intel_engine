"use client";

import { useState } from "react";
import { Plus, X } from "lucide-react";
import { useRouter } from "next/navigation";

export function AddProductModal({ marketplaces }: { marketplaces: any[] }) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const [formData, setFormData] = useState({
    name: "",
    source: marketplaces[0]?.id || "",
    external_id: "",
    region: "",
    currency: "USD",
    price_drop_threshold_pct: 5.0,
    notify_on_restock: true,
    notify_on_stockout: true
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
      
      const payload = { ...formData };
      if (!payload.region) payload.region = null as any;

      const res = await fetch(`${apiUrl}/products`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        setIsOpen(false);
        setFormData({
            name: "",
            source: marketplaces[0]?.id || "",
            external_id: "",
            region: "",
            currency: "USD",
            price_drop_threshold_pct: 5.0,
            notify_on_restock: true,
            notify_on_stockout: true
        });
        router.refresh();
      } else {
        const data = await res.json();
        setError(data.detail || "Failed to add product");
      }
    } catch (err: any) {
      setError(err.message || "Network error");
    } finally {
      setLoading(false);
    }
  }

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 text-ink text-sm font-bold font-mono tracking-wider transition-colors rounded-sm"
      >
        <Plus className="w-4 h-4" /> ADD_TARGET
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-ink/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-panel border border-hairline p-6 w-full max-w-lg rounded-sm shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-bold font-mono text-text-primary">ADD_NEW_TARGET</h2>
          <button onClick={() => setIsOpen(false)} className="text-text-secondary hover:text-text-primary">
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 border border-critical/50 bg-critical/10 text-critical text-sm font-mono rounded-sm">
            ERROR: {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 font-mono text-sm">
          <div>
            <label className="block text-text-secondary mb-1">Name / Label</label>
            <input required type="text" className="w-full bg-ink border border-hairline px-3 py-2 text-text-primary focus:border-accent outline-none" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-text-secondary mb-1">Source</label>
              <select className="w-full bg-ink border border-hairline px-3 py-2 text-text-primary focus:border-accent outline-none" value={formData.source} onChange={e => setFormData({...formData, source: e.target.value})}>
                {marketplaces.map(m => (
                  <option key={m.id} value={m.id}>{m.display_name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-text-secondary mb-1">Region (Optional)</label>
              <input type="text" placeholder="e.g. us, uk" className="w-full bg-ink border border-hairline px-3 py-2 text-text-primary focus:border-accent outline-none" value={formData.region} onChange={e => setFormData({...formData, region: e.target.value})} />
            </div>
          </div>
          <div>
            <label className="block text-text-secondary mb-1">External ID / URL</label>
            <input required type="text" placeholder="e.g. B08N5LNQCX or https://..." className="w-full bg-ink border border-hairline px-3 py-2 text-text-primary focus:border-accent outline-none" value={formData.external_id} onChange={e => setFormData({...formData, external_id: e.target.value})} />
          </div>
          
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-hairline">
            <div>
              <label className="block text-text-secondary mb-1">Drop Thresh %</label>
              <input type="number" step="0.1" className="w-full bg-ink border border-hairline px-3 py-2 text-text-primary focus:border-accent outline-none" value={formData.price_drop_threshold_pct} onChange={e => setFormData({...formData, price_drop_threshold_pct: parseFloat(e.target.value)})} />
            </div>
            <div className="flex items-center gap-2 pt-6">
              <input type="checkbox" id="restock" checked={formData.notify_on_restock} onChange={e => setFormData({...formData, notify_on_restock: e.target.checked})} className="accent-accent" />
              <label htmlFor="restock" className="text-text-secondary cursor-pointer">Restock</label>
            </div>
            <div className="flex items-center gap-2 pt-6">
              <input type="checkbox" id="stockout" checked={formData.notify_on_stockout} onChange={e => setFormData({...formData, notify_on_stockout: e.target.checked})} className="accent-accent" />
              <label htmlFor="stockout" className="text-text-secondary cursor-pointer">Stockout</label>
            </div>
          </div>

          <div className="pt-6 flex justify-end gap-4">
            <button type="button" onClick={() => setIsOpen(false)} className="px-4 py-2 border border-hairline text-text-secondary hover:text-text-primary transition-colors">
              CANCEL
            </button>
            <button type="submit" disabled={loading} className="px-4 py-2 bg-accent hover:bg-accent/80 text-ink font-bold transition-colors disabled:opacity-50 flex items-center gap-2">
              {loading && <span className="animate-spin text-lg inline-block">⟳</span>}
              {loading ? "VERIFYING..." : "SAVE & VERIFY"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
