import asyncio
import logging
from datetime import datetime

from core.config import Config
from models.ticket import Ticket
from formatters.telegram_ticket import TelegramTicketFormatter
from publishers.telegram import TelegramPublisher
from schedulers.random_daily import RandomDailyScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

async def mock_data_producer(queue: asyncio.Queue):
    """
    Simulates external data collectors adding data to the system.
    """
    mock_tickets = [
        Ticket(
            source="Uzbekistan Airways",
            from_city="Tashkent",
            to_city="Istanbul",
            departure_date="2026-06-25",
            arrival_date="2026-06-25",
            airline="Uzbekistan Airways",
            price=2150000,
            currency="UZS",
            booking_url="https://example.com/book/1"
        ),
        Ticket(
            source="Aviasales",
            from_city="Tashkent",
            to_city="Dubai",
            departure_date="2026-07-10",
            arrival_date="2026-07-10",
            airline="FlyDubai",
            price=1800000,
            currency="UZS",
            booking_url="https://example.com/book/2"
        )
    ]
    
    # Pre-populate queue with 50 mock items
    for _ in range(25):
        for ticket in mock_tickets:
            await queue.put(ticket)
            
    logger.info(f"Mock data producer populated queue with {queue.qsize()} items.")

async def main():
    logger.info("Initializing Telegram Publishing System...")
    
    # 1. Setup in-memory queue (simulating a database/message broker)
    queue = asyncio.Queue()
    
    # 2. Setup presentation and infrastructure layers
    formatter = TelegramTicketFormatter()
    publisher = TelegramPublisher(
        bot_token=Config.TELEGRAM_BOT_TOKEN,
        chats_file=Config.ACTIVE_CHATS_FILE
    )
    
    # 3. Setup application logic (scheduler)
    scheduler = RandomDailyScheduler(
        queue=queue,
        formatter=formatter,
        publisher=publisher,
        posts_per_day=Config.POSTS_PER_DAY,
        start_hour=Config.POSTING_WINDOW_START_HOUR,
        end_hour=Config.POSTING_WINDOW_END_HOUR
    )
    
    # 4. Start background tasks
    asyncio.create_task(mock_data_producer(queue))  # Mock data
    asyncio.create_task(publisher.start_polling())  # Listen for new groups/channels
    
    # 5. Start scheduler (blocks forever)
    await scheduler.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Publishing system stopped by user.")
