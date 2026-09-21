# Inventory Intel Agent

An autonomous AI agent designed to monitor e-commerce inventory and pricing, built with LangGraph, FastAPI, Next.js, and the Model Context Protocol (MCP). The agent orchestrates targeted scraping runs, evaluates price drops and stock changes against user-defined thresholds, updates a centralized database, and generates concise natural language summaries of its findings.

## Architecture

```mermaid
graph TD
    A[Scheduler / Cron] -->|Triggers Run| B(LangGraph Agent)
    B -->|Tools| C[MCP Server]
    C -->|Scrapes| D((Amazon))
    C -->|Scrapes| E((Ubuy))
    C -->|Queries/Updates| F[(PostgreSQL)]
    B -->|Summarizes| G[LLM (OpenAI)]
    B -->|Logs| F
    H[Next.js Dashboard] -->|Reads| I(FastAPI Read-only)
    I -->|Queries| F
```

## Tech Stack
- **Orchestration**: LangGraph, Langchain
- **MCP Tools Integration**: `langchain-mcp-adapters`
- **Backend / MCP Server**: FastAPI, Python 3.12, Uvicorn
- **Database**: PostgreSQL 16, SQLAlchemy 2.0, Alembic
- **Scraping**: BeautifulSoup4, Cloudscraper
- **Frontend**: Next.js 14, TailwindCSS, Recharts
- **Testing & Tooling**: Playwright (for dashboard screenshot capture), Pytest
- **Deployment**: Docker, Docker Compose

## Core Components
- **The MCP Server**: The scraper functions and database operations are encapsulated in a robust Model Context Protocol (MCP) server. This makes the tools highly reusable and protocol-verified, allowing any MCP-compatible client to invoke them.
- **The Agent**: A stateful LangGraph orchestrator that iterates over the watchlist, calls MCP tools, evaluates pricing logic, and utilizes an LLM to generate run summaries.
- **The Dashboard**: A responsive Next.js web application that visualizes price history, stock charts, recent runs, and alerts.

## Setup Instructions

### Option 1: Docker Compose (Recommended)
You can run the entire stack (PostgreSQL, FastAPI Backend, Scheduler, and Next.js Dashboard) via Docker Compose.
1. Clone the repository.
2. Create a `.env` file at the root based on `.env.example` (ensure `OPENAI_API_KEY` is set).
3. Run `docker-compose up -d --build`.
4. Access the dashboard at `http://localhost:3000`. The API will be available at `http://localhost:8000`.

### Option 2: Local Development
1. **Database**: Run PostgreSQL 16 locally and create a database (default: `inventory`).
2. **Backend**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   alembic upgrade head
   python -m backend.app.main
   ```
3. **Scheduler**: Run the agent in a separate terminal: `python -m backend.scheduler.run_scheduler`
4. **Frontend**:
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

## Highlights
- **Intelligent Thresholds**: Alerts are only triggered if the price drops by a user-configured percentage, preventing noise from minor fluctuations.
- **Multi-Currency Support**: Persists and reports the original currency of the product, with fallback logic for scraping anomalies.
- **Robust Orchestration**: Built with LangGraph, enabling stateful tracking and clean error recovery for individual product failures without crashing the entire run.

## Known Limitations
- **Amazon CAPTCHA & Region Restrictions**: Under heavy testing traffic or certain region configurations, Amazon serves CAPTCHA or bot-challenge pages. These are successfully caught and reported as errors by the agent (they are *not* bypassed or handled seamlessly).
- **Ubuy JS-Rendered Prices**: Ubuy occasionally uses JavaScript rendering for pricing, which bypasses static scrapers. The agent falls back to detecting stock status without the price.
