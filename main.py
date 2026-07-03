import os
from pyrogram import Client, filters
from pyrogram.enums import ChatType

from config import Config
from handlers import *

os.makedirs(Config.SESSIONS_DIR, exist_ok=True)
os.makedirs(Config.DATA_DIR, exist_ok=True)

app = Client(
    name=os.path.join(Config.SESSIONS_DIR, "my_account"),
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    device_model="SmartUserBot",
    app_version="2.0",
    system_version="PyroTGFork",
    lang_code="ar",
    max_concurrent_transmissions=5
)

# الأوامر
app.on_message(filters.command("start") & filters.private)(cmd_start)
app.on_message(filters.command("settings"))(cmd_settings)
app.on_message(filters.command("stats"))(cmd_stats)
app.on_message(filters.command("ai"))(cmd_ai)
app.on_message(filters.command("add_reply"))(cmd_add_reply)
app.on_message(filters.command("remove_reply"))(cmd_remove_reply)
app.on_message(filters.command("list_replies"))(cmd_list_replies)
app.on_message(filters.command("help"))(cmd_help)

# الرسائل
app.on_message(filters.text & filters.private & ~filters.me)(handle_message)
app.on_message(filters.text & filters.group & reply_filter & ~filters.me)(handle_message)

# الأزرار
app.on_callback_query()(handle_callback)

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Smart UserBot - بوت تلغرام الذكي")
    print("=" * 50)
    print("✅ جاري تشغيل البوت...")
    print("📱 سجل دخولك باستخدام رقم هاتفك")
    print("⏳ انتظر كود التحقق...")
    print("=" * 50)
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n👋 تم إيقاف البوت")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
