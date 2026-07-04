import subprocess
import traceback
import io
import sys
from pyrogram import Client, filters
from pyrogram.types import Message

# 1. أمر /term - لتنفيذ أوامر النظام (مثل cmd أو terminal)
@Client.on_message(filters.command("term") & filters.me)
async def terminal_executer(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ اكتب الأمر بعد `/term`.\nمثال: `/term ls` أو `/term ping google.com`")
    
    cmd = message.text.split(maxsplit=1)[1]
    processing = await message.reply_text("⏳ جاري التنفيذ...")
    
    try:
        # تنفيذ الأمر بالنظام وسحب النتيجة
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        
        result = stdout.decode('utf-8') + stderr.decode('utf-8')
        if not result:
            result = "✅ تم التنفيذ بنجاح (بدون مخرجات)."
            
        # إذا كانت النتيجة طويلة جداً
        if len(result) > 4000:
            result = result[:4000] + "\n... (تم قطع النص للطول)"
            
        await processing.edit_text(f"💻 **الأمر:** `{cmd}`\n\n**المخرجات:**\n```\n{result}\n```")
    except Exception as e:
        await processing.edit_text(f"❌ **خطأ:**\n`{str(e)}`")

# 2. أمر /eval - لتنفيذ أكواد بايثون مباشرة من المحادثة
@Client.on_message(filters.command("eval") & filters.me)
async def python_eval(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ اكتب كود بايثون بعد `/eval`.")
    
    code = message.text.split(maxsplit=1)[1]
    processing = await message.reply_text("⏳ جاري المعالجة...")
    
    # تحويل الإخراج إلى المتغيرات حتى نرسلها بالتلكرام
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    
    try:
        # دالة لتنفيذ الأكواد التي تحتوي على await
        async def aexec(code, client, message):
            exec(
                f'async def __aexec(client, message):\n' +
                ''.join(f'    {l}\n' for l in code.split('\n'))
            )
            return await locals()['__aexec'](client, message)
        
        await aexec(code, client, message)
        result = redirected_output.getvalue()
        
        if not result:
            result = "✅ تم التنفيذ (بدون مخرجات مطبوعة)."
            
        await processing.edit_text(f"🐍 **الكود:**\n```python\n{code}\n```\n\n**النتيجة:**\n```\n{result}\n```")
    except Exception:
        exc = traceback.format_exc()
        await processing.edit_text(f"❌ **خطأ برمجي:**\n```python\n{exc}\n```")
    finally:
        sys.stdout = old_stdout
