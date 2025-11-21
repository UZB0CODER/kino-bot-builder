from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Bot konfiguratsiyasini yuklash va validatsiya qilish uchun sinf.
    Railway avtomatik o'zgaruvchilarini ishlatishga moslashtirildi.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # --- Bot Settings ---
    BOT_TOKEN: str
    ADMIN_IDS: List[int]

    # --- Webhook Settings (RAILWAY_PUBLIC_DOMAIN dan foydalanish) ---
    # WEBHOOK_HOST uchun Railway'ning avtomatik domenini ishlatamiz
    WEBHOOK_HOST: str = Field(..., alias="RAILWAY_PUBLIC_DOMAIN") 
    WEBHOOK_PATH: str = "/webhook"
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = Field(default=8080, alias="PORT")

    # --- Database Settings (AVTOMATIK ULANISHNI TO'G'RILASH) ---
    # MONGO_URL nomi PyDantic tomonidan talab qilinmoqda, lekin ulanish uchun
    # Railway'ning haqiqiy ssilkasini beruvchi MONGO_PUBLIC_URL dan foydalanamiz.
    MONGO_URL: str = Field(..., alias="MONGO_PUBLIC_URL") 
    MONGO_DATABASE: str = "auto_reply_bot_db"

    # --- Validators ---
    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: str | List[int]) -> List[int]:
        if isinstance(v, list):
            return v
        if isinstance(v, str) and v:
            try:
                return [int(i.strip()) for i in v.split(",") if i.strip()]
            except ValueError:
                raise ValueError("ADMIN_IDS butun sonlardan iborat bo'lishi kerak.")
        return []

    @property
    def WEBHOOK_URL(self) -> str:
        # WEBHOOK_HOST dan 'https://'ni olib tashlash kerak emas, Railway uni o'zi to'g'ri beradi.
        host = self.WEBHOOK_HOST.rstrip('/')
        return f"https://{host}{self.WEBHOOK_PATH}" 

# Sozlamalarni yuklaymiz va global obyekt yaratamiz
CONFIG = Settings()