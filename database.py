import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

class Database:
    def __init__(self):
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        self.replies_file = os.path.join(Config.DATA_DIR, "auto_replies.json")
        self.stats_file = os.path.join(Config.DATA_DIR, "stats.json")
        self.history_file = os.path.join(Config.DATA_DIR, "chat_history.json")
        self.settings_file = os.path.join(Config.DATA_DIR, "settings.json")

        self.replies = self._load_json(self.replies_file, {})
        self.stats = self._load_json(self.stats_file, self._default_stats())
        self.history = self._load_json(self.history_file, {})
        self.settings = self._load_json(self.settings_file, self._default_settings())

    def _load_json(self, filepath: str, default: dict) -> dict:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default

    def _save_json(self, filepath: str, data: dict):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _default_stats(self) -> dict:
        return {
            "total_messages": 0,
            "auto_replies_sent": 0,
            "ai_replies_sent": 0,
            "groups_handled": 0,
            "private_chats": 0,
            "start_time": datetime.now().isoformat(),
            "daily_stats": {},
            "top_keywords": {},
            "user_stats": {}
        }

    def _default_settings(self) -> dict:
        return {
            "auto_reply": True,
            "ai_reply": True,
            "reply_to_all": False,
            "welcome_message": "👋 مرحباً! كيف يمكنني مساعدتك؟",
            "blocked_keywords": [],
            "allowed_groups": [],
            "language": "ar"
        }

    def add_reply(self, keyword: str, response: str) -> bool:
        self.replies[keyword.lower()] = response
        self._save_json(self.replies_file, self.replies)
        return True

    def remove_reply(self, keyword: str) -> bool:
        if keyword.lower() in self.replies:
            del self.replies[keyword.lower()]
            self._save_json(self.replies_file, self.replies)
            return True
        return False

    def get_reply(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for keyword, response in self.replies.items():
            if keyword in text_lower:
                return response
        return None

    def get_all_replies(self) -> Dict[str, str]:
        return self.replies.copy()

    def increment_stat(self, stat_name: str, user_id: int = None):
        self.stats[stat_name] = self.stats.get(stat_name, 0) + 1
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = {"messages": 0, "replies": 0}
        self.stats["daily_stats"][today]["messages"] += 1
        if user_id:
            uid = str(user_id)
            if uid not in self.stats["user_stats"]:
                self.stats["user_stats"][uid] = {"messages": 0, "last_seen": ""}
            self.stats["user_stats"][uid]["messages"] += 1
            self.stats["user_stats"][uid]["last_seen"] = datetime.now().isoformat()
        self._save_json(self.stats_file, self.stats)

    def get_stats(self) -> dict:
        return self.stats.copy()

    def get_setting(self, key: str):
        return self.settings.get(key)

    def set_setting(self, key: str, value):
        self.settings[key] = value
        self._save_json(self.settings_file, self.settings)

    def get_all_settings(self) -> dict:
        return self.settings.copy()

    def add_to_history(self, chat_id: int, role: str, content: str):
        cid = str(chat_id)
        if cid not in self.history:
            self.history[cid] = []
        self.history[cid].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.history[cid] = self.history[cid][-50:]
        self._save_json(self.history_file, self.history)

    def get_chat_history(self, chat_id: int, limit: int = 10) -> List[dict]:
        cid = str(chat_id)
        return self.history.get(cid, [])[-limit:]
