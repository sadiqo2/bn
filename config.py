import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram API (من my.telegram.org)
    API_ID = int(os.getenv("API_ID", "12345"))
    API_HASH = os.getenv("API_HASH", "your_api_hash_here")

    # AI API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

    # إعدادات البوت
    BOT_NAME = os.getenv("BOT_NAME", "🤖 SmartBot")
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

    # إعدادات الذكاء الاصطناعي
    AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
    AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash")

    # إعدادات الردود
    AUTO_REPLY_ENABLED = True
    REPLY_DELAY = 2
    MAX_MESSAGE_LENGTH = 4096

    # إعدادات الحماية
    RATE_LIMIT = 20
    BLOCKED_USERS = []

    # مسارات الملفات
    DATA_DIR = "data"
    SESSIONS_DIR = "sessions"
