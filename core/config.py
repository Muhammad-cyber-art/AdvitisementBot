import os

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8034710652:AAG4sQ9mkHddhpjLyZGhmj6VYOaKqFw4B2k")
    
    # Endi statik kanal ID kerak emas. Bot qo'shilgan joylarni o'zi saqlab boradi.
    ACTIVE_CHATS_FILE = os.getenv("ACTIVE_CHATS_FILE", "active_chats.json")
    
    # Scheduling configurations
    POSTS_PER_DAY = int(os.getenv("POSTS_PER_DAY", "15"))
    POSTING_WINDOW_START_HOUR = int(os.getenv("POSTING_WINDOW_START_HOUR", "9")) # 09:00
    POSTING_WINDOW_END_HOUR = int(os.getenv("POSTING_WINDOW_END_HOUR", "21"))   # 21:00
    
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Tashkent")
    
    # -------------------------------------
    # Tizimni test qilish uchun (har 1 daqiqada post)
    # -------------------------------------
    TEST_MODE = True  # Original holatga qaytarish uchun buni False qilib qo'ying
