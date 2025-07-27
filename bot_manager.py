import threading
import time
import logging
import random
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from bot.scraper import run_bot

logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.scheduler = None
        self.is_running = False
        self.last_run_time = None
        self.run_count = 0
        self.error_count = 0
        
    def job(self):
        """Job function that runs the bot"""
        logger.info("Starting bot execution...")
        self.last_run_time = datetime.now()
        try:
            run_bot()
            logger.info("Bot execution completed successfully")
            self.run_count += 1
        except Exception as e:
            logger.error(f"Bot execution failed: {e}")
            self.error_count += 1
    
    def start_scheduled_bot(self, interval_minutes=None):
        """Start the scheduled bot"""
        if self.is_running:
            logger.warning("Bot scheduler is already running")
            return False
        
        try:
            self.scheduler = BackgroundScheduler()
            
            # Use provided interval or random between 1-10 minutes
            delay = interval_minutes if interval_minutes else random.randint(1, 10)
            
            self.scheduler.add_job(self.job, "interval", minutes=delay)
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"Bot scheduler started with {delay} minute interval")
            return True
        except Exception as e:
            logger.error(f"Failed to start bot scheduler: {e}")
            return False
    
    def stop_scheduled_bot(self):
        """Stop the scheduled bot"""
        if not self.is_running or not self.scheduler:
            logger.warning("Bot scheduler is not running")
            return False
        
        try:
            self.scheduler.shutdown()
            self.scheduler = None
            self.is_running = False
            logger.info("Bot scheduler stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop bot scheduler: {e}")
            return False
    
    def run_once(self):
        """Run the bot once manually"""
        try:
            logger.info("Running bot manually...")
            self.job()
            return True
        except Exception as e:
            logger.error(f"Manual bot run failed: {e}")
            return False
    
    def get_status(self):
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'last_run_time': self.last_run_time,
            'run_count': self.run_count,
            'error_count': self.error_count,
            'scheduler_active': self.scheduler is not None and self.scheduler.running
        }
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        if self.scheduler and self.is_running:
            jobs = self.scheduler.get_jobs()
            if jobs:
                return jobs[0].next_run_time
        return None

# Global bot manager instance
bot_manager = BotManager() 