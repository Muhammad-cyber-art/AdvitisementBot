import os
import sys
from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from .models import ActiveChat, Advertisement

# Tashqi papkani import qilish uchun sys.path ga qo'shamiz
parent_dir = os.path.dirname(settings.BASE_DIR)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from publishers.telegram import TelegramPublisher

@admin.register(ActiveChat)
class ActiveChatAdmin(admin.ModelAdmin):
    list_display = ('title', 'chat_id', 'added_at')
    search_fields = ('title', 'chat_id')

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'departure_date', 'price', 'is_published', 'created_at')
    list_filter = ('is_published', 'departure_date')
    search_fields = ('from_city', 'to_city', 'phone')
    readonly_fields = ('is_published',)
    
    def save_model(self, request, obj, form, change):
        was_published = obj.is_published
        super().save_model(request, obj, form, change)
        
        if not was_published:
            # Xabarni shakllantirish
            caption = (
                f"✈️ <b>Yangi E'lon!</b>\n\n"
                f"🛫 <b>Yo'nalish:</b> {obj.from_city} ➔ {obj.to_city}\n"
                f"📅 <b>Sana:</b> {obj.departure_date.strftime('%Y-%m-%d')}\n"
                f"💰 <b>Narxi:</b> {obj.price}\n\n"
                f"📞 <b>Murojaat uchun tel:</b> {obj.phone}\n"
            )
            if obj.telegram_username:
                caption += f"💬 <b>Telegram:</b> @{obj.telegram_username.replace('@', '')}\n"
            if obj.description:
                caption += f"\n📝 <b>Qo'shimcha izoh:</b> {obj.description}\n"

            # Tashqi TelegramPublisher'ni chaqiramiz
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "8034710652:AAG4sQ9mkHddhpjLyZGhmj6VYOaKqFw4B2k")
            
            # JSON fayl keraksiz bo'lsa ham parametr sifatida beramiz
            chats_file_path = os.path.join(parent_dir, "active_chats.json")
            publisher = TelegramPublisher(bot_token=bot_token, chats_file=chats_file_path)
            
            # Ma'lumotlar bazasidan active chat ID larni olamiz
            db_chat_ids = list(ActiveChat.objects.values_list('chat_id', flat=True))
            
            if not db_chat_ids:
                self.message_user(request, "Bazada hech qanday faol chat topilmadi. Yuborish bekor qilindi.", level=messages.ERROR)
                return

            # Asinxron publish funksiyasini sinxron holatda chaqiramiz, db_chat_ids uzatamiz
            # Bu yerda URL emas, faylning aniq manzilini uzatamiz (local rasm yuklash uchun)
            photo_path = obj.image.path if obj.image else None
            
            try:
                success = async_to_sync(publisher.publish)(content=caption, photo=photo_path, chat_ids=db_chat_ids)
                if success:
                    obj.is_published = True
                    obj.save(update_fields=['is_published'])
                    self.message_user(request, f"E'lon {len(db_chat_ids)} ta chatga muvaffaqiyatli yuborildi!", level=messages.SUCCESS)
                else:
                    self.message_user(request, "Yuborishda xatolik yuz berdi.", level=messages.ERROR)
            except Exception as e:
                self.message_user(request, f"Tashqi publisher bilan ulanishda xatolik: {e}", level=messages.ERROR)

