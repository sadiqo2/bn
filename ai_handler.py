import aiohttp
import asyncio
from typing import Optional, List, Dict
from config import Config

class AIHandler:
    def __init__(self):
        self.provider = Config.AI_PROVIDER
        self.model = Config.AI_MODEL
        self.system_prompt = """أنت مساعد ذكي وودود. تتحدث بالعربية بشكل افتراضي.
        أجب بإيجاز ومفيد وبدون فلسفة زائدة."""

    async def get_response(self, message: str, chat_history: List[dict] = None) -> str:
        if not Config.AI_ENABLED:
            return "⚠️ الذكاء الاصطناعي معطل حالياً من الإعدادات."
        try:
            if self.provider == "groq":
                return await self._groq_response(message, chat_history)
            else:
                return "⚠️ مزود الذكاء الاصطناعي الحالي غير مدعوم، تم حصر البوت على Groq."
        except Exception as e:
            return f"❌ خطأ في الاتصال بسيرفر الذكاء الاصطناعي: {str(e)[:100]}"

    async def _groq_response(self, message: str, chat_history: List[dict] = None) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        messages = [{"role": "system", "content": self.system_prompt}]
        if chat_history:
            for msg in chat_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": self.model, 
            "messages": messages, 
            "temperature": 0.7, 
            "max_tokens": 1024
        }
        headers = {
            "Authorization": f"Bearer {Config.GROQ_API_KEY}", 
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as response:
                data = await response.json()
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"]
                
                error_msg = data.get("error", {}).get("message", str(data))
                return f"⚠️ خطأ من سيرفر Groq:\n{error_msg}"
