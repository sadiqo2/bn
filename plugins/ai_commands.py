from pyrogram import Client, filters
from pyrogram.types import Message
from ai_handler import AIHandler
from database import Database

db = Database()
ai = AIHandler()

@Client.on_message(filters.command("ai") & filters.me)
async def cmd_ai(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("❌ الاستخدام: `/ai سؤالك هنا`")
    
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
        await processing_msg.edit_text(f"❌ خطأ: {str(e)[:100]}")

@Client.on_message(filters.command("toggle_ai") & filters.me)
async def cmd_toggle_ai(client: Client, message: Message):
    current = db.get_setting("ai_reply")
    db.set_setting("ai_reply", not current)
    await message.reply_text(f"🔄 تم {'تفعيل' if not current else 'تعطيل'} الذكاء الاصطناعي.")
