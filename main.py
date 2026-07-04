import asyncio
import os
from aiohttp import web
from config import Config
from pyrogram import Client

# تفعيل الإضافات
app = Client(
    "my_account",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=os.getenv("SESSION_STRING"), # يجب وضع الـ SESSION_STRING في متغيرات البيئة في Railway
    plugins=dict(root="plugins")
)

async def web_dashboard_handler(request):
    return web.Response(text="<h1>Bot is running!</h1>", content_type='text/html')

async def start_web_server():
    app_web = web.Application()
    app_web.router.add_get('/', web_dashboard_handler)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()

async def main():
    await start_web_server()
    print("✅ البوت يعمل الآن على Railway")
    await app.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    app.run(main())
