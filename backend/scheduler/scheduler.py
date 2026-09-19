import logging
import traceback
from datetime import datetime, timezone
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
    db = SessionLocal()
    try:
        running_jobs = db.query(AgentRun).filter(AgentRun.status == RunStatusEnum.running).all()
        if running_jobs:
            logger.warning(f"Overlap prevention: Found {len(running_jobs)} running job(s). Skipping this tick.")
            return
    finally:
        db.close()
        
    try:
        logger.info("No overlapping jobs found. Proceeding with agent run.")
        await async_run_agent()
        logger.info("Agent run finished successfully.")
    except Exception as e:
        logger.error(f"Top-level resilience: Unhandled exception in agent run: {e}")
        logger.error(traceback.format_exc())
        
        # Mark any stuck 'running' jobs as failed
        db = SessionLocal()
        try:
            stuck_jobs = db.query(AgentRun).filter(AgentRun.status == RunStatusEnum.running).all()
            for job in stuck_jobs:
                job.status = RunStatusEnum.failed
                job.error = "Failed due to unhandled exception in scheduler job wrapper"
                job.finished_at = datetime.now(timezone.utc)
            db.commit()
            if stuck_jobs:
                logger.info(f"Marked {len(stuck_jobs)} stuck job(s) as failed.")
        except Exception as db_e:
            logger.error(f"Failed to update DB for stuck jobs: {db_e}")
        finally:
            db.close()
