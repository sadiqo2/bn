import os

class Config:
    # Telegram API
    API_ID = 29528386
    API_HASH = "2e6bf629432f1dd91a06d77342482218"

    # AI API Keys (ضع مفتاح جروق هنا)
    GROQ_API_KEY = "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"

    # إعدادات البوت
    BOT_NAME = "🤖 SmartBot"
    ADMIN_ID = 8892756167

    # إعدادات الذكاء الاصطناعي (مثبت على Groq الخفيف والسريع)
    AI_ENABLED = True
    AI_PROVIDER = "groq"
    AI_MODEL = "llama-3.3-70b-versatile"  # نموذج خفيف وسريع جداً وممتاز للعربية

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
