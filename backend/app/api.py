import sys
import os
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel

from backend.db.session import SessionLocal
from backend.db.models import Product, PriceHistory, StockHistory, AlertSent, AgentRun
from backend.scrapers.registry import MARKETPLACES
from backend.scheduler.scheduler import check_overlap_and_start_run, execute_run_with_cleanup
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from backend.agent.graph import parse_mcp_result

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- MCP Helper ---
async def invoke_mcp_tool_with_timeout(tool_name: str, args: dict, timeout_sec: int = 15):
    async def _invoke():
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "backend.mcp_server.server"],
            env=dict(os.environ)
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                tool = next((t for t in tools if t.name == tool_name), None)
                if not tool:
                    return {"status": "error", "message": f"Tool {tool_name} not found"}
                res = await tool.ainvoke(args)
                return parse_mcp_result(res)
                
    try:
        return await asyncio.wait_for(_invoke(), timeout=timeout_sec)
    except asyncio.TimeoutError:
        return {"status": "error", "message": "Verification timed out"}

# --- Models ---
class ProductCreate(BaseModel):
    name: str
    source: str
    external_id: str
    region: Optional[str] = None
    currency: str = "USD"
    price_drop_threshold_pct: float = 5.0
    notify_on_restock: bool = True
    notify_on_stockout: bool = True
    
class ProductUpdate(BaseModel):
    price_drop_threshold_pct: Optional[float] = None
    notify_on_restock: Optional[bool] = None
    notify_on_stockout: Optional[bool] = None
    active: Optional[bool] = None

# --- Marketplaces ---
@router.get("/api/marketplaces")
def get_marketplaces():
    return [{"id": k, "display_name": v["display_name"]} for k, v in MARKETPLACES.items()]

# --- Products ---
@router.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    result = []
    for p in products:
        latest_price = db.query(PriceHistory).filter(PriceHistory.product_id == p.id).order_by(desc(PriceHistory.checked_at)).first()
        latest_stock = db.query(StockHistory).filter(StockHistory.product_id == p.id).order_by(desc(StockHistory.checked_at)).first()
        
        result.append({
            "id": p.id,
            "name": p.name,
            "source": p.source,
            "external_id": p.external_id,
            "region": p.region,
            "currency": p.currency,
            "price_drop_threshold_pct": p.price_drop_threshold_pct,
            "notify_on_restock": p.notify_on_restock,
            "notify_on_stockout": p.notify_on_stockout,
            "active": p.active,
            "latest_price": latest_price.price if latest_price else None,
            "latest_currency": latest_price.currency if latest_price else None,
            "latest_stock": latest_stock.in_stock if latest_stock else None
        })
    return result

@router.post("/api/products")
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    if product.source not in MARKETPLACES:
        raise HTTPException(status_code=400, detail=f"Unknown source {product.source}")
        
    marketplace = MARKETPLACES[product.source]
    mcp_tool_name = marketplace["mcp_tool_name"]
    args = marketplace["mcp_args_mapper"](product.model_dump())
    
    # Live Verification
    verify_res = await invoke_mcp_tool_with_timeout(mcp_tool_name, args, timeout_sec=15)
    
    if isinstance(verify_res, list) and len(verify_res) > 0:
        verify_res = verify_res[0]
    elif isinstance(verify_res, list):
        verify_res = {"status": "error", "message": "Empty response from verification"}
        
    if not isinstance(verify_res, dict) or verify_res.get("status") == "error":
        msg = verify_res.get("message", "Verification failed") if isinstance(verify_res, dict) else "Invalid verification format"
        err_type = verify_res.get("error_type") if isinstance(verify_res, dict) else ""
        if err_type:
            msg = f"{err_type} - {msg}"
        raise HTTPException(status_code=400, detail=msg)
        
    db_prod = Product(
        name=product.name,
        source=product.source,
        external_id=product.external_id,
        region=product.region,
        currency=verify_res.get("currency") or product.currency,
        price_drop_threshold_pct=product.price_drop_threshold_pct,
        notify_on_restock=product.notify_on_restock,
        notify_on_stockout=product.notify_on_stockout,
        active=True
    )
    db.add(db_prod)
    db.commit()
    db.refresh(db_prod)
    
    # Record initial price/stock
    if verify_res.get("price") is not None:
        ph = PriceHistory(product_id=db_prod.id, price=verify_res["price"], currency=db_prod.currency)
        db.add(ph)
    if verify_res.get("in_stock") is not None:
        sh = StockHistory(product_id=db_prod.id, in_stock=verify_res["in_stock"])
        db.add(sh)
    db.commit()
    
    return db_prod

@router.patch("/api/products/{product_id}")
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    db_prod = db.query(Product).get(product_id)
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")
        
    update_data = product_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(db_prod, k, v)
        
    db.commit()
    db.refresh(db_prod)
    return db_prod

@router.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_prod = db.query(Product).get(product_id)
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Soft delete
    db_prod.active = False
    db.commit()
    return {"status": "success", "message": "Product deactivated"}

@router.post("/api/products/{product_id}/check-now")
async def check_product_now(product_id: int, db: Session = Depends(get_db)):
    db_prod = db.query(Product).get(product_id)
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if db_prod.source not in MARKETPLACES:
        raise HTTPException(status_code=400, detail=f"Unknown source {db_prod.source}")
        
    marketplace = MARKETPLACES[db_prod.source]
    mcp_tool_name = marketplace["mcp_tool_name"]
    
    # We can dump the dict for the mapper
    p_dict = {
        "external_id": db_prod.external_id,
        "region": db_prod.region
    }
    args = marketplace["mcp_args_mapper"](p_dict)
    
    check_res = await invoke_mcp_tool_with_timeout(mcp_tool_name, args, timeout_sec=20)
    
    if isinstance(check_res, list) and len(check_res) > 0:
        check_res = check_res[0]
        
    if not isinstance(check_res, dict) or check_res.get("status") == "error":
        msg = check_res.get("message", "Check failed") if isinstance(check_res, dict) else "Invalid check format"
        err_type = check_res.get("error_type") if isinstance(check_res, dict) else ""
        if err_type:
            msg = f"{err_type} - {msg}"
        raise HTTPException(status_code=400, detail=msg)
        
    if check_res.get("price") is not None:
        ph = PriceHistory(product_id=db_prod.id, price=check_res["price"], currency=check_res.get("currency", db_prod.currency))
        db.add(ph)
    if check_res.get("in_stock") is not None:
        sh = StockHistory(product_id=db_prod.id, in_stock=check_res["in_stock"])
        db.add(sh)
    db.commit()
    
    return {"status": "success", "price": check_res.get("price"), "in_stock": check_res.get("in_stock")}

# --- Runs / History ---
@router.post("/api/runs/trigger")
async def trigger_run(background_tasks: BackgroundTasks):
    run_id = await check_overlap_and_start_run()
    if not run_id:
        return {"status": "queued_or_rejected", "message": "A run is already in progress."}
        
    background_tasks.add_task(execute_run_with_cleanup, run_id)
    return {"status": "started", "run_id": run_id}

@router.get("/api/products/{product_id}/price-history")
def get_price_history(product_id: int, limit: int = 50, db: Session = Depends(get_db)):
    history = db.query(PriceHistory).filter(PriceHistory.product_id == product_id).order_by(desc(PriceHistory.checked_at)).limit(limit).all()
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
