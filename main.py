import random
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from bot.scraper import run_bot


def job():
    print("Running bot...")
    run_bot()


scheduler = BlockingScheduler()
delay = random.randint(1, 10)
scheduler.add_job(job, "interval", minutes=delay)
print(f"Scheduled job every {delay} minutes")
scheduler.start()
