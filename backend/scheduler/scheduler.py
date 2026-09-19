import logging
import traceback
import os
from datetime import datetime, timezone, timedelta
from backend.db.session import SessionLocal
from backend.db.models import AgentRun, RunStatusEnum
from backend.agent.run_agent import async_run_agent

logger = logging.getLogger(__name__)

async def job_wrapper():
    """
    Executes the agent run while providing top-level resilience and overlap prevention.
    """
    logger.info("Scheduler tick: Starting job_wrapper...")
    
    # Check for overlapping runs (status='running')
    stale_timeout_minutes = int(os.getenv("AGENT_RUN_STALE_TIMEOUT_MINUTES", "15"))
    now = datetime.now(timezone.utc)
    db = SessionLocal()
    try:
        running_jobs = db.query(AgentRun).filter(AgentRun.status == RunStatusEnum.running).all()
        active_jobs = 0
        for job in running_jobs:
            # If naive datetime, make it aware (fallback)
            started_at = job.started_at
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
                
            if (now - started_at) > timedelta(minutes=stale_timeout_minutes):
                logger.warning(f"Stale lock detected for run {job.id}. Marking as failed.")
                job.status = RunStatusEnum.failed
                job.error = "marked failed: exceeded stale timeout, likely orphaned from a crashed process"
                job.finished_at = now
            else:
                active_jobs += 1
        db.commit()
        
        if active_jobs > 0:
            logger.warning(f"Overlap prevention: Found {active_jobs} active running job(s). Skipping this tick.")
            return
    finally:
        db.close()
        
    start_time = datetime.now(timezone.utc)
        
    run_ctx = {}
    try:
        logger.info("No overlapping jobs found. Proceeding with agent run.")
        await async_run_agent(run_ctx)
        logger.info("Agent run finished successfully.")
    except Exception as e:
        logger.error(f"Top-level resilience: Unhandled exception in agent run: {e}")
        logger.error(traceback.format_exc())
        
        # Mark ONLY the run this invocation owns (the exact run_id we captured)
        run_id = run_ctx.get("run_id")
        if run_id:
            db = SessionLocal()
            try:
                my_job = db.query(AgentRun).filter(AgentRun.id == run_id).first()
                if my_job and my_job.status == RunStatusEnum.running:
                    my_job.status = RunStatusEnum.failed
                    my_job.error = "Failed due to unhandled exception in scheduler job wrapper"
                    my_job.finished_at = datetime.now(timezone.utc)
                    db.commit()
                    logger.info(f"Marked our crashed job (run_id={run_id}) as failed.")
                else:
                    logger.info(f"Job (run_id={run_id}) is not in running state or not found.")
            except Exception as db_e:
                logger.error(f"Failed to update DB for our crashed job: {db_e}")
            finally:
                db.close()
        else:
            logger.info("No run_id was captured; nothing to clean up.")
