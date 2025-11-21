from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Callback datalar uchun konstantalar
class AddTriggerCallback:
    # Trigger turlari
    TYPE_NUMERIC = "tr_type_numeric"
    TYPE_TEXT = "tr_type_text"
    
    # Kontent turlari
    CONTENT_TEXT = "ct_text"
    CONTENT_PHOTO = "ct_photo"
    CONTENT_VIDEO = "ct_video"
    CONTENT_AUDIO = "ct_audio"
    CONTENT_VOICE = "ct_voice"
    CONTENT_DOCUMENT = "ct_document"
    CONTENT_STICKER = "ct_sticker"
    
    # Tasdiqlash
    CONFIRM_YES = "confirm_save"
    CONFIRM_NO = "confirm_cancel"
    
    # Bekor qilish
    CANCEL = "cancel_wizard"

def get_trigger_type_keyboard() -> InlineKeyboardMarkup:
    """1-qadam: Trigger turini tanlash."""
    buttons = [
        [
            InlineKeyboardButton(text="🔢 Raqam (1, 25...)", callback_data=AddTriggerCallback.TYPE_NUMERIC),
            InlineKeyboardButton(text="🔤 Matn (Salom...)", callback_data=AddTriggerCallback.TYPE_TEXT)
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=AddTriggerCallback.CANCEL)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_content_type_keyboard() -> InlineKeyboardMarkup:
    """3-qadam: Javob turini tanlash."""
    buttons = [
        [
            InlineKeyboardButton(text="📄 Matn", callback_data=AddTriggerCallback.CONTENT_TEXT),
            InlineKeyboardButton(text="📸 Rasm", callback_data=AddTriggerCallback.CONTENT_PHOTO)
        ],
        [
            InlineKeyboardButton(text="🎞 Video", callback_data=AddTriggerCallback.CONTENT_VIDEO),
            InlineKeyboardButton(text="🎵 Audio", callback_data=AddTriggerCallback.CONTENT_AUDIO)
        ],
        [
            InlineKeyboardButton(text="🎙 Voice", callback_data=AddTriggerCallback.CONTENT_VOICE),
            InlineKeyboardButton(text="🎭 Sticker", callback_data=AddTriggerCallback.CONTENT_STICKER)
        ],
        [
            InlineKeyboardButton(text="📁 Fayl (Document)", callback_data=AddTriggerCallback.CONTENT_DOCUMENT)
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=AddTriggerCallback.CANCEL)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """5-qadam: Saqlashni tasdiqlash."""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Ha, saqlash", callback_data=AddTriggerCallback.CONFIRM_YES),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=AddTriggerCallback.CONFIRM_NO)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Faqat bekor qilish tugmasi (input kutilayotganda)."""
    buttons = [
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=AddTriggerCallback.CANCEL)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)