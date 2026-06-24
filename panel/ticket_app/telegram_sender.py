import requests
import os
from django.conf import settings
from .models import ActiveChat
from core.config import Config
def send_telegram_advertisement(ad):
    # Telegram bot tokenidan foydalanamiz
    bot_token = Config.TELEGRAM_BOT_TOKEN
    api_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    # HTML xabar matnini shakllantiramiz
    caption = (
        f"✈️ <b>Yangi E'lon!</b>\n\n"
        f"🛫 <b>Yo'nalish:</b> {ad.from_city} ➔ {ad.to_city}\n"
        f"📅 <b>Sana:</b> {ad.departure_date.strftime('%Y-%m-%d')}\n"
        f"💰 <b>Narxi:</b> {ad.price}\n\n"
        f"📞 <b>Murojaat uchun tel:</b> {ad.phone}\n"
    )
    if ad.telegram_username:
        caption += f"💬 <b>Telegram:</b> @{ad.telegram_username.replace('@', '')}\n"
    if ad.description:
        caption += f"\n📝 <b>Qo'shimcha izoh:</b> {ad.description}\n"

    # Aktiv chatlarni olamiz
    active_chats = ActiveChat.objects.all()
    if not active_chats.exists():
        return False, "Faol chatlar topilmadi!"

    # Rasm faylini ochamiz
    success_count = 0
    try:
        with open(ad.image.path, 'rb') as photo:
            for chat in active_chats:
                payload = {
                    "chat_id": chat.chat_id,
                    "caption": caption,
                    "parse_mode": "HTML"
                }
                files = {
                    "photo": photo
                }
                # Rasm pointerini boshiga qaytaramiz
                photo.seek(0)
                
                response = requests.post(api_url, data=payload, files=files)
                if response.status_code == 200:
                    success_count += 1
                else:
                    # Agar xatolik bo'lsa chat o'chirilgan yoki bot chiqarilgan bo'lishi mumkin
                    if response.status_code in [403, 400]:
                        chat.delete()
    except Exception as e:
        return False, str(e)

    return True, f"{success_count} ta chatga muvaffaqiyatli yuborildi."
