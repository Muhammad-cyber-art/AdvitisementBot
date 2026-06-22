import asyncio
import random
import logging
from datetime import datetime, timedelta, time
from typing import List
from formatters.base import BaseFormatter
from publishers.base import BasePublisher

logger = logging.getLogger(__name__)

class RandomDailyScheduler:
    def __init__(
        self,
        queue: asyncio.Queue,
        formatter: BaseFormatter,
        publisher: BasePublisher,
        posts_per_day: int,
        start_hour: int,
        end_hour: int
    ):
        self.queue = queue
        self.formatter = formatter
        self.publisher = publisher
        self.posts_per_day = posts_per_day
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.schedule: List[datetime] = []

    def _generate_daily_schedule(self, target_date: datetime.date) -> List[datetime]:
        """
        Generates a sorted list of random datetimes for the given date
        between start_hour and end_hour.
        """
        start_dt = datetime.combine(target_date, time(hour=self.start_hour))
        end_dt = datetime.combine(target_date, time(hour=self.end_hour))
        
        # Total seconds in the active window
        window_seconds = int((end_dt - start_dt).total_seconds())
        
        times = []
        for _ in range(self.posts_per_day):
            random_offset = random.randint(0, window_seconds)
            random_dt = start_dt + timedelta(seconds=random_offset)
            times.append(random_dt)
            
        return sorted(times)

    async def _publish_next(self):
        """Fetches an item from the queue, formats it, and publishes it."""
        try:
            # Wait for an item if the queue is empty
            item = await self.queue.get()
            
            # Presentation logic
            formatted_content = self.formatter.format(item)
            
            # Infrastructure logic
            if isinstance(formatted_content, dict):
                success = await self.publisher.publish(**formatted_content)
            else:
                success = await self.publisher.publish(formatted_content)
            
            if success:
                logger.info("Successfully published scheduled post.")
            else:
                logger.error("Failed to publish scheduled post.")
                # Depending on business logic, we could requeue the item:
                # await self.queue.put(item)
                
            self.queue.task_done()
        except Exception as e:
            logger.error(f"Error during publishing workflow: {e}")

    async def start(self):
        """Starts the infinite scheduling loop."""
        logger.info("Starting RandomDailyScheduler...")
        from core.config import Config
        
        while True:
            # Agar TEST_MODE yoniq bo'lsa, har 1 daqiqada post yuboradi
            if getattr(Config, "TEST_MODE", False):
                logger.info("TEST_MODE yoniq: 60 soniya kutish...")
                await asyncio.sleep(60)
                await self._publish_next()
                continue

            now = datetime.now()
            
            # If schedule is empty, generate it for today
            if not self.schedule:
                logger.info(f"Generating random schedule for {now.date()}...")
                self.schedule = self._generate_daily_schedule(now.date())
                
                # Filter out times that have already passed today
                self.schedule = [t for t in self.schedule if t > now]
                
                # If no times left for today (e.g., app started late at night)
                if not self.schedule:
                    logger.info("No posting times left for today. Generating for tomorrow.")
                    tomorrow = now.date() + timedelta(days=1)
                    self.schedule = self._generate_daily_schedule(tomorrow)

            # Get the next scheduled time
            next_run = self.schedule.pop(0)
            now = datetime.now()
            
            wait_seconds = (next_run - now).total_seconds()
            
            if wait_seconds > 0:
                logger.info(f"Next post scheduled at {next_run.strftime('%Y-%m-%d %H:%M:%S')}. Sleeping for {wait_seconds:.0f} seconds.")
                await asyncio.sleep(wait_seconds)
            
            # Trigger publish!
            logger.info(f"Time reached ({datetime.now().strftime('%H:%M:%S')}). Triggering publish workflow...")
            await self._publish_next()
