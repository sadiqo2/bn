import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

class Database:
    def __init__(self):
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        self.db_path = os.path.join(Config.DATA_DIR, "bot_database.sqlite")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._setup_tables()
        
    # ... (باقي كود قاعدة البيانات مثل ما هو بدون تغيير)


    def _setup_tables(self):
        # إنشاء الجداول إذا ما كانت موجودة
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS auto_replies (keyword TEXT PRIMARY KEY, response TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stats (stat_name TEXT PRIMARY KEY, count INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history (chat_id TEXT, role TEXT, content TEXT, timestamp TEXT)''')
        self.conn.commit()
        
        # الإعدادات الافتراضية
        default_settings = {
            "auto_reply": "true", "ai_reply": "true", 
            "reply_to_all": "false", "language": "ar"
        }
        for k, v in default_settings.items():
            self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
        
        default_stats = [
            "total_messages", "auto_replies_sent", "ai_replies_sent", 
            "groups_handled", "private_chats"
        ]
        for stat in default_stats:
            self.cursor.execute("INSERT OR IGNORE INTO stats (stat_name, count) VALUES (?, 0)", (stat,))
            
        self.cursor.execute("INSERT OR IGNORE INTO stats (stat_name, count) VALUES ('start_time', ?)", (datetime.now().isoformat(),))
        self.conn.commit()

    # --- دوال الإعدادات ---
    def get_setting(self, key: str):
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        if result:
            val = result[0]
            if val == "true": return True
            if val == "false": return False
            return val
        return None

    def set_setting(self, key: str, value):
        val_str = "true" if value is True else "false" if value is False else str(value)
        self.cursor.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, val_str))
        self.conn.commit()

    def get_all_settings(self) -> dict:
        self.cursor.execute("SELECT key, value FROM settings")
        return {row[0]: (True if row[1]=="true" else False if row[1]=="false" else row[1]) for row in self.cursor.fetchall()}

    # --- دوال الردود ---
    def add_reply(self, keyword: str, response: str) -> bool:
        self.cursor.execute("REPLACE INTO auto_replies (keyword, response) VALUES (?, ?)", (keyword.lower(), response))
        self.conn.commit()
        return True

    def remove_reply(self, keyword: str) -> bool:
        self.cursor.execute("DELETE FROM auto_replies WHERE keyword = ?", (keyword.lower(),))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_reply(self, text: str) -> Optional[str]:
        self.cursor.execute("SELECT response FROM auto_replies WHERE ? LIKE '%' || keyword || '%'", (text.lower(),))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_all_replies(self) -> Dict[str, str]:
        self.cursor.execute("SELECT keyword, response FROM auto_replies")
        return {row[0]: row[1] for row in self.cursor.fetchall()}

    # --- دوال الإحصائيات ---
    def increment_stat(self, stat_name: str, user_id: int = None):
        self.cursor.execute("UPDATE stats SET count = count + 1 WHERE stat_name = ?", (stat_name,))
        self.conn.commit()

    def get_stats(self) -> dict:
        self.cursor.execute("SELECT stat_name, count FROM stats")
        stats_dict = {row[0]: row[1] for row in self.cursor.fetchall()}
        return stats_dict

    # --- دوال سجل المحادثات للذكاء الاصطناعي ---
    def add_to_history(self, chat_id: int, role: str, content: str):
        cid = str(chat_id)
        self.cursor.execute("INSERT INTO chat_history (chat_id, role, content, timestamp) VALUES (?, ?, ?, ?)", 
                            (cid, role, content, datetime.now().isoformat()))
        # الحفاظ على آخر 50 رسالة فقط لكل محادثة
        self.cursor.execute("""
            DELETE FROM chat_history WHERE rowid NOT IN (
                SELECT rowid FROM chat_history WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 50
            ) AND chat_id = ?
        """, (cid, cid))
        self.conn.commit()

    def get_chat_history(self, chat_id: int, limit: int = 10) -> List[dict]:
        self.cursor.execute("SELECT role, content FROM chat_history WHERE chat_id = ? ORDER BY timestamp ASC LIMIT ?", (str(chat_id), limit))
        return [{"role": row[0], "content": row[1]} for row in self.cursor.fetchall()]
