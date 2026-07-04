import asyncio
import os
import importlib
import subprocess
import sys
from aiohttp import web

# Fix for Android/Termux
asyncio.set_event_loop(asyncio.new_event_loop())

from config import Config
from pyrogram import Client

os.makedirs(Config.SESSIONS_DIR, exist_ok=True)
os.makedirs(Config.DATA_DIR, exist_ok=True)
os.makedirs("plugins", exist_ok=True) # إنشاء مجلد الإضافات تلقائياً

# ==========================================
# 🌐 Web Dashboard Server (سيرفر لوحة التحكم)
# ==========================================
async def web_dashboard_handler(request):
    # حالياً صفحة بسيطة، بعدين تكدر تصممها بلغة الـ Front-end مالتك!
    html_content = f"""
    <html>
        <head><title>{Config.BOT_NAME} - لوحة التحكم</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>مرحباً بك في لوحة تحكم البوت!</h1>
            <p>سيرفر الويب يعمل بنجاح بالتزامن مع بوت التلكرام.</p>
            <p>سيتم ربط الإعدادات وقاعدة البيانات هنا قريباً.</p>
        </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', web_dashboard_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌐 Web Dashboard running on http://localhost:8080")

# ==========================================
# 🤖 Telegram Bot (الحساب الشخصي)
# ==========================================
print("=" * 50)
print(f"🤖 {Config.BOT_NAME} - وضع الحساب الشخصي (SQLite + Web + Plugins)")
print("=" * 50)

# تفعيل الإضافات الذكية من مجلد plugins
app = Client(
    name=os.path.join(Config.SESSIONS_DIR, "my_account"),
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    device_model="SmartUserBot",
    app_version="3.0",
    system_version="Pro",
    lang_code="ar",
    plugins=dict(root="plugins") # 👈 هنا فعلنا الإضافات!
)

async def main():
    # تشغيل سيرفر الويب
    await start_web_server()
    
    # تشغيل بوت التلكرام
    print("✅ جاري تشغيل البوت...")
    await app.start()
    
    # إبقاء السيرفر والبوت يعملان
    await pyrogram.idle()

if __name__ == "__main__":
    import pyrogram
    try:
        app.run(main())
    except KeyboardInterrupt:
        print("\n👋 تم إيقاف البوت والسيرفر")
