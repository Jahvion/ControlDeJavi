import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
import bot

scheduler = BackgroundScheduler()

def run_async_notification():
    asyncio.run(bot.send_daily_notification())

def start_scheduler():
    argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
    
    trigger = CronTrigger(
        hour=22,
        minute=0,
        timezone=argentina_tz
    )
    
    scheduler.add_job(
        run_async_notification,
        trigger=trigger,
        id='daily_notification',
        name='Daily expiration check at 22:00 Argentina time',
        replace_existing=True
    )
    
    scheduler.start()
    print(f"Scheduler started. Daily notifications will run at 22:00 Argentina time.")
    print(f"Current time in Argentina: {datetime.now(argentina_tz).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    jobs = scheduler.get_jobs()
    for job in jobs:
        print(f"Scheduled job: {job.name} - Next run: {job.next_run_time}")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler stopped")
