import aiohttp
import asyncio
import logging
import json
import os
from publishers.base import BasePublisher

logger = logging.getLogger(__name__)

class TelegramPublisher(BasePublisher):
    def __init__(self, bot_token: str, chats_file: str = "active_chats.json"):
        self.bot_token = bot_token
        self.chats_file = chats_file
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.active_chats = self._load_chats()

    def _load_chats(self) -> set:
        """Fayldan aktiv chat/kanallar ro'yxatini o'qiydi."""
        if os.path.exists(self.chats_file):
            try:
                with open(self.chats_file, "r") as f:
                    return set(json.load(f))
            except Exception as e:
                logger.error(f"Failed to load chats from {self.chats_file}: {e}")
        return set()

    def _save_chats(self):
        """Aktiv chatlarni faylga saqlaydi."""
        try:
            with open(self.chats_file, "w") as f:
                json.dump(list(self.active_chats), f)
        except Exception as e:
            logger.error(f"Failed to save chats: {e}")

    async def _process_update(self, update: dict):
        """Telegramdan kelgan yangilanishni tahlil qiladi va yangi chatlarni qo'shadi."""
        chat_id = None
        chat_title = "Unknown"
        
        # 1. Bot kanalga qo'shilganda yoki huquqlari o'zgarganda (my_chat_member)
        if "my_chat_member" in update:
            chat_id = update["my_chat_member"]["chat"]["id"]
            chat_title = update["my_chat_member"]["chat"].get("title", chat_id)
            new_status = update["my_chat_member"]["new_chat_member"]["status"]
            
            if new_status in ["administrator", "member"]:
                if chat_id not in self.active_chats:
                    self.active_chats.add(chat_id)
                    self._save_chats()
                    logger.info(f"✅ Bot yangi guruh/kanalga qo'shildi: {chat_title} ({chat_id})")
            elif new_status in ["left", "kicked"]:
                if chat_id in self.active_chats:
                    self.active_chats.remove(chat_id)
                    self._save_chats()
                    logger.info(f"❌ Bot guruh/kanaldan o'chirildi: {chat_title} ({chat_id})")
                    
        # 2. Oddiy xabar kelganda (masalan, kimdir guruhda /start yozsa)
        elif "message" in update:
            chat_id = update["message"]["chat"]["id"]
            chat_title = update["message"]["chat"].get("title", update["message"]["chat"].get("first_name", chat_id))
            
            # Agar bot endigina xabar olayotgan bo'lsa va ro'yxatda yo'q bo'lsa
            if chat_id not in self.active_chats:
                self.active_chats.add(chat_id)
                self._save_chats()
                logger.info(f"✅ Bot yangi chatni qayd etdi: {chat_title} ({chat_id})")

    async def start_polling(self):
        """Botni uzoq muddatli so'rovlar (long-polling) rejimida ishlatadi."""
        if self.bot_token == "YOUR_TELEGRAM_BOT_TOKEN":
            logger.warning("Bot token berilmagan, polling ishga tushmaydi.")
            return

        logger.info("Telegram Polling ishga tushdi. Bot qayerga qo'shilsa kuzatib boradi...")
        offset = 0
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    url = f"{self.api_url}/getUpdates?timeout=30&offset={offset}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            for update in data.get("result", []):
                                offset = update["update_id"] + 1
                                await self._process_update(update)
                        else:
                            await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"Polling error: {e}")
                    await asyncio.sleep(5)

    async def publish(self, content: str, photo: str = None, chat_ids: list = None) -> bool:
        """Barcha aktiv chatlarga xabarni yuboradi (va agar rasm bo'lsa rasmni ham)."""
        target_chats = chat_ids if chat_ids is not None else list(self.active_chats)

        if not target_chats:
            logger.warning("Hozircha hech qanday kanal yoki guruh yo'q! Hech qayerga yuborilmaydi.")
            return False

        success_count = 0
        async with aiohttp.ClientSession() as session:
            for chat_id in target_chats:
                if photo:
                    endpoint = f"{self.api_url}/sendPhoto"
                    if str(photo).startswith("http://") or str(photo).startswith("https://"):
                        payload = {
                            "chat_id": chat_id,
                            "caption": content,
                            "parse_mode": "HTML",
                            "photo": photo
                        }
                        kwargs = {"json": payload}
                    else:
                        data = aiohttp.FormData()
                        data.add_field("chat_id", str(chat_id))
                        data.add_field("caption", content)
                        data.add_field("parse_mode", "HTML")
                        # Faylni ob'yekt ko'rinishida qo'shamiz
                        data.add_field("photo", open(photo, "rb"))
                        kwargs = {"data": data}
                else:
                    endpoint = f"{self.api_url}/sendMessage"
                    payload = {
                        "chat_id": chat_id,
                        "text": content,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True
                    }
                    kwargs = {"json": payload}
                    
                try:
                    async with session.post(endpoint, **kwargs) as response:
                        if response.status == 200:
                            success_count += 1
                        elif response.status in [403, 400]:
                            # Bot kanaldan chiqarib yuborilgan yoki chat o'chirilgan
                            logger.warning(f"Bot {chat_id} dan o'chirilgan ko'rinadi.")
                            # Agar chat_ids berilmagan bo'lsa, o'zining json faylidan o'chiradi
                            if chat_ids is None:
                                self.active_chats.discard(chat_id)
                                self._save_chats()
                except Exception as e:
                    logger.error(f"Exception sending to {chat_id}: {e}")
        
        logger.info(f"E'lon {success_count}/{len(target_chats)} ta chatga yuborildi.")
        return success_count > 0
