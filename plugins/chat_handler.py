import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from database import Database
from ai_handler import AIHandler

db = Database()
ai = AIHandler()

# قفل ذكي لحماية قاعدة البيانات من التداخل السريع
db_lock = asyncio.Lock()

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

# دالة لتنفيذ عمليات الحفظ بالخلفية بالترتيب وبدون تداخل
async def background_db_tasks(chat_id, user_id, text, response):
    async with db_lock:
        # نجمع كل عمليات الحفظ بدالة وحدة ونشغلها بخيط (Thread) واحد
        def _save():
            db.add_to_history(chat_id, "user", text)
            db.add_to_history(chat_id, "assistant", response)
            db.increment_stat("ai_replies_sent", user_id)
        await asyncio.to_thread(_save)

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
            await message.reply_text(auto_response)
            
            # تحديث الإحصائيات بأمان بالخلفية
            async def update_stats():
                async with db_lock:
                    await asyncio.to_thread(db.increment_stat, "auto_replies_sent", user_id)
            asyncio.create_task(update_stats())
            return  
            
    # 2. الذكاء الاصطناعي السريع
    if settings.get("ai_reply", True):
        processing_msg = await message.reply_text("🤖 ...") 
        try:
            # جلب التاريخ بأمان
            async with db_lock:
                history = await asyncio.to_thread(db.get_chat_history, chat_id)
                
            response = await ai.get_response(text, history)
            await processing_msg.edit_text(f"🤖 {response}")
            
            # استدعاء دالة الحفظ المنظمة بالخلفية
            asyncio.create_task(background_db_tasks(chat_id, user_id, text, response))
        except Exception as e:
            await processing_msg.edit_text("❌ حدث خطأ في الاتصال.")
