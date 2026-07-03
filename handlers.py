import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType

from config import Config
from database import Database
from ai_handler import AIHandler
from keyboards import *

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
• ⚙️ إعدادات سهلة بالأزرار

🎯 **كيفية الاستخدام:**
• رد على أي رسالتي في المجموعات
• أو سوِّ تاك @username
• أو راسلني في الخاص

اضغط على الأزرار أدناه للبدء:
"""
    await message.reply_text(welcome_text, reply_markup=main_menu_keyboard())

async def cmd_settings(client: Client, message: Message):
    settings = db.get_all_settings()
    text = f"""
⚙️ **الإعدادات الحالية:**

📝 الردود التلقائية: {'✅' if settings['auto_reply'] else '❌'}
🤖 الذكاء الاصطناعي: {'✅' if settings['ai_reply'] else '❌'}
📢 الرد على الجميع: {'✅' if settings['reply_to_all'] else '❌'}
🌐 اللغة: {settings['language']}
"""
    await message.reply_text(text, reply_markup=settings_keyboard())

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
    await message.reply_text(text, reply_markup=stats_keyboard())

async def cmd_add_reply(client: Client, message: Message):
    args = message.text.split("\n", 2)
    if len(args) < 3:
        await message.reply_text(
            "❌ **الاستخدام:**\n"
            "`/add_reply`\n"
            "`الكلمة المفتاحية`\n"
            "`الرد التلقائي`",
            reply_markup=back_keyboard()
        )
        return
    keyword = args[1].strip()
    response = args[2].strip()
    if db.add_reply(keyword, response):
        await message.reply_text(
            f"✅ **تم إضافة الرد:**\n"
            f"🔑 الكلمة: `{keyword}`\n"
            f"💬 الرد: `{response[:50]}...`",
            reply_markup=back_keyboard()
        )
    else:
        await message.reply_text("❌ حدث خطأ", reply_markup=back_keyboard())

async def cmd_remove_reply(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text("❌ الاستخدام: `/remove_reply الكلمة`", reply_markup=back_keyboard())
        return
    keyword = args[1].strip()
    if db.remove_reply(keyword):
        await message.reply_text(f"✅ تم حذف الرد: `{keyword}`", reply_markup=back_keyboard())
    else:
        await message.reply_text("❌ الكلمة غير موجودة", reply_markup=back_keyboard())

async def cmd_list_replies(client: Client, message: Message):
    replies = db.get_all_replies()
    if not replies:
        await message.reply_text("📭 لا توجد ردود تلقائية", reply_markup=back_keyboard())
        return
    text = "📝 **الردود التلقائية:**\n\n"
    for i, (keyword, response) in enumerate(replies.items(), 1):
        text += f"{i}. 🔑 `{keyword}` → 💬 `{response[:30]}...`\n"
    await message.reply_text(text, reply_markup=auto_replies_keyboard())

async def cmd_ai(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text("❌ الاستخدام: `/ai سؤالك هنا`", reply_markup=back_keyboard())
        return
    query = args[1]
    processing_msg = await message.reply_text("🤖 **جاري التفكير...**")
    try:
        history = db.get_chat_history(message.chat.id)
        response = await ai.get_response(query, history)
        db.add_to_history(message.chat.id, "user", query)
        db.add_to_history(message.chat.id, "assistant", response)
        db.increment_stat("ai_replies_sent", message.from_user.id)
        await processing_msg.edit_text(
            f"🤖 **الذكاء الاصطناعي:**\n\n{response}",
            reply_markup=back_keyboard()
        )
    except Exception as e:
        await processing_msg.edit_text(f"❌ خطأ: {str(e)}", reply_markup=back_keyboard())

async def cmd_help(client: Client, message: Message):
    help_text = """
📚 **دليل الاستخدام:**

**الأوامر:**
• `/start` - القائمة الرئيسية
• `/settings` - الإعدادات
• `/stats` - الإحصائيات
• `/ai` سؤال - تحدث مع AI
• `/add_reply` - إضافة رد تلقائي
• `/remove_reply` كلمة - حذف رد
• `/list_replies` - قائمة الردود
• `/help` - هذا الدليل

**في المجموعات:**
• رد على رسالتي ← يرد
• سوِّ تاك @username ← يرد
• رسالة عادية ← **ما يرد**

**في الخاص:**
• يرد على كل الرسائل تلقائياً
"""
    await message.reply_text(help_text, reply_markup=back_keyboard())

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
            await message.reply_text(
                auto_response,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🤖 اسأل AI", callback_data=f"ask_ai_{message.id}")]
                ])
            )
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
            await processing_msg.edit_text(
                f"🤖 {response}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 إعادة المحاولة", callback_data=f"retry_ai_{message.id}")],
                    [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")]
                ])
            )
        except Exception as e:
            await processing_msg.edit_text(f"❌ عذراً، حدث خطأ: {str(e)[:100]}")

async def handle_callback(client: Client, callback: CallbackQuery):
    data = callback.data
    if data == "main_menu":
        await callback.message.edit_text(
            "🎛️ **القائمة الرئيسية**\n\nاختر ما تريد:",
            reply_markup=main_menu_keyboard()
        )
    elif data == "settings":
        settings = db.get_all_settings()
        text = f"""
⚙️ **الإعدادات:**

📝 الردود التلقائية: {'✅' if settings['auto_reply'] else '❌'}
🤖 الذكاء الاصطناعي: {'✅' if settings['ai_reply'] else '❌'}
📢 الرد على الجميع: {'✅' if settings['reply_to_all'] else '❌'}
🌐 اللغة: `{settings['language']}`
"""
        await callback.message.edit_text(text, reply_markup=settings_keyboard())
    elif data == "toggle_auto_reply":
        current = db.get_setting("auto_reply")
        db.set_setting("auto_reply", not current)
        await handle_callback(client, callback)
    elif data == "toggle_ai":
        current = db.get_setting("ai_reply")
        db.set_setting("ai_reply", not current)
        await handle_callback(client, callback)
    elif data == "toggle_reply_all":
        current = db.get_setting("reply_to_all")
        db.set_setting("reply_to_all", not current)
        await handle_callback(client, callback)
    elif data == "auto_replies":
        await callback.message.edit_text(
            "📝 **إدارة الردود التلقائية**\n\n"
            "يمكنك إضافة، حذف، أو عرض الردود:",
            reply_markup=auto_replies_keyboard()
        )
    elif data == "add_reply":
        await callback.message.edit_text(
            "➕ **إضافة رد تلقائي**\n\n"
            "أرسل الآن بالصيغة التالية:\n"
            "`/add_reply`\n"
            "`الكلمة المفتاحية`\n"
            "`الرد التلقائي`",
            reply_markup=back_keyboard()
        )
    elif data == "list_replies":
        replies = db.get_all_replies()
        if not replies:
            text = "📭 لا توجد ردود تلقائية"
        else:
            text = "📝 **الردود التلقائية:**\n\n"
            for i, (k, v) in enumerate(replies.items(), 1):
                text += f"{i}. `{k}` → `{v[:40]}`\n"
        await callback.message.edit_text(text, reply_markup=auto_replies_keyboard())
    elif data == "delete_reply":
        await callback.message.edit_text(
            "🗑️ **حذف رد تلقائي**\n\n"
            "أرسل الآن:\n`/remove_reply الكلمة_المفتاحية`",
            reply_markup=back_keyboard()
        )
    elif data == "stats":
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
        await callback.message.edit_text(text, reply_markup=stats_keyboard())
    elif data == "general_stats":
        await handle_callback(client, callback)
    elif data == "daily_stats":
        stats = db.get_stats()
        daily = stats.get("daily_stats", {})
        text = "📅 **إحصائيات يومية (آخر 7 أيام):**\n\n"
        for date, data in list(daily.items())[-7:]:
            text += f"📆 `{date}`: 📨 {data.get('messages', 0)} | 💬 {data.get('replies', 0)}\n"
        await callback.message.edit_text(text, reply_markup=stats_keyboard())
    elif data == "user_stats":
        stats = db.get_stats()
        users = stats.get("user_stats", {})
        text = "👥 **أكثر المستخدمين تفاعلاً:**\n\n"
        sorted_users = sorted(users.items(), key=lambda x: x[1].get("messages", 0), reverse=True)[:10]
        for uid, data in sorted_users:
            text += f"🆔 `{uid}`: 📨 {data.get('messages', 0)}\n"
        await callback.message.edit_text(text, reply_markup=stats_keyboard())
    elif data == "refresh_stats":
        await handle_callback(client, callback)
    elif data == "ai_settings":
        await callback.message.edit_text(
            f"""
🤖 **إعدادات الذكاء الاصطناعي:**

المزود الحالي: `{Config.AI_PROVIDER}`
النموذج: `{Config.AI_MODEL}`
الحالة: {'✅ مفعل' if Config.AI_ENABLED else '❌ معطل'}
""",
            reply_markup=ai_settings_keyboard()
        )
    elif data == "change_provider":
        await callback.message.edit_text(
            "🔄 **اختر المزود:**\n\n"
            "1. Google Gemini (مجاني)\n"
            "2. Groq (سريع)\n"
            "3. OpenRouter (متعدد النماذج)\n\n"
            "عدل `AI_PROVIDER` في ملف `.env`",
            reply_markup=back_keyboard()
        )
    elif data == "test_ai":
        processing = await callback.message.edit_text("🤖 **جاري الاختبار...**")
        try:
            response = await ai.get_response("مرحباً! قدم نفسك باختصار")
            await processing.edit_text(
                f"✅ **اختبار ناجح!**\n\n{response}",
                reply_markup=ai_settings_keyboard()
            )
        except Exception as e:
            await processing.edit_text(
                f"❌ **فشل الاختبار:**\n`{str(e)[:200]}`",
                reply_markup=ai_settings_keyboard()
            )
    elif data == "help":
        await callback.message.edit_text(
            """
📚 **المساعدة:**

**الأوامر:**
• `/start` - القائمة الرئيسية
• `/settings` - الإعدادات
• `/stats` - الإحصائيات
• `/ai` سؤال - تحدث مع AI
• `/add_reply` - إضافة رد تلقائي
• `/remove_reply` كلمة - حذف رد
• `/list_replies` - قائمة الردود

**ملاحظات:**
• في المجموعات يرد فقط على الرد/التاك
• في الخاص يرد على كل الرسائل
• يدعم 3 مزودين للذكاء الاصطناعي
""",
            reply_markup=back_keyboard()
        )
    elif data.startswith("ask_ai_"):
        await callback.answer("🤖 استخدم الأمر /ai للسؤال", show_alert=True)
    elif data.startswith("retry_ai_"):
        await callback.answer("🔄 جاري إعادة المحاولة...")
    await callback.answer()
