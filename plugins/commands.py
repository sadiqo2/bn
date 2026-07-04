from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from database import Database

db = Database()

@Client.on_message(filters.command("start") & filters.me)
async def cmd_start(client: Client, message: Message):
    await message.reply_text(f"🎉 **أهلاً بك في {Config.BOT_NAME}!**\nالبوت يعمل الآن بنظام الإضافات الجديد.")

@Client.on_message(filters.command("settings") & filters.me)
async def cmd_settings(client: Client, message: Message):
    settings = db.get_all_settings()
    text = f"""
⚙️ **الإعدادات الحالية:**
📝 الردود: {'✅' if settings.get('auto_reply') else '❌'}
🤖 AI: {'✅' if settings.get('ai_reply') else '❌'}
"""
    await message.reply_text(text)

@Client.on_message(filters.command("stats") & filters.me)
async def cmd_stats(client: Client, message: Message):
    stats = db.get_stats()
    await message.reply_text(f"📊 **إحصائياتك:**\n📨 الرسائل: {stats.get('total_messages', 0)}")
