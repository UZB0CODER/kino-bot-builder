from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Botda qo'llab-quvvatlanadigan kontent turlari
class ContentType:
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    DOCUMENT = "document"
    STICKER = "sticker"

# Trigger turlari
class TriggerType:
    NUMERIC = "numeric"
    TEXT = "text"

class Trigger(BaseModel):
    """Ma'lumotlar bazasida saqlanadigan trigger obyekti."""
    
    # Trigger kaliti (matn yoki raqam). Unique bo'lishi kerak.
    trigger: str = Field(..., description="Foydalanuvchi yuboradigan kalit so'z yoki raqam.")
    
    # Trigger turi: 'numeric' yoki 'text'
    trigger_type: str = Field(..., description="Triggerni qanday qabul qilish kerakligi.")

    # Javob turi: 'text', 'photo', 'video' va hokazo.
    content_type: str = Field(..., description="Avtomatik javob kontent turi.")
    
    # Telegram File ID (Matn bo'lsa, bu erda matn saqlanadi)
    file_id: str = Field(..., description="Kontentning file_id (yoki matn kontenti).")
    
    # Trigger bo'limi (faqat raqamli triggerlar uchun, masalan '1-25')
    category: Optional[str] = Field(None, description="Triggerni ajratish uchun bo'lim.")
    
    # Yaratilgan vaqt
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Oxirgi yangilangan vaqt
    updated_at: Optional[datetime] = None

    # MongoDB obyektini Pydantic modelga moslash
    class Config:
        from_attributes = True
        populate_by_name = True