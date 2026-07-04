import logging
from pyrogram import Client, filters

_tracker_started = False

# كلاس مخصص لصيد أخطاء النظام وتحويلها لرسائل تلكرام
class TelegramErrorHandler(logging.Handler):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def emit(self, record):
        # نريد بس الأخطاء القوية (ERROR أو CRITICAL) اللي توكف الأوامر
        if record.levelno < logging.ERROR:
            return
            
        try:
            # ترتيب شكل رسالة الخطأ
            log_text = self.format(record)
            
            # نغلس على أخطاء الشبكة والاتصال العادية مال Railway حتى لا يدوخك ويزعجك
            if "Connection" in log_text or "Timeout" in log_text or "Network" in log_text:
                return
            
            # إرسال الخطأ للرسائل المحفوظة (me)
            # القص [-3900:] حتى نتجنب تجاوز الحد الأقصى لطول الرسالة بالتلكرام
            self.client.loop.create_task(
                self.client.send_message("me", f"⚠️ **صائد الأخطاء (Bug Tracker):**\n\n`{log_text[-3900:]}`")
            )
        except Exception:
            pass

# group=-10 يعني هذا الكود يشتغل أول واحد بالبوت حتى يصيد الأخطاء من البداية
@Client.on_message(group=-10)
async def start_error_tracker(client: Client, message):
    global _tracker_started
    # نأكد إن الصائد يشتغل مرة وحدة بس أول ما البوت يستلم رسالة
    if _tracker_started:
        return
        
    _tracker_started = True
    
    # نجهز الصائد
    tg_handler = TelegramErrorHandler(client)
    tg_handler.setFormatter(logging.Formatter('ملف الخطأ: %(filename)s\nالرسالة: %(message)s'))
    
    # نربطه بمكتبة التلكرام (Pyrogram) وبأساس البايثون
    logging.getLogger("pyrogram").addHandler(tg_handler)
    logging.getLogger().addHandler(tg_handler)
    
    # رسالة تأكيد تندز مرة وحدة بس من يشتغل البوت
    try:
        await client.send_message("me", "✅ **تم تفعيل صائد الأخطاء!**\nأي خطأ برمجي يصير بالبوت راح يوصلك هنا للرسائل المحفوظة.")
    except:
        pass
