import random
import time
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from bot.scraper import run_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_logs.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def job():
    logger.info("Starting bot execution...")
    try:
        run_bot()
        logger.info("Bot execution completed successfully")
    except Exception as e:
        logger.error(f"Bot execution failed: {e}")

logger.info("Initializing LinkedIn automation bot...")
scheduler = BlockingScheduler()
delay = random.randint(1, 10)
scheduler.add_job(job, "interval", minutes=delay)
logger.info(f"Scheduled job every {delay} minutes")
logger.info("Bot scheduler started. Press Ctrl+C to stop.")
scheduler.start()
