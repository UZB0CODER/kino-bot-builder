from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

# Bosh menyu buttonlari uchun callback data prefixlari
class AdminCallback:
    MAIN_MENU = "admin_main"
    CATEGORIES = "admin_cats"
    ADD_TRIGGER = "admin_add_trigger"
    IMPORT_EXPORT = "admin_import_export"
    ADMIN_LIST = "admin_admins"
    SETTINGS = "admin_settings"
    BACK = "back_to_menu"

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """
    Admin paneli uchun asosiy menyu klaviaturasini yaratadi.
    """
    
    buttons = [
        # Bosh menyu (4-qadam)
        [InlineKeyboardButton(text="📁 Trigger Bo‘limlari", callback_data=AdminCallback.CATEGORIES)],
        [InlineKeyboardButton(text="➕ Yangi Javob", callback_data=AdminCallback.ADD_TRIGGER)],
        [
            InlineKeyboardButton(text="📦 Import/Export", callback_data=AdminCallback.IMPORT_EXPORT),
            InlineKeyboardButton(text="👥 Adminlar", callback_data=AdminCallback.ADMIN_LIST),
        ],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data=AdminCallback.SETTINGS)],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_categories_keyboard(categories: List[str]) -> InlineKeyboardMarkup:
    """
    Trigger bo'limlari ro'yxati uchun klaviatura yaratadi.
    """
    buttons = []
    for cat in categories:
        # Bo'lim nomlari button matni va callback datasi sifatida ishlatiladi
        # Callback formati: "admin_cats:1-25"
        buttons.append([InlineKeyboardButton(text=cat, callback_data=f"{AdminCallback.CATEGORIES}:{cat}")])
        
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=AdminCallback.MAIN_MENU)])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)