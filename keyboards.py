from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")],
        [InlineKeyboardButton("📝 الردود التلقائية", callback_data="auto_replies")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton("🤖 الذكاء الاصطناعي", callback_data="ai_settings")],
        [InlineKeyboardButton("❓ المساعدة", callback_data="help")]
    ])

def settings_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تفعيل الردود التلقائية", callback_data="toggle_auto_reply")],
        [InlineKeyboardButton("🤖 تفعيل الذكاء الاصطناعي", callback_data="toggle_ai")],
        [InlineKeyboardButton("📢 الرد على الجميع", callback_data="toggle_reply_all")],
        [InlineKeyboardButton("🌐 تغيير اللغة", callback_data="change_lang")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
    ])

def auto_replies_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة رد", callback_data="add_reply")],
        [InlineKeyboardButton("📋 قائمة الردود", callback_data="list_replies")],
        [InlineKeyboardButton("🗑️ حذف رد", callback_data="delete_reply")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
    ])

def stats_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 إحصائيات عامة", callback_data="general_stats")],
        [InlineKeyboardButton("📅 إحصائيات يومية", callback_data="daily_stats")],
        [InlineKeyboardButton("👥 إحصائيات المستخدمين", callback_data="user_stats")],
        [InlineKeyboardButton("🔄 تحديث", callback_data="refresh_stats")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
    ])

def ai_settings_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 تغيير المزود", callback_data="change_provider")],
        [InlineKeyboardButton("📝 تغيير النموذج", callback_data="change_model")],
        [InlineKeyboardButton("🎯 اختبار الذكاء الاصطناعي", callback_data="test_ai")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
    ])

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
    ])
