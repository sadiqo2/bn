import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from database import Database
from ai_handler import AIHandler

db = Database()
ai = AIHandler()

# فلتر ذكي: يحدد إذا الرسالة بالخاص، أو رد على رسالتك، أو تاك إلك بالكروب
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

# يشتغل على رسائل الآخرين فقط (~filters.me)
@Client.on_message(filters.text & ~filters.me & target_filter)
async def handle_others(client: Client, message: Message):
    # 🛑 التعديل الجديد: فحص الإسكات قبل كل شيء
    # إذا كان الشخص مسكت (Muted)، توقف فوراً ولا تكمل الكود
    if db.get_setting(f"mute_{message.from_user.id}"):
        return
        
    settings = db.get_all_settings()
    
    # 1. فحص الردود التلقائية أولاً
    if settings.get("auto_reply", True):
        auto_response = db.get_reply(message.text)
        if auto_response:
            await asyncio.sleep(2)
            await message.reply_text(auto_response)
            db.increment_stat("auto_replies_sent", message.from_user.id)
            return  
            
    # 2. إذا ماكو رد تلقائي، يجاوب بالذكاء الاصطناعي
    if settings.get("ai_reply", True):
        processing_msg = await message.reply_text("🤖 **جاري التفكير...**")
        try:
            history = db.get_chat_history(message.chat.id)
            response = await ai.get_response(message.text, history)
            db.add_to_history(message.chat.id, "user", message.text)
            db.add_to_history(message.chat.id, "assistant", response)
            db.increment_stat("ai_replies_sent", message.from_user.id)
            await processing_msg.edit_text(f"🤖 {response}")
        except Exception as e:
            await processing_msg.edit_text(f"❌ عذراً، حدث خطأ: {str(e)[:100]}")
