from formatters.base import BaseFormatter
from models.ticket import Ticket
from core.config import Config

class TelegramTicketFormatter(BaseFormatter):
    def format(self, item: Ticket) -> str:
        """
        Formats a Ticket object into a beautiful Telegram HTML message.
        """
        # Ensure price is nicely formatted (e.g., 2,150,000)
        formatted_price = f"{item.price:,.0f}".replace(",", " ")
        
        # We can format dates better, but assuming they are strings or datetime
        dep_date_str = item.departure_date if isinstance(item.departure_date, str) else item.departure_date.strftime("%Y-%m-%d")
        
        html = (
            f"✈️ <b>Yangi Arzon Chipta Topildi!</b>\n\n"
            f"🛫 <b>Yo'nalish:</b> {item.from_city} ➔ {item.to_city}\n"
            f"📅 <b>Uchish sanasi:</b> {dep_date_str}\n"
            f"🏢 <b>Aviakompaniya:</b> {item.airline}\n\n"
            f"💰 <b>Narxi:</b> {formatted_price} {item.currency}\n\n"
            f"🔗 <a href='{item.booking_url}'>Chiptani band qilish</a>\n\n"
            f"👉 Barcha chiptalar bu yerda: @aviasales_uzbekistan_bot" # Example ending
        )
        # Rasm qo'shilishi (amaliyotda bu rasm URL'ni item yoki boshqa joydan olamiz)
        # Test uchun bitta istalgan rasm URL'i kiritamiz
        demo_photo_url = "https://picsum.photos/800/400"
        
        return {
            "content": html,
            "photo": demo_photo_url
        }
