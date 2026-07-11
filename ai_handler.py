import aiohttp
import asyncio
import socket  # تم إضافة هذه المكتبة لحل مشكلة الـ DNS
from typing import Optional, List, Dict
from config import Config

class AIHandler:
    def __init__(self):
        self.provider = Config.AI_PROVIDER
        self.model = Config.AI_MODEL
        self.system_prompt = """أنت مساعد ذكي وودود. تتحدث بالعربية بشكل افتراضي.
        أجب بإيجاز ومفيد. إذا سُئلت عن شيء لا تعرفه، قل ذلك بصراحة.
        لا تستخدم لغة مسيئة أو غير لائقة."""

    async def get_response(self, message: str, chat_history: List[dict] = None) -> str:
        if not Config.AI_ENABLED:
            return "⚠️ الذكاء الاصطناعي معطل حالياً من الإعدادات."
        try:
            if self.provider == "huggingface":
                return await self._huggingface_response(message, chat_history)
            else:
                return "⚠️ مزود الذكاء الاصطناعي الحالي غير مدعوم، تم حصر البوت على Hugging Face."
        except Exception as e:
            return f"❌ خطأ برمجي في الاتصال: {str(e)[:100]}"

    async def _huggingface_response(self, message: str, chat_history: List[dict] = None) -> str:
        url = "https://api-inference.huggingface.co/v1/chat/completions"
        
        messages = [{"role": "system", "content": self.system_prompt}]
        if chat_history:
            for msg in chat_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": self.model, 
            "messages": messages, 
            "temperature": 0.7, 
            "max_tokens": 2048
        }
        headers = {
            "Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}", 
            "Content-Type": "application/json"
        }
        
        # حلال المشاكل: إجبار aiohttp على استخدام بروتوكول IPv4 لحل خطأ الـ DNS في Railway
        connector = aiohttp.TCPConnector(family=socket.AF_INET)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                data = await response.json()
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"]
                
                error_msg = data.get("error", {}).get("message", str(data))
                return f"⚠️ خطأ من سيرفر Hugging Face:\n{error_msg}"
