# Dashboard & API Documentation

## FastAPI DB API (Read-Only)

The `backend/app/api.py` router provides read-only HTTP endpoints querying the PostgreSQL database directly, designed to power the Next.js frontend. It runs alongside the MCP server.

### Available Endpoints
- `GET /api/products`: Returns the active watchlist, including the latest recorded price and stock status for each item.
- `GET /api/products/{id}/price-history`: Returns the chronological price history array for a specific product.
- `GET /api/products/{id}/stock-history`: Returns the chronological stock history array.
- `GET /api/alerts`: Returns the recent alerts log (optionally filtered by `?product_id=X`).
- `GET /api/runs`: Returns a high-level summary list of recent agent orchestration runs.
- `GET /api/runs/{id}`: Returns a single agent run, including its full trace JSONB output (with the LLM-generated summary and individual product results).

## Next.js Dashboard

The dashboard is built with Next.js 14, Tailwind CSS, and Recharts. 

### Running Locally

To run the complete system with the dashboard locally:

1. **Start the FastAPI Backend** (serves `127.0.0.1:8000`):
   ```bash
   # From project root
   source venv/Scripts/activate
   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
   ```

2. **Start the Next.js Frontend** (serves `localhost:3000`):
   ```bash
   cd dashboard
   npm run dev
   ```

3. (Optional) **Start the Agent Scheduler** (to populate live data):
   ```bash
   # From project root
   source venv/Scripts/activate
   python -m backend.scheduler.run_scheduler
   ```

Open [http://localhost:3000](http://localhost:3000) to view the Watchlist, Agent Runs, and Alert logs.
