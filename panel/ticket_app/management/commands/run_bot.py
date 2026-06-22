import os
import time
import requests
from django.core.management.base import BaseCommand
from ticket_app.models import ActiveChat

class Command(BaseCommand):
    help = 'Runs Telegram bot long-polling to track active groups and channels.'

    def handle(self, *args, **kwargs):
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "8034710652:AAG4sQ9mkHddhpjLyZGhmj6VYOaKqFw4B2k")
        if bot_token == "YOUR_TELEGRAM_BOT_TOKEN":
            self.stdout.write(self.style.ERROR("Bot token berilmagan, polling ishga tushmaydi."))
            return

        api_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        offset = 0

        self.stdout.write(self.style.SUCCESS('Telegram Polling ishga tushdi. Bot qayerga qo\'shilsa kuzatib boradi...'))

        while True:
            try:
                response = requests.get(f"{api_url}?timeout=30&offset={offset}", timeout=35)
                if response.status_code == 200:
                    data = response.json()
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        self.process_update(update)
                else:
                    time.sleep(5)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Polling xatosi: {e}"))
                time.sleep(5)

    def process_update(self, update):
        chat_id = None
        chat_title = "Unknown"
        
        # 1. Bot kanalga qo'shilganda yoki huquqlari o'zgarganda (my_chat_member)
        if "my_chat_member" in update:
            chat_id = update["my_chat_member"]["chat"]["id"]
            chat_title = update["my_chat_member"]["chat"].get("title", str(chat_id))
            new_status = update["my_chat_member"]["new_chat_member"]["status"]
            
            if new_status in ["administrator", "member"]:
                obj, created = ActiveChat.objects.get_or_create(chat_id=str(chat_id), defaults={"title": chat_title})
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✅ Bot yangi guruh/kanalga qo'shildi: {chat_title} ({chat_id})"))
            elif new_status in ["left", "kicked"]:
                ActiveChat.objects.filter(chat_id=str(chat_id)).delete()
                self.stdout.write(self.style.WARNING(f"❌ Bot guruh/kanaldan o'chirildi: {chat_title} ({chat_id})"))
                    
        # 2. Oddiy xabar kelganda (masalan, kimdir guruhda /start yozsa)
        elif "message" in update:
            chat_id = update["message"]["chat"]["id"]
            chat_title = update["message"]["chat"].get("title", update["message"]["chat"].get("first_name", str(chat_id)))
            
            obj, created = ActiveChat.objects.get_or_create(chat_id=str(chat_id), defaults={"title": chat_title})
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Bot yangi chatni qayd etdi: {chat_title} ({chat_id})"))
