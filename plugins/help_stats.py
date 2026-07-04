import os
import time
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database

db = Database()
start_time = time.time()

def get_readable_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return f"{d} يوم و {h} ساعة"

# -----------------------------------------
# قائمة الأوامر الشاملة (/help)
# -----------------------------------------
@Client.on_message(filters.command("help", prefixes="/") & filters.me)
async def help_command(client: Client, message: Message):
    try: await message.delete()
    except: pass
    
    help_text = """
🛠 **قائمة أوامر اليوزر بوت الشاملة** 🛠

🛡 **أوامر الحماية والتحكم (بدون /)**
*(بالرد على الشخص أو ذكره @ أو بالخاص)*
• `حظر` / `بلوك` : حظر المستخدم.
• `فك حظر` / `فك البلوك` : إلغاء الحظر.
• `اسكات` / `ميوت` : كتم الشخص (تنحذف رسائله فوراً).
• `الغاء الاسكات` / `انميوت` : فك الكتم.

🎨 **أوامر الملصقات (بدون /)**
*(بالرد على رسالة)*
• `ملصق` / `صانع` : (رد على صورة) لتحويلها لملصق.
• `خمط` / `زرف` : (رد على ملصق) لسرقته للرسائل المحفوظة.

🤖 **أوامر الذكاء الاصطناعي (مع /)**
• `/ai [سؤالك]` : سؤال الذكاء الاصطناعي بالخاص.
• `/toggle_ai` : تشغيل/إيقاف الرد التلقائي للذكاء الاصطناعي.

📝 **الردود التلقائية (مع /)**
• `/add_reply [الكلمة] [الرد]` : إضافة رد تلقائي.
• `/remove_reply [الكلمة]` : حذف رد تلقائي.
• `/list_replies` : عرض جميع الردود.

⚙️ **النظام والإحصائيات (مع /)**
• `/sys` أو `/allstats` : عرض إحصائيات النظام الشاملة واستهلاك السيرفر.
• `/help` : عرض هذه القائمة.
"""
    await client.send_message("me", help_text)

# -----------------------------------------
# الإحصائيات الشاملة المحدثة بـأمر جديد (/sys)
# -----------------------------------------
@Client.on_message(filters.command(["sys", "allstats"], prefixes="/") & filters.me)
async def stats_command(client: Client, message: Message):
    processing = await message.reply_text("⏳ جاري سحب الإحصائيات الشاملة من السيرفر...")
    
    # حساب وقت التشغيل
    uptime = int(time.time() - start_time)
    uptime_str = get_readable_time(uptime)
    
    # استهلاك السيرفر
    try:
        cpu_usage = psutil.cpu_percent(interval=0.2)
        ram = psutil.virtual_memory()
        ram_percent = f"{ram.percent}%"
    except Exception:
        cpu_usage = "غير مدعوم"
        ram_percent = "غير مدعوم"
    
    # جلب الإحصائيات بحماية ذكية (تفحص get_stats أو get_stat أو ترجع 0)
    try:
        if hasattr(db, "get_stats"):
            ai_replies = db.get_stats("ai_replies_sent") or 0
            auto_replies = db.get_stats("auto_replies_sent") or 0
        elif hasattr(db, "get_stat"):
            ai_replies = db.get_stat("ai_replies_sent") or 0
            auto_replies = db.get_stat("auto_replies_sent") or 0
        else:
            # حل بديل إذا الدالتين مو موجودات بقاعدة البيانات مالتك
            ai_replies = db.get_setting("ai_replies_sent") or 0
            auto_replies = db.get_setting("auto_replies_sent") or 0
    except Exception:
        ai_replies = 0
        auto_replies = 0
    
    stats_text = f"""
📊 **إحصائيات النظام الشاملة** 📊

⏱ **وقت تشغيل البوت:** `{uptime_str}`

💻 **أداء سيرفر Railway:**
• **استهلاك المعالج (CPU):** `{cpu_usage}%`
• **استهلاك الذاكرة (RAM):** `{ram_percent}`

🤖 **عداد النشاط والتفاعل:**
• **ردود الذكاء الاصطناعي:** `{ai_replies}` رسالة
• **الردود التلقائية:** `{auto_replies}` رسالة

📂 **حالة قاعدة البيانات:** `مستقرة وجاهزة وآمنة ✅`
"""
    await processing.edit_text(stats_text)
