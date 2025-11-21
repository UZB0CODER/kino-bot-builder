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

    # --- Database Settings (Avtomatik ulanish) ---
    # MONGO_URL nomi kerak emas, shuning uchun 'alias' orqali uni Railway bergan nomga bog'laymiz
    # Agar Railway MongoDB servisida MONGO_URL yetsa, uni qo'lda kiritish shart emas.
    # Agar sizning DB ssilkangiz DATABASE_URL nomi bilan berilgan bo'lsa, quyidagini ishlatamiz:
    MONGO_URL: str = Field(..., alias="MONGO_URL") # Hozircha shu nomni qoldiramiz, lekin ulanishni tekshiramiz.
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
        host = self.WEBHOOK_HOST.rstrip('/')
        return f"https://{host}{self.WEBHOOK_PATH}" # HTTPS qo'shildi

# Sozlamalarni yuklaymiz va global obyekt yaratamiz
CONFIG = Settings()