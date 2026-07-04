import os
import time
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database

db = Database()
start_time = time.time()

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
• `اسكات` / `ميوت` : كتم الشخص (تنحذف رسائله من الطرفين فوراً).
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
• `/stats` : عرض إحصائيات البوت واستهلاك السيرفر.
• `/help` : عرض هذه القائمة.
"""
    await client.send_message("me", help_text)

# -----------------------------------------
# الإحصائيات الشاملة واستخدام النظام (/stats)
# -----------------------------------------
def get_readable_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return f"{d}يوم {h}ساعة {m}دقيقة"

@Client.on_message(filters.command("stats", prefixes="/") & filters.me)
async def stats_command(client: Client, message: Message):
    processing = await message.reply_text("⏳ جاري سحب الإحصائيات...")
    
    # حساب وقت تشغيل البوت (Uptime)
    uptime = int(time.time() - start_time)
    uptime_str = get_readable_time(uptime)
    
    # استهلاك السيرفر (Railway)
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    ram_used_mb = ram.used / (1024 * 1024)
    ram_total_mb = ram.total / (1024 * 1024)
    
    # جلب إحصائيات قاعدة البيانات (الرسائل والردود)
    ai_replies = db.get_setting("ai_replies_sent") or "0"
    auto_replies = db.get_setting("auto_replies_sent") or "0"
    
    stats_text = f"""
📊 **إحصائيات النظام الشاملة** 📊

⏱ **وقت التشغيل (Uptime):** `{uptime_str}`

💻 **استهلاك السيرفر (Railway):**
• **المعالج (CPU):** `{cpu_usage}%` 🎛
• **الذاكرة (RAM):** `{ram_usage}%` 🧠
• **المستخدم:** `{ram_used_mb:.1f} MB` من `{ram_total_mb:.1f} MB`

🤖 **نشاط البوت:**
• **ردود الذكاء الاصطناعي:** `{ai_replies}` رسالة
• **الردود التلقائية:** `{auto_replies}` رسالة

📂 **حالة التخزين:** `مستقر (Volume Mounted) ✅`
"""
    await processing.edit_text(stats_text)
