import os
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Bot konfiguratsiyasini yuklash va validatsiya qilish uchun sinf.
    Loyiha bo'ylab bir xil nomlarni (Uppercase) saqlash uchun moslashtirildi.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # .env dagi ortiqcha o'zgaruvchilarni ignor qilish
    )

    # --- Bot Settings ---
    # Field(..., alias="BOT_TOKEN") atrof-muhit o'zgaruvchisini o'qiydi
    BOT_TOKEN: str
    
    # Adminlarni vergul bilan ajratilgan stringdan listga o'tkazamiz
    ADMIN_IDS: List[int]

    # --- Webhook Settings ---
    WEBHOOK_HOST: str
    WEBHOOK_PATH: str = "/webhook"
    
    # Railway va server sozlamalari
    WEB_SERVER_HOST: str = "0.0.0.0"
    # Railway PORT environment o'zgaruvchisini beradi, biz uni WEB_SERVER_PORT ga o'zlashtiramiz
    WEB_SERVER_PORT: int = Field(default=8080, alias="PORT")

    # --- Database Settings ---
    MONGO_URL: str
    MONGO_DATABASE: str = "auto_reply_bot_db"

    # --- Validators ---
    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: str | List[int]) -> List[int]:
        """
        Vergul bilan ajratilgan satrni (masalan: "123,456") integerlar ro'yxatiga aylantiradi.
        """
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
        """To'liq Webhook URL manzilini shakllantiradi."""
        # Oxirida slash bor-yo'qligini tekshirib olamiz
        host = self.WEBHOOK_HOST.rstrip('/')
        return f"{host}{self.WEBHOOK_PATH}"

# Sozlamalarni yuklaymiz va global obyekt yaratamiz
# Boshqa fayllar "from config import CONFIG" deb chaqiradi
CONFIG = Settings()