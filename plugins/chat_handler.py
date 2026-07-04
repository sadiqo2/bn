import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from database import Database
from ai_handler import AIHandler

db = Database()
ai = AIHandler()

def is_target(_, __, message: Message) -> bool:
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

target_filter = filters.create(is_target)

@Client.on_message(filters.text & ~filters.me & target_filter)
async def handle_others(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text

    # فحص الإسكات السريع
    if db.get_setting(f"mute_{user_id}"):
        return
        
    settings = db.get_all_settings()
    
    # 1. الرد التلقائي الصاروخي
    if settings.get("auto_reply", True):
        auto_response = db.get_reply(text)
        if auto_response:
            # إرسال الرد فوراً بدون أي تأخير (انحذف الـ sleep)
            await message.reply_text(auto_response)
            
            # تسجيل الإحصائيات بالخلفية حتى ما يبطئ البوت
            asyncio.create_task(asyncio.to_thread(db.increment_stat, "auto_replies_sent", user_id))
            return  
            
    # 2. الذكاء الاصطناعي السريع
    if settings.get("ai_reply", True):
        # رسالة مؤقتة سريعة جداً
        processing_msg = await message.reply_text("🤖 ...") 
        try:
            # جلب الرد من الذكاء الاصطناعي
            history = await asyncio.to_thread(db.get_chat_history, chat_id)
            response = await ai.get_response(text, history)
            
            # تعديل الرسالة وعرض النتيجة فوراً
            await processing_msg.edit_text(f"🤖 {response}")
            
            # حفظ السجل بالخلفية (Background Tasks)
            asyncio.create_task(asyncio.to_thread(db.add_to_history, chat_id, "user", text))
            asyncio.create_task(asyncio.to_thread(db.add_to_history, chat_id, "assistant", response))
            asyncio.create_task(asyncio.to_thread(db.increment_stat, "ai_replies_sent", user_id))
        except Exception as e:
            await processing_msg.edit_text("❌ حدث خطأ في الاتصال.")
