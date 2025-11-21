from typing import Union
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import CONFIG
from keyboards.admin_main import get_admin_main_keyboard, AdminCallback, get_categories_keyboard
from utils.category_calc import get_all_categories

# Admin uchun alohida router yaratamiz
admin_router = Router()

# --- States & Filters ---

class AdminStates(StatesGroup):
    """Admin paneli holatlari."""
    MAIN_MENU = State()
    # Yangi trigger qo'shish va boshqa holatlar keyinroq boshqa fayllarda qo'shilishi mumkin

class IsAdmin(BaseFilter):
    """Foydalanuvchi admin ekanligini tekshiruvchi filtr."""
    async def __call__(self, update: Union[Message, CallbackQuery]) -> bool:
        user_id = update.from_user.id
        return user_id in CONFIG.ADMIN_IDS

# --- Handlers ---

@admin_router.message(CommandStart(), IsAdmin())
async def cmd_start_admin(message: Message, state: FSMContext):
    """
    Admin uchun /start buyrug'i.
    Bosh menyuni ko'rsatadi.
    """
    await state.clear()
    await state.set_state(AdminStates.MAIN_MENU)
    
    welcome_text = (
        "<b>Assalomu alaykum, Admin!</b> 👨‍💻\n\n"
        "Avtomatik javoblar konstruktori admin paneliga xush kelibsiz. "
        "Iltimos, ishlash uchun bo'limni tanlang:"
    )
    await message.answer(welcome_text, reply_markup=get_admin_main_keyboard())

@admin_router.callback_query(AdminStates.MAIN_MENU, F.data == AdminCallback.CATEGORIES)
async def handle_categories_menu(call: CallbackQuery):
    """
    'Trigger Bo‘limlari' tugmasi bosilganda ishlaydi.
    """
    categories = get_all_categories()
    await call.message.edit_text(
        "📁 <b>Trigger Bo‘limlari</b>\n\n"
        "Triggerlar soniga qarab ajratilgan bo'limni tanlang. "
        "Matnli triggerlar bo'limlarga kirmaydi.",
        reply_markup=get_categories_keyboard(categories)
    )
    await call.answer()

@admin_router.callback_query(F.data == AdminCallback.MAIN_MENU)
async def handle_back_to_main_menu(call: CallbackQuery, state: FSMContext):
    """
    'Orqaga' tugmasi bosilganda Bosh menyuga qaytaradi.
    """
    await state.set_state(AdminStates.MAIN_MENU)
    await call.message.edit_text(
        "Bosh menyu. Iltimos, bo'limni tanlang:",
        reply_markup=get_admin_main_keyboard()
    )
    await call.answer()