import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from config import Config
from database import Database
from ai_handler import AIHandler

db = Database()
ai = AIHandler()

def is_reply_to_me_or_mention(_, __, message: Message) -> bool:
    if not message or not message.from_user:
        return False
    if message.chat.type == ChatType.PRIVATE:
        return True
    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_self:
            return True
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                return True
    return False

reply_filter = filters.create(is_reply_to_me_or_mention)

async def cmd_start(client: Client, message: Message):
    welcome_text = f"""
🎉 **أهلاً بك في {Config.BOT_NAME}!**

أنا بوت ذكي يعمل على حسابك الشخصي في تلغرام.

📌 **المميزات:**
• 🤖 ذكاء اصطناعي متقدم
• 📝 ردود تلقائية قابلة للتخصيص
• 📊 إحصائيات كاملة

🎯 **الأوامر المتاحة:**
• `/settings` - عرض الإعدادات
• `/stats` - عرض الإحصائيات
• `/ai سؤال` - التحدث مع الذكاء الاصطناعي
• `/add_reply كلمة رد` - إضافة رد تلقائي
• `/list_replies` - عرض الردود التلقائية
• `/remove_reply كلمة` - حذف رد تلقائي
• `/help` - دليل الاستخدام الشامل
"""
    await message.reply_text(welcome_text)

async def cmd_settings(client: Client, message: Message):
    settings = db.get_all_settings()
    
    # استخدام .get() لتجنب الأخطاء في حال كانت الإعدادات ناقصة بملف الـ JSON
    auto_reply = settings.get('auto_reply', True)
    ai_reply = settings.get('ai_reply', True)
    reply_to_all = settings.get('reply_to_all', False)
    lang = settings.get('language', 'ar')

    text = f"""
⚙️ **الإعدادات الحالية:**

📝 الردود التلقائية: {'✅' if auto_reply else '❌'} (للتغيير: /toggle_auto)
🤖 الذكاء الاصطناعي: {'✅' if ai_reply else '❌'} (للتغيير: /toggle_ai)
📢 الرد على الجميع بالكروبات: {'✅' if reply_to_all else '❌'} (للتغيير: /toggle_reply_all)
🌐 اللغة: {lang}
"""
    await message.reply_text(text)

async def cmd_toggle_auto(client: Client, message: Message):
    current = db.get_setting("auto_reply")
    db.set_setting("auto_reply", not current)
    await message.reply_text(f"🔄 تم {'تفعيل' if not current else 'تعطيل'} الردود التلقائية.")

async def cmd_toggle_ai(client: Client, message: Message):
    current = db.get_setting("ai_reply")
    db.set_setting("ai_reply", not current)
    await message.reply_text(f"🔄 تم {'تفعيل' if not current else 'تعطيل'} الذكاء الاصطناعي.")

async def cmd_toggle_reply_all(client: Client, message: Message):
    current = db.get_setting("reply_to_all")
    db.set_setting("reply_to_all", not current)
    await message.reply_text(f"🔄 تم {'تفعيل' if not current else 'تعطيل'} الرد على الجميع في المجموعات.")

async def cmd_stats(client: Client, message: Message):
    stats = db.get_stats()
    uptime = datetime.now() - datetime.fromisoformat(stats['start_time'])
    text = f"""
📊 **الإحصائيات:**

📨 إجمالي الرسائل: `{stats['total_messages']}`
🤖 ردود تلقائية: `{stats['auto_replies_sent']}`
🧠 ردود AI: `{stats['ai_replies_sent']}`
👥 مجموعات: `{stats['groups_handled']}`
💬 محادثات خاصة: `{stats['private_chats']}`
⏱️ وقت التشغيل: `{str(uptime).split('.')[0]}`
"""
    await message.reply_text(text)

async def cmd_add_reply(client: Client, message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply_text(
            "❌ **الاستخدام الخاطئ!**\n"
            "اكتب الأمر بهذا الشكل:\n"
            "`/add_reply الكلمة الرد`\n"
            "مثال: `/add_reply هلو هلا بيك نورت`"
        )
        return
    keyword = args[1].strip()
    response = args[2].strip()
    if db.add_reply(keyword, response):
        await message.reply_text(
            f"✅ **تم إضافة الرد بنجاح:**\n"
            f"🔑 الكلمة: `{keyword}`\n"
            f"💬 الرد: `{response[:50]}`"
        )
    else:
        await message.reply_text("❌ حدث خطأ أثناء إضافة الرد")

async def cmd_remove_reply(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text("❌ الاستخدام: `/remove_reply الكلمة`")
        return
    keyword = args[1].strip()
    if db.remove_reply(keyword):
        await message.reply_text(f"✅ تم حذف الرد الخاص بكلمة: `{keyword}`")
    else:
        await message.reply_text("❌ الكلمة غير موجودة في الردود التلقائية.")

async def cmd_list_replies(client: Client, message: Message):
    replies = db.get_all_replies()
    if not replies:
        await message.reply_text("📭 لا توجد ردود تلقائية مسجلة حالياً.")
        return
    text = "📝 **الردود التلقائية:**\n\n"
    for i, (keyword, response) in enumerate(replies.items(), 1):
        text += f"{i}. 🔑 `{keyword}` → 💬 `{response[:30]}...`\n"
    await message.reply_text(text)

async def cmd_ai(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text("❌ الاستخدام: `/ai سؤالك هنا`")
        return
    query = args[1]
    processing_msg = await message.reply_text("🤖 **جاري التفكير...**")
    try:
        history = db.get_chat_history(message.chat.id)
        response = await ai.get_response(query, history)
        db.add_to_history(message.chat.id, "user", query)
        db.add_to_history(message.chat.id, "assistant", response)
        db.increment_stat("ai_replies_sent", message.from_user.id)
        await processing_msg.edit_text(f"🤖 **الذكاء الاصطناعي:**\n\n{response}")
    except Exception as e:
        await processing_msg.edit_text(f"❌ خطأ: {str(e)}")

async def cmd_help(client: Client, message: Message):
    help_text = """
📚 **دليل الاستخدام:**

**الأوامر الأساسية:**
• `/start` - القائمة الرئيسية
• `/settings` - عرض الإعدادات
• `/stats` - الإحصائيات
• `/ai سؤال` - تحدث مع الذكاء الاصطناعي

**أوامر الإعدادات:**
• `/toggle_auto` - تفعيل/تعطيل الردود التلقائية
• `/toggle_ai` - تفعيل/تعطيل الذكاء الاصطناعي
• `/toggle_reply_all` - تفعيل/تعطيل الرد على الجميع بالكروبات

**أوامر الردود التلقائية:**
• `/add_reply كلمة رد` - إضافة رد تلقائي
• `/remove_reply كلمة` - حذف رد
• `/list_replies` - قائمة الردود

**كيف يعمل البوت؟**
• في المجموعات: يرد إذا تم الرد على رسالتك أو تم الإشارة إليك (@)، ما لم تقم بتفعيل (الرد على الجميع).
• في الخاص: يرد على كل الرسائل تلقائياً.
"""
    await message.reply_text(help_text)

async def handle_message(client: Client, message: Message):
    if not message or not message.text:
        return
    if message.from_user and message.from_user.is_self:
        return
    db.increment_stat("total_messages", message.from_user.id if message.from_user else None)
    settings = db.get_all_settings()
    
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        is_target = False
        if message.reply_to_message and message.reply_to_message.from_user:
            if message.reply_to_message.from_user.is_self:
                is_target = True
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    is_target = True
                    break
        if not is_target and not settings.get("reply_to_all", False):
            return
            
    if settings.get("auto_reply", True):
        auto_response = db.get_reply(message.text)
        if auto_response:
            await asyncio.sleep(Config.REPLY_DELAY)
            await message.reply_text(auto_response)
            db.increment_stat("auto_replies_sent", message.from_user.id if message.from_user else None)
            return
            
    if settings.get("ai_reply", True):
        processing_msg = await message.reply_text("🤖 **جاري التفكير...**")
        try:
            history = db.get_chat_history(message.chat.id)
            response = await ai.get_response(message.text, history)
            db.add_to_history(message.chat.id, "user", message.text)
            db.add_to_history(message.chat.id, "assistant", response)
            db.increment_stat("ai_replies_sent", message.from_user.id if message.from_user else None)
            await processing_msg.edit_text(f"🤖 {response}")
        except Exception as e:
            await processing_msg.edit_text(f"❌ عذراً، حدث خطأ: {str(e)[:100]}")
