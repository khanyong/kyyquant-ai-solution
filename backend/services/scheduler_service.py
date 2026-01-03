
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.strategy_service import StrategyService
import asyncio
import os
import datetime

class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.strategy_service = StrategyService()
        self.is_running = False

    def start(self):
        if self.is_running:
            return
        
        # Add Jobs
        # Strategy Verification: Every 1 minute
        # We use a simple interval trigger for robust testing.
        self.scheduler.add_job(
            self._run_strategy_verification,
            'interval',
            minutes=1,
            id='strategy_verification',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        print("[Scheduler] Service Started (Interval: 1 min)")

    def stop(self):
        self.scheduler.shutdown()
        self.is_running = False
        print("[Scheduler] Service Stopped")

    def _run_strategy_verification(self):
        """
        Async wrapper for strategy verification
        """
        # Skip if outside market hours? (Optional)
        now = datetime.datetime.now()
        # Simple check: 09:00 ~ 15:30 (Weekdays) - Implementing strict check is good but strictly for SaaS might be overkill for now.
        # Let's run it 24/7 for debugging (during development).
        
        print(f"[Scheduler] Triggering Verification at {now}")
        try:
            # Create a new event loop for this thread to run async tasks
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.strategy_service.verify_all_active_strategies())
            loop.close()
        except Exception as e:
            print(f"[Scheduler] Verification Job Failed: {e}")

# Global Instance
scheduler_service = SchedulerService()
