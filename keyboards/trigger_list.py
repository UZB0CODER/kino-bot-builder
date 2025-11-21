from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from db.models import Trigger
from keyboards.admin_main import AdminCallback

class TriggerAction:
    """Trigger ustida bajariladigan amallar uchun callback prefixlari."""
    SELECT = "tr_sel"   # Triggerni tanlash
    DELETE = "tr_del"   # O'chirish
    DELETE_CONFIRM = "tr_del_y" # O'chirishni tasdiqlash
    EDIT = "tr_edit"    # Tahrirlash
    PAGE = "tr_page"    # Sahifalash (Pagination)
    BACK_TO_LIST = "tr_back_list" # Ro'yxatga qaytish

def get_trigger_list_keyboard(triggers: List[Trigger], category: str, page: int = 0, page_size: int = 25) -> InlineKeyboardMarkup:
    """
    Berilgan bo'limdagi triggerlar ro'yxatini sahifalab chiqaradi.
    """
    builder = InlineKeyboardBuilder()
    
    # 1. Triggerlarni qirqib olamiz (Pagination logic)
    start_index = page * page_size
    end_index = start_index + page_size
    current_page_triggers = triggers[start_index:end_index]
    
    # 2. Har bir trigger uchun tugma yaratamiz
    for trigger in current_page_triggers:
        # Tugmada trigger nomi (kaliti) ko'rinadi
        builder.row(InlineKeyboardButton(
            text=f"🔹 {trigger.trigger}", 
            callback_data=f"{TriggerAction.SELECT}:{trigger.trigger}"
        ))
    
    # 3. Pagination tugmalari (Oldinga / Orqaga)
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Oldingi", 
            callback_data=f"{TriggerAction.PAGE}:{category}:{page-1}"
        ))
    
    if end_index < len(triggers):
        pagination_buttons.append(InlineKeyboardButton(
            text="Keyingi ➡️", 
            callback_data=f"{TriggerAction.PAGE}:{category}:{page+1}"
        ))
    
    if pagination_buttons:
        builder.row(*pagination_buttons)
    
    # 4. Orqaga (Bo'limlar menyusiga)
    builder.row(InlineKeyboardButton(text="🔙 Bo'limlarga qaytish", callback_data=AdminCallback.CATEGORIES))
    
    return builder.as_markup()

def get_trigger_detail_keyboard(trigger_key: str, category: str) -> InlineKeyboardMarkup:
    """
    Bitta trigger tanlanganda chiqadigan boshqaruv tugmalari.
    """
    buttons = [
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"{TriggerAction.EDIT}:{trigger_key}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"{TriggerAction.DELETE}:{trigger_key}")
        ],
        [InlineKeyboardButton(text="🔙 Ro'yxatga qaytish", callback_data=f"{TriggerAction.BACK_TO_LIST}:{category}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_delete_confirm_keyboard(trigger_key: str, category: str) -> InlineKeyboardMarkup:
    """
    O'chirishni tasdiqlash menyusi.
    """
    buttons = [
        [
            InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"{TriggerAction.DELETE_CONFIRM}:{trigger_key}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"{TriggerAction.SELECT}:{trigger_key}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)