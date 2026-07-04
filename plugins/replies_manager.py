from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database

db = Database()

@Client.on_message(filters.command("add_reply") & filters.me)
async def cmd_add_reply(client: Client, message: Message):
    try: await message.delete() 
    except: pass
    
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        return await message.reply_text("❌ الصيغة الخاطئة! استخدم: `/add_reply الكلمة الرد`")
        
    keyword = args[1].strip()
    response = args[2].strip()
    db.add_reply(keyword, response)
    await message.reply_text(f"✅ **تم إضافة الرد بنجاح:**\n🔑 الكلمة: `{keyword}`\n💬 الرد: `{response}`")

@Client.on_message(filters.command("remove_reply") & filters.me)
async def cmd_remove_reply(client: Client, message: Message):
    try: await message.delete() 
    except: pass
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("❌ الاستخدام: `/remove_reply الكلمة`")
        
    keyword = args[1].strip()
    if db.remove_reply(keyword):
        await message.reply_text(f"✅ تم حذف الرد لـ: `{keyword}`")
    else:
        await message.reply_text("❌ الكلمة غير موجودة في قائمة الردود.")

@Client.on_message(filters.command("list_replies") & filters.me)
async def cmd_list_replies(client: Client, message: Message):
    try: await message.delete() 
    except: pass
    
    replies = db.get_all_replies()
    if not replies:
        return await message.reply_text("📭 لا توجد ردود تلقائية مسجلة حالياً.")
        
    text = "📝 **الردود التلقائية المضافة:**\n\n"
    for i, (k, v) in enumerate(replies.items(), 1):
        text += f"{i}. 🔑 `{k}` → 💬 `{v[:30]}`\n"
        
    await message.reply_text(text)
