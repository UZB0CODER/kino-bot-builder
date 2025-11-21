from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from db.mongo import db_service
from db.models import Trigger, TriggerType, ContentType as DBContentType
from keyboards.admin_main import AdminCallback, get_admin_main_keyboard
from keyboards.add_trigger import (
    AddTriggerCallback, 
    get_trigger_type_keyboard, 
    get_content_type_keyboard, 
    get_confirm_keyboard,
    get_cancel_keyboard
)
from utils.category_calc import get_category_name

# Yangi router
add_trigger_router = Router()

# --- HOLATLAR (STATES) ---
class AddTriggerStates(StatesGroup):
    WAITING_FOR_TYPE = State()          # 1. Trigger turi (Raqam/Matn)
    WAITING_FOR_VALUE = State()         # 2. Trigger qiymati (masalan "7" yoki "Salom")
    WAITING_FOR_CONTENT_TYPE = State()  # 3. Javob turi (Rasm/Video...)
    WAITING_FOR_CONTENT = State()       # 4. Kontentni yuklash
    CONFIRMATION = State()              # 5. Tasdiqlash

# --- 1-QADAM: JARAYONNI BOSHLASH ---
@add_trigger_router.callback_query(F.data == AdminCallback.ADD_TRIGGER)
async def start_add_trigger(call: CallbackQuery, state: FSMContext):
    """Yangi trigger qo'shishni boshlash."""
    await state.clear() # Eski ma'lumotlarni tozalash
    await state.set_state(AddTriggerStates.WAITING_FOR_TYPE)
    
    await call.message.edit_text(
        "<b>1-qadam:</b> Trigger turini tanlang:\n\n"
        "🔢 <b>Raqam</b> — menyu bo'limlariga tushadi (1, 25...)\n"
        "🔤 <b>Matn</b> — har qanday so'z yoki gap uchun",
        reply_markup=get_trigger_type_keyboard()
    )
    await call.answer()

# --- 2-QADAM: TRIGGER QIYMATINI SO'RASH ---
@add_trigger_router.callback_query(AddTriggerStates.WAITING_FOR_TYPE)
async def set_trigger_type(call: CallbackQuery, state: FSMContext):
    trigger_type = TriggerType.NUMERIC if call.data == AddTriggerCallback.TYPE_NUMERIC else TriggerType.TEXT
    
    # Ma'lumotni vaqtinchalik xotiraga yozamiz
    await state.update_data(trigger_type=trigger_type)
    await state.set_state(AddTriggerStates.WAITING_FOR_VALUE)
    
    text_type = "raqamni" if trigger_type == TriggerType.NUMERIC else "so'z yoki gapni"
    
    await call.message.edit_text(
        f"<b>2-qadam:</b> Iltimos, trigger bo'ladigan {text_type} yozib yuboring:",
        reply_markup=get_cancel_keyboard()
    )
    await call.answer()

# --- 3-QADAM: KONTENT TURINI SO'RASH ---
@add_trigger_router.message(AddTriggerStates.WAITING_FOR_VALUE)
async def set_trigger_value(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, matn ko'rinishida yuboring.")
        return

    value = message.text.strip()
    data = await state.get_data()
    
    # Agar raqamli trigger tanlangan bo'lsa, raqam ekanligini tekshiramiz
    if data['trigger_type'] == TriggerType.NUMERIC and not value.isdigit():
        await message.answer("⚠️ Iltimos, faqat butun son yuboring (masalan: 7)")
        return

    # DB da borligini tekshiramiz
    existing = await db_service.get_trigger(value)
    if existing:
        await message.answer(f"⚠️ <b>'{value}'</b> triggeri allaqachon mavjud! Boshqasini kiriting yoki bekor qiling.", reply_markup=get_cancel_keyboard())
        return

    await state.update_data(trigger_value=value)
    await state.set_state(AddTriggerStates.WAITING_FOR_CONTENT_TYPE)
    
    await message.answer(
        f"Trigger qabul qilindi: <b>{value}</b>\n\n"
        "<b>3-qadam:</b> Endi javob turini tanlang:",
        reply_markup=get_content_type_keyboard()
    )

# --- 4-QADAM: KONTENTNI KUTISH ---
@add_trigger_router.callback_query(AddTriggerStates.WAITING_FOR_CONTENT_TYPE)
async def set_content_type(call: CallbackQuery, state: FSMContext):
    # Mapping callback -> DBContentType
    mapping = {
        AddTriggerCallback.CONTENT_TEXT: DBContentType.TEXT,
        AddTriggerCallback.CONTENT_PHOTO: DBContentType.PHOTO,
        AddTriggerCallback.CONTENT_VIDEO: DBContentType.VIDEO,
        AddTriggerCallback.CONTENT_AUDIO: DBContentType.AUDIO,
        AddTriggerCallback.CONTENT_VOICE: DBContentType.VOICE,
        AddTriggerCallback.CONTENT_DOCUMENT: DBContentType.DOCUMENT,
        AddTriggerCallback.CONTENT_STICKER: DBContentType.STICKER,
    }
    
    c_type = mapping.get(call.data)
    if not c_type:
        return # Noma'lum callback

    await state.update_data(content_type=c_type)
    await state.set_state(AddTriggerStates.WAITING_FOR_CONTENT)
    
    msg = "<b>4-qadam:</b> "
    if c_type == DBContentType.TEXT:
        msg += "Javob matnini yuboring:"
    else:
        msg += f"Javob uchun <b>{c_type}</b> (fayl) yuboring:"
        
    await call.message.edit_text(msg, reply_markup=get_cancel_keyboard())
    await call.answer()

# --- 5-QADAM: KONTENTNI QABUL QILISH VA TASDIQLASH ---
@add_trigger_router.message(AddTriggerStates.WAITING_FOR_CONTENT)
async def receive_content(message: Message, state: FSMContext):
    data = await state.get_data()
    expected_type = data.get('content_type')
    
    file_id = None
    
    # Fayl ID sini olish logikasi
    if expected_type == DBContentType.TEXT:
        if not message.text:
            await message.answer("Iltimos, matn yuboring.")
            return
        file_id = message.html_text # Formatlangan matnni olamiz
        
    elif expected_type == DBContentType.PHOTO and message.photo:
        file_id = message.photo[-1].file_id # Eng yuqori sifat
    elif expected_type == DBContentType.VIDEO and message.video:
        file_id = message.video.file_id
    elif expected_type == DBContentType.AUDIO and message.audio:
        file_id = message.audio.file_id
    elif expected_type == DBContentType.VOICE and message.voice:
        file_id = message.voice.file_id
    elif expected_type == DBContentType.DOCUMENT and message.document:
        file_id = message.document.file_id
    elif expected_type == DBContentType.STICKER and message.sticker:
        file_id = message.sticker.file_id
    else:
        await message.answer(f"⚠️ Iltimos, to'g'ri formatdagi ({expected_type}) ma'lumot yuboring.")
        return

    # Hamma ma'lumot tayyor
    await state.update_data(file_id=file_id)
    await state.set_state(AddTriggerStates.CONFIRMATION)
    
    # Tasdiqlash xabari
    summary = (
        "<b>Tasdiqlash:</b>\n\n"
        f"🔹 Trigger: <b>{data['trigger_value']}</b>\n"
        f"🔹 Turi: {data['trigger_type']}\n"
        f"🔹 Javob: {expected_type}\n\n"
        "Saqlaymizmi?"
    )
    
    # Agar bu fayl bo'lsa, oldin o'zini yuborib ko'rsatishimiz mumkin (preview),
    # lekin hozircha oddiy text bilan tasdiqlaymiz.
    await message.answer(summary, reply_markup=get_confirm_keyboard())

# --- 6-QADAM: SAQLASH ---
@add_trigger_router.callback_query(AddTriggerStates.CONFIRMATION, F.data == AddTriggerCallback.CONFIRM_YES)
async def save_trigger(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Kategoriyani hisoblash (faqat numeric uchun)
    category = None
    if data['trigger_type'] == TriggerType.NUMERIC:
        category = get_category_name(int(data['trigger_value']))

    # Model yaratish
    new_trigger = Trigger(
        trigger=data['trigger_value'],
        trigger_type=data['trigger_type'],
        content_type=data['content_type'],
        file_id=data['file_id'],
        category=category
    )
    
    # DB ga yozish
    success = await db_service.add_trigger(new_trigger)
    
    if success:
        await call.message.edit_text(
            f"✅ <b>Trigger ({new_trigger.trigger}) muvaffaqiyatli saqlandi!</b>",
            reply_markup=None
        )
        # Bosh menyuga qaytish
        await call.message.answer("Bosh menyu:", reply_markup=get_admin_main_keyboard())
    else:
        await call.message.edit_text("❌ Xatolik yuz berdi. Trigger saqlanmadi.")
        
    await state.clear()
    await call.answer()

# --- BEKOR QILISH (Universal) ---
@add_trigger_router.callback_query(F.data.in_([AddTriggerCallback.CANCEL, AddTriggerCallback.CONFIRM_NO]))
async def cancel_wizard(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await call.message.edit_text("❌ Jarayon bekor qilindi.", reply_markup=None)
    await call.message.answer("Bosh menyu:", reply_markup=get_admin_main_keyboard())
    await call.answer()