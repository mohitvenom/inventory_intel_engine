# Scheduler Configuration

The Inventory Intel Agent uses a standalone scheduler process powered by `APScheduler` to run the LangGraph orchestrator periodically.

## Standalone Worker Architecture

We run the scheduler as its own dedicated Python process (`backend/scheduler/run_scheduler.py`) rather than embedding it in the FastAPI app (`main.py`). 
This guarantees that heavy orchestration logic (which spawns subprocesses for the MCP server) does not block or conflict with the asynchronous event loop serving HTTP requests.

## Overlap Prevention and Stale Lock Recovery

To prevent a new scheduled run from beginning while an old run is still processing, the scheduler employs a **database lock mechanism**.
- Before starting a graph execution, `job_wrapper` queries the database for any `AgentRun` rows with `status='running'`.
- If any are found, the scheduler logs a warning and **skips the current tick**.

However, if a worker process crashes completely (e.g., OOM kill, manual force kill), a running job could become orphaned and permanently block future cycles. To recover from this, we enforce a **Stale Lock Timeout**:
- If an `AgentRun` with `status='running'` is older than `AGENT_RUN_STALE_TIMEOUT_MINUTES` (defaults to 15), it is marked as `failed` with the error `marked failed: exceeded stale timeout, likely orphaned from a crashed process`.
- Once stale jobs are cleared, the scheduler will proceed to start a fresh orchestration cycle.

This guarantees that only one orchestration cycle is active at any time, protecting both local memory and the target e-commerce sites from parallel scraping storms, while seamlessly recovering from ungraceful process terminations.

## Top-Level Resilience

If the agent graph throws an unhandled exception (e.g., LLM failure, LangGraph crash) during normal execution, the exception is caught by the top-level scheduler `job_wrapper`. 
The scheduler will safely:
1. Log the full traceback.
2. Mark ONLY the specific `AgentRun` that this exact invocation started (and not any other running jobs) as `failed` in PostgreSQL.
3. Keep the scheduler event loop alive, ensuring that the *next* tick fires normally.

## Running the Scheduler

### In Development
You can start the scheduler in the foreground alongside your other services:

```bash
# Ensure virtual environment is activated
python -m backend.scheduler.run_scheduler
```

### In Production
For production environments, the scheduler should be managed by a process supervisor.
- **Docker Compose**: You can define a new service in `docker-compose.yml` (e.g. `scheduler`) that uses the same `backend` image but overrides the command to `python -m backend.scheduler.run_scheduler`.
- **Systemd**: You can create an `/etc/systemd/system/inventory-scheduler.service` file that runs the module with your active `venv`.

## Configuration
The interval is controlled by the following environment variable in `.env`:
`AGENT_RUN_INTERVAL_MINUTES` (defaults to 30).
