import aiohttp
import asyncio
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
            return None
        try:
            if self.provider == "gemini":
                return await self._gemini_response(message, chat_history)
            elif self.provider == "groq":
                return await self._groq_response(message, chat_history)
            elif self.provider == "openrouter":
                return await self._openrouter_response(message, chat_history)
            else:
                return "⚠️ مزود الذكاء الاصطناعي غير محدد"
        except Exception as e:
            return f"❌ خطأ في الذكاء الاصطناعي: {str(e)[:100]}"

    async def _gemini_response(self, message: str, chat_history: List[dict] = None) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        contents = [{"role": "user", "parts": [{"text": self.system_prompt}]}]
        if chat_history:
            for msg in chat_history:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        contents.append({"role": "user", "parts": [{"text": message}]})
        payload = {
            "contents": contents,
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048, "topP": 0.9}
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params={"key": Config.GEMINI_API_KEY}, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                data = await response.json()
                if "candidates" in data and data["candidates"]:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                return "🤔 لم أفهم السؤال، هل يمكنك توضيحه أكثر؟"

    async def _groq_response(self, message: str, chat_history: List[dict] = None) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        messages = [{"role": "system", "content": self.system_prompt}]
        if chat_history:
            for msg in chat_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})
        payload = {"model": self.model, "messages": messages, "temperature": 0.7, "max_tokens": 2048}
        headers = {"Authorization": f"Bearer {Config.GROQ_API_KEY}", "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                data = await response.json()
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"]
                return "🤔 لم أفهم السؤال، هل يمكنك توضيحه أكثر؟"

    async def _openrouter_response(self, message: str, chat_history: List[dict] = None) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        messages = [{"role": "system", "content": self.system_prompt}]
        if chat_history:
            for msg in chat_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})
        payload = {"model": self.model, "messages": messages, "temperature": 0.7, "max_tokens": 2048}
        headers = {"Authorization": f"Bearer {Config.OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                data = await response.json()
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"]
                return "🤔 لم أفهم السؤال، هل يمكنك توضيحه أكثر؟"
