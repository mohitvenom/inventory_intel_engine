from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from backend.db.session import SessionLocal
from backend.db.models import Product, PriceHistory, StockHistory, AlertSent, AgentRun

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    # For the overview, we might also want to attach the latest price/stock.
    # We can fetch the latest price and stock for each product.
    result = []
    for p in products:
        latest_price = db.query(PriceHistory).filter(PriceHistory.product_id == p.id).order_by(desc(PriceHistory.checked_at)).first()
        latest_stock = db.query(StockHistory).filter(StockHistory.product_id == p.id).order_by(desc(StockHistory.checked_at)).first()
        
        result.append({
            "id": p.id,
            "name": p.name,
            "source": p.source,
            "region": p.region,
            "price_drop_threshold_pct": p.price_drop_threshold_pct,
            "notify_on_restock": p.notify_on_restock,
            "notify_on_stockout": p.notify_on_stockout,
            "latest_price": latest_price.price if latest_price else None,
            "latest_currency": latest_price.currency if latest_price else None,
            "latest_stock": latest_stock.in_stock if latest_stock else None
        })
    return result

@router.get("/api/products/{product_id}/price-history")
def get_price_history(product_id: int, limit: int = 50, db: Session = Depends(get_db)):
    history = db.query(PriceHistory).filter(PriceHistory.product_id == product_id).order_by(desc(PriceHistory.checked_at)).limit(limit).all()
    # Return ascending for charts
    history = reversed(history)
    return [{"timestamp": h.checked_at, "price": h.price, "currency": h.currency} for h in history]

@router.get("/api/products/{product_id}/stock-history")
def get_stock_history(product_id: int, limit: int = 50, db: Session = Depends(get_db)):
    history = db.query(StockHistory).filter(StockHistory.product_id == product_id).order_by(desc(StockHistory.checked_at)).limit(limit).all()
    history = reversed(history)
    return [{"timestamp": h.checked_at, "in_stock": h.in_stock} for h in history]

@router.get("/api/alerts")
def get_alerts(product_id: Optional[int] = None, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(AlertSent)
    if product_id:
        query = query.filter(AlertSent.product_id == product_id)
    alerts = query.order_by(desc(AlertSent.sent_at)).limit(limit).all()
    return [{"id": a.id, "product_id": a.product_id, "alert_type": a.alert_type, "timestamp": a.sent_at, "message": a.message} for a in alerts]

@router.get("/api/runs")
def get_runs(limit: int = 20, db: Session = Depends(get_db)):
    runs = db.query(AgentRun).order_by(desc(AgentRun.started_at)).limit(limit).all()
    # Only return high-level summary, not full trace
    return [{
        "id": r.id, 
        "status": r.status.value if r.status else None, 
        "started_at": r.started_at, 
        "finished_at": r.finished_at,
        "products_checked": r.products_checked,
        "error": r.error,
        "summary": r.trace.get("summary") if r.trace else None
    } for r in runs]

@router.get("/api/runs/{run_id}")
def get_run_trace(run_id: int, db: Session = Depends(get_db)):
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "id": run.id,
        "status": run.status.value if run.status else None,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "trace": run.trace
    }
