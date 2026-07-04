import os
# لغينا استدعاء ملف .env حتى ما يتداخل وي الإعدادات الجديدة

class Config:
    # Telegram API
    API_ID = 29528386
    API_HASH = "2e6bf629432f1dd91a06d77342482218"

    # AI API Keys (خلي مفتاح جروق هنا)
    GEMINI_API_KEY = "AQ.Ab8RN6Kc6FuS-RpY7-PXLQt_W4cfJPPcWtfn-r_MzlISNULwuQ"
    GROQ_API_KEY = "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"
    OPENROUTER_API_KEY = ""

    # إعدادات البوت
    BOT_NAME = "🤖 SmartBot"
    ADMIN_ID = 8892756167

    # إعدادات الذكاء الاصطناعي (أجبرناه على Groq بشكل مباشر)
    AI_ENABLED = True
    AI_PROVIDER = "groq"
    AI_MODEL = "llama3-8b-8192"

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
