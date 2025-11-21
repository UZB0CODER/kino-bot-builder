from aiogram import Router
from aiogram.types import Message
from aiogram.enums import ContentType as AiogramContentType # Aiogram turlari
import logging

from db.mongo import db_service
from db.models import ContentType as DBContentType # Bizning DB modelimizdagi turlar

# Foydalanuvchilar uchun alohida router
user_router = Router()

@user_router.message()
async def handle_user_message(message: Message):
    """
    Foydalanuvchidan kelgan har qanday matnli xabarni qabul qiladi
    va DB dan mos triggerni qidiradi.
    """
    # Faqat matnli xabarlarni ko'rib chiqamiz
    if not message.text:
        return

    # Kalit so'zni tozalaymiz (bosh va oxiridagi bo'shliqlarni olib tashlaymiz)
    trigger_key = message.text.strip()
    
    # 1. DB dan qidirish
    trigger_data = await db_service.get_trigger(trigger_key)
    
    # 2. Agar trigger topilsa, javob beramiz
    if trigger_data:
        file_id = trigger_data.file_id
        content_type = trigger_data.content_type
        
        try:
            if content_type == DBContentType.TEXT:
                # Agar matn bo'lsa, file_id o'rnida matn saqlangan bo'ladi
                await message.answer(file_id)
                
            elif content_type == DBContentType.PHOTO:
                await message.answer_photo(photo=file_id, caption=trigger_data.trigger)
                
            elif content_type == DBContentType.VIDEO:
                await message.answer_video(video=file_id, caption=trigger_data.trigger)
                
            elif content_type == DBContentType.AUDIO:
                await message.answer_audio(audio=file_id, caption=trigger_data.trigger)
                
            elif content_type == DBContentType.VOICE:
                await message.answer_voice(voice=file_id, caption=trigger_data.trigger)
                
            elif content_type == DBContentType.DOCUMENT:
                await message.answer_document(document=file_id, caption=trigger_data.trigger)
                
            elif content_type == DBContentType.STICKER:
                await message.answer_sticker(sticker=file_id)
                
            else:
                await message.answer("⚠️ Kechirasiz, bu kontent turi hozircha qo'llab-quvvatlanmaydi.")
                
        except Exception as e:
            logging.error(f"Trigger javobini yuborishda xato ({trigger_key}): {e}")
            await message.answer("⚠️ Texnik xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
            
    else:
        # 3. Agar trigger topilmasa
        # Kelajakda bu yerga "Default Reply" logikasini qo'shish mumkin
        await message.answer("Afsuski, bunday buyruq topilmadi. 😕")