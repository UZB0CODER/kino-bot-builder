from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from db.mongo import db_service
from db.models import Trigger
from keyboards.admin_main import AdminCallback
from keyboards.trigger_list import (
    TriggerAction, 
    get_trigger_list_keyboard, 
    get_trigger_detail_keyboard,
    get_delete_confirm_keyboard
)

edit_trigger_router = Router()

# --- 1. BO'LIM TANLANGANDA RO'YXATNI CHIQARISH ---
@edit_trigger_router.callback_query(F.data.startswith(f"{AdminCallback.CATEGORIES}:"))
async def show_trigger_list(call: CallbackQuery):
    """
    Masalan: 'admin_cats:1-25' bosilganda shu bo'limdagi triggerlarni chiqaradi.
    """
    # Callbackdan bo'lim nomini ajratib olamiz
    category = call.data.split(":")[1]
    
    # DB dan shu bo'limga tegishli triggerlarni olamiz
    triggers = await db_service.get_triggers_by_category(category)
    
    if not triggers:
        await call.answer("Bu bo'limda hali triggerlar yo'q.")
        return

    # Klaviatura yaratish (0-sahifa)
    keyboard = get_trigger_list_keyboard(triggers, category, page=0)
    
    await call.message.edit_text(
        f"📂 <b>Bo'lim: {category}</b>\n\nTriggerlardan birini tanlang:",
        reply_markup=keyboard
    )
    await call.answer()

# --- 2. PAGINATION (SAHIFALASH) ---
@edit_trigger_router.callback_query(F.data.startswith(f"{TriggerAction.PAGE}:"))
async def paginate_trigger_list(call: CallbackQuery):
    """
    Oldinga/Orqaga tugmalari bosilganda ishlaydi.
    Data formati: 'tr_page:CATEGORY:PAGE_NUM'
    """
    _, category, page_str = call.data.split(":")
    page = int(page_str)
    
    triggers = await db_service.get_triggers_by_category(category)
    keyboard = get_trigger_list_keyboard(triggers, category, page=page)
    
    await call.message.edit_text(
        f"📂 <b>Bo'lim: {category}</b>\n\nTriggerlardan birini tanlang:",
        reply_markup=keyboard
    )
    await call.answer()

# --- 3. TRIGGER TAFSILOTLARINI KO'RISH ---
@edit_trigger_router.callback_query(F.data.startswith(f"{TriggerAction.SELECT}:"))
async def show_trigger_details(call: CallbackQuery):
    """
    Trigger bosilganda uning tafsilotlari va boshqaruv tugmalari chiqadi.
    Data formati: 'tr_sel:TRIGGER_KEY'
    """
    trigger_key = call.data.split(":", 1)[1]
    
    trigger = await db_service.get_trigger(trigger_key)
    if not trigger:
        await call.answer("Trigger topilmadi (o'chirilgan bo'lishi mumkin).", show_alert=True)
        # Ro'yxatni yangilash mantiqan to'g'ri bo'lardi, lekin hozircha shunchaki qaytamiz
        return

    # Tafsilotlar matni
    info_text = (
        f"📌 <b>Trigger:</b> {trigger.trigger}\n"
        f"📂 <b>Bo'lim:</b> {trigger.category}\n"
        f"📝 <b>Turi:</b> {trigger.trigger_type}\n"
        f"📦 <b>Javob turi:</b> {trigger.content_type}\n\n"
        "Quyidagi amallardan birini tanlang:"
    )
    
    category = trigger.category if trigger.category else "Umumiy"
    keyboard = get_trigger_detail_keyboard(trigger_key, category)
    
    await call.message.edit_text(info_text, reply_markup=keyboard)
    await call.answer()

# --- 4. O'CHIRISHNI SO'RASH ---
@edit_trigger_router.callback_query(F.data.startswith(f"{TriggerAction.DELETE}:"))
async def ask_delete_trigger(call: CallbackQuery):
    trigger_key = call.data.split(":", 1)[1]
    
    # Triggerni qayta olamiz (category kerak bo'ladi orqaga qaytish uchun)
    trigger = await db_service.get_trigger(trigger_key)
    category = trigger.category if trigger and trigger.category else "Umumiy"
    
    await call.message.edit_text(
        f"🗑 <b>Haqiqatan ham '{trigger_key}' triggerini o'chirmoqchimisiz?</b>",
        reply_markup=get_delete_confirm_keyboard(trigger_key, category)
    )
    await call.answer()

# --- 5. O'CHIRISHNI TASDIQLASH ---
@edit_trigger_router.callback_query(F.data.startswith(f"{TriggerAction.DELETE_CONFIRM}:"))
async def confirm_delete_trigger(call: CallbackQuery):
    trigger_key = call.data.split(":", 1)[1]
    
    # O'chirishdan oldin kategoriyani eslab qolamiz (ro'yxatga qaytish uchun)
    trigger = await db_service.get_trigger(trigger_key)
    category = trigger.category if trigger and trigger.category else "1-25" # Default fallback
    
    success = await db_service.delete_trigger(trigger_key)
    
    if success:
        await call.answer("✅ Trigger o'chirildi!", show_alert=True)
        # Ro'yxatga qaytamiz
        triggers = await db_service.get_triggers_by_category(category)
        keyboard = get_trigger_list_keyboard(triggers, category, page=0)
        
        await call.message.edit_text(
            f"📂 <b>Bo'lim: {category}</b>\n\nTriggerlardan birini tanlang:",
            reply_markup=keyboard
        )
    else:
        await call.answer("❌ Xatolik: Trigger o'chirilmay qoldi.", show_alert=True)

# --- 6. RO'YXATGA QAYTISH (BACK) ---
@edit_trigger_router.callback_query(F.data.startswith(f"{TriggerAction.BACK_TO_LIST}:"))
async def back_to_list(call: CallbackQuery):
    category = call.data.split(":", 1)[1]
    
    triggers = await db_service.get_triggers_by_category(category)
    keyboard = get_trigger_list_keyboard(triggers, category, page=0)
    
    await call.message.edit_text(
        f"📂 <b>Bo'lim: {category}</b>\n\nTriggerlardan birini tanlang:",
        reply_markup=keyboard
    )
    await call.answer()

# --- 7. TAHRIRLASH (TODO) ---
@edit_trigger_router.callback_query(F.data.startswith(f"{TriggerAction.EDIT}:"))
async def edit_trigger_placeholder(call: CallbackQuery):
    """
    Hozircha tahrirlash funksiyasi 'Yangi qo'shish' logikasiga o'xshash.
    Soddalashtirish uchun adminni ogohlantiramiz.
    """
    await call.answer("✏️ Tahrirlash uchun eski triggerni o'chirib, yangisini yarating.", show_alert=True)