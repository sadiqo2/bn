import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from database import Database

db = Database()

# دالة ذكية تجيب آيدي الشخص (من الرد، أو التاك، أو إذا بالخاص تجيب آيدي الطرف الثاني)
async def get_target(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id
    
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        try:
            user = await client.get_users(parts[1])
            return user.id
        except:
            pass
            
    if message.chat.type == ChatType.PRIVATE:
        return message.chat.id
        
    return None

# -----------------------------------------
# أوامر الحظر وفك الحظر (بدون /)
# -----------------------------------------
@Client.on_message(filters.regex(r"^(حظر|بلوك)(?:\s+|$)") & filters.me)
async def block_user_cmd(client: Client, message: Message):
    try: await message.delete() 
    except: pass
    
    target = await get_target(client, message)
    if target:
        await client.block_user(target)
        msg = await message.reply_text("🚫 **تم حظر الشخص بنجاح.**")
        await asyncio.sleep(3)
        await msg.delete() # الرسالة تختفي بعد 3 ثواني حتى تبقى المحادثة نظيفة

@Client.on_message(filters.regex(r"^(فك حظر|فك البلوك)(?:\s+|$)") & filters.me)
async def unblock_user_cmd(client: Client, message: Message):
    try: await message.delete() 
    except: pass
    
    target = await get_target(client, message)
    if target:
        await client.unblock_user(target)
        msg = await message.reply_text("✅ **تم فك الحظر عنه.**")
        await asyncio.sleep(3)
        await msg.delete()

# -----------------------------------------
# أوامر الإسكات (الميوت)
# -----------------------------------------
@Client.on_message(filters.regex(r"^(اسكات|ميوت)(?:\s+|$)") & filters.me)
async def mute_user_cmd(client: Client, message: Message):
    try: await message.delete() 
    except: pass
    
    target = await get_target(client, message)
    if target:
        db.set_setting(f"mute_{target}", "true")
        msg = await message.reply_text("🤫 **تم اسكات الشخص. أي رسالة يدزها راح تنحذف من الطرفين.**")
        await asyncio.sleep(3)
        await msg.delete()

@Client.on_message(filters.regex(r"^(الغاء الاسكات|انميوت)(?:\s+|$)") & filters.me)
async def unmute_user_cmd(client: Client, message: Message):
    try: await message.delete() 
    except: pass
    
    target = await get_target(client, message)
    if target:
        db.set_setting(f"mute_{target}", "false")
        msg = await message.reply_text("🔊 **تم الغاء الاسكات.**")
        await asyncio.sleep(3)
        await msg.delete()

# -----------------------------------------
# نظام الحذف التلقائي للمسكتين (سريع جداً)
# -----------------------------------------
# group=-1 يعني هذا الفلتر يشتغل قبل كل شي بالبوت (أسرع أداء للـ Railway)
@Client.on_message(~filters.me, group=-1)
async def auto_delete_muted(client: Client, message: Message):
    if not message.from_user: return
    
    user_id = message.from_user.id
    if db.get_setting(f"mute_{user_id}") == "true":
        try:
            # revoke=True تعني حذف الرسالة من عندك ومن عنده (للطرفين)
            await message.delete(revoke=True)
        except:
            pass
