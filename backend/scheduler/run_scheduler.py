import os
import asyncio
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.scheduler.scheduler import job_wrapper

# Ensure basic logging is setup for the whole standalone process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    load_dotenv()
    
    # Get interval from env, default to 30
    interval_str = os.getenv("AGENT_RUN_INTERVAL_MINUTES", "30")
    try:
        interval_minutes = int(interval_str)
    except ValueError:
        logger.error(f"Invalid AGENT_RUN_INTERVAL_MINUTES: {interval_str}. Defaulting to 30.")
        interval_minutes = 30
        
    logger.info(f"Starting Inventory Intel Agent Scheduler with interval: {interval_minutes} minutes")
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job_wrapper, 'interval', minutes=interval_minutes)
    scheduler.start()
    
    logger.info("Scheduler started. Running indefinitely...")
    try:
        # Keep the event loop running forever
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
