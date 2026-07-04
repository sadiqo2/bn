import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# -----------------------------------------
# صانع الملصقات (تحويل أي صورة إلى ملصق)
# -----------------------------------------
@Client.on_message(filters.regex(r"^(ملصق|صانع)(?:\s+|$)") & filters.me)
async def make_sticker(client: Client, message: Message):
    # مسح أمرك فوراً
    try: await message.delete() 
    except: pass

    # التأكد من وجود رد على صورة
    if not message.reply_to_message or not message.reply_to_message.photo:
        msg = await message.reply_text("❌ **سوي رد (Reply) على صورة واكتب 'ملصق' حتى أحولها.**")
        await asyncio.sleep(3)
        return await msg.delete()
        
    processing = await message.reply_text("⏳ **جاري القص والتحويل...**")
    
    try:
        # تحميل الصورة وتحويلها لصيغة الملصقات (.webp)
        file_path = await message.reply_to_message.download(file_name="sticker.webp")
        
        # إرسال الملصق للمحادثة
        await client.send_sticker(message.chat.id, sticker=file_path)
        
        # تنظيف الملفات ورسالة التحميل
        os.remove(file_path)
        await processing.delete()
    except Exception as e:
        await processing.edit_text(f"❌ **حدث خطأ:** {str(e)[:50]}")


# -----------------------------------------
# سارق الملصقات (خمط الملصقات للمحفوظة)
# -----------------------------------------
@Client.on_message(filters.regex(r"^(خمط|زرف|سرقة)(?:\s+|$)") & filters.me)
async def steal_sticker(client: Client, message: Message):
    # مسح أمرك فوراً
    try: await message.delete() 
    except: pass

    # التأكد من وجود رد على ملصق
    if not message.reply_to_message or not message.reply_to_message.sticker:
        msg = await message.reply_text("❌ **سوي رد (Reply) على ملصق واكتب 'خمط' حتى أسرقه.**")
        await asyncio.sleep(3)
        return await msg.delete()
        
    processing = await message.reply_text("🥷 **جاري الخمط...**")
    
    try:
        # أخذ آيدي الملصق وإرساله للرسائل المحفوظة (me)
        sticker_id = message.reply_to_message.sticker.file_id
        await client.send_sticker("me", sticker_id)
        
        await processing.edit_text("✅ **تم خمط الملصق بنجاح وتهريبه للرسائل المحفوظة!** 🏃‍♂️💨")
        await asyncio.sleep(3)
        await processing.delete()
    except Exception as e:
        await processing.edit_text(f"❌ **حدث خطأ:** {str(e)[:50]}")
