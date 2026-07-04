import asyncio
import os
import sys
import subprocess
import importlib

# Fix for Android
asyncio.set_event_loop(asyncio.new_event_loop())

# ============================================================
# 🔧 AUTO-INSTALL
# ============================================================

def auto_install_requirements():
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        print("⚠️ ملف requirements.txt غير موجود")
        return

    print("📦 جاري التحقق من المكتبات...")
    with open(req_file, 'r') as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    missing = []
    for package in packages:
        pkg_name = package.split('==')[0].split('>=')[0].split('<')[0].strip()
        try:
            importlib.import_module(pkg_name.replace('-', '_'))
            print(f"  ✅ {pkg_name}")
        except ImportError:
            missing.append(package)
            print(f"  ❌ {pkg_name}")

    if missing:
        print(f"\n📥 جاري تنصيب {len(missing)} مكتبات...")
        for pkg in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])
                print(f"  ✅ {pkg.split('==')[0]}")
            except Exception as e:
                print(f"  ❌ {pkg}: {e}")
    else:
        print("\n✅ جميع المكتبات موجودة!")
    print("=" * 50)

auto_install_requirements()

# ============================================================
# 🤖 MAIN APP
# ============================================================

from config import Config

os.makedirs(Config.SESSIONS_DIR, exist_ok=True)
os.makedirs(Config.DATA_DIR, exist_ok=True)

# Check for SESSION_STRING
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()

print("=" * 50)
print("🤖 Smart UserBot - بوت تلغرام الذكي (وضع الحساب الشخصي)")
print("=" * 50)

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from handlers import *

if SESSION_STRING:
    print("🔑 Using SESSION_STRING mode")
    print(f"   Length: {len(SESSION_STRING)} chars")

    app = Client(
        "my_account",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        session_string=SESSION_STRING,
        device_model="SmartUserBot",
        app_version="2.0",
        system_version="PyroTGFork",
        lang_code="ar",
        max_concurrent_transmissions=5
    )
else:
    print("📁 Using session file mode (local)")
    print("📱 سجل دخولك باستخدام رقم هاتفك")

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

# Commands (مخصصة فقط لصاحب الحساب لضمان الحماية)
app.on_message(filters.command("start") & filters.me)(cmd_start)
app.on_message(filters.command("settings") & filters.me)(cmd_settings)
app.on_message(filters.command("toggle_auto") & filters.me)(cmd_toggle_auto)
app.on_message(filters.command("toggle_ai") & filters.me)(cmd_toggle_ai)
app.on_message(filters.command("toggle_reply_all") & filters.me)(cmd_toggle_reply_all)
app.on_message(filters.command("stats") & filters.me)(cmd_stats)
app.on_message(filters.command("ai") & filters.me)(cmd_ai)
app.on_message(filters.command("add_reply") & filters.me)(cmd_add_reply)
app.on_message(filters.command("remove_reply") & filters.me)(cmd_remove_reply)
app.on_message(filters.command("list_replies") & filters.me)(cmd_list_replies)
app.on_message(filters.command("help") & filters.me)(cmd_help)

# Messages (الرد على الآخرين)
app.on_message(filters.text & filters.private & ~filters.me)(handle_message)
app.on_message(filters.text & filters.group & reply_filter & ~filters.me)(handle_message)

if __name__ == "__main__":
    print("=" * 50)
    print("✅ جاري تشغيل البوت...")
    print("=" * 50)

    try:
        app.run()
    except KeyboardInterrupt:
        print("\n👋 تم إيقاف البوت")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
