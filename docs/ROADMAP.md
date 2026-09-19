# Inventory Intel Agent - Project Roadmap

- [x] **Phase 1**: Initial scaffolding (FastAPI, Docker, config).
- [x] **Phase 2**: Database setup (PostgreSQL, models, Alembic, seeding).
- [x] **Phase 3**: Core scrapers (Pure python functions for Amazon/Ubuy).
- [x] **Phase 4**: MCP Server (Expose scrapers and DB access as MCP tools).
- [x] **Phase 5**: LangGraph Agent (Orchestrator to run checks and summarize).
- [x] **Phase 6**: Alerting Engine (Slack webhooks, dedupe logic, `alerts_sent` tracking).
- [x] **Phase 7**: Scheduler (Cron job/APScheduler to run agent periodically).
- [x] **Phase 8**: Dashboard
  - Read-only FastAPI endpoints for querying Postgres.
  - Next.js 14 frontend for visualizing watchlist, price/stock history charts, and agent run traces.
- [ ] **Phase 10**: Email Alerts (SMTP integration, replacing/augmenting Slack).
