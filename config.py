import os
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Main settings class to load environment variables.
    Utilizes pydantic-settings for robust validation and type casting.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # --- Bot Settings ---
    bot_token: str = Field(..., alias="BOT_TOKEN")
    admin_ids: List[int] = Field(..., alias="ADMIN_IDS")

    # --- Webhook Settings (for Railway) ---
    webhook_host: str = Field(..., alias="WEBHOOK_HOST")
    # Railway provides the PORT environment variable automatically
    port: int = Field(default=8080, alias="PORT")
    # Path for the webhook, e.g., /webhook/123456:ABC-DEF...
    webhook_path: str = Field(default="/webhook/{bot_token}")

    # --- Database Settings ---
    mongo_url: str = Field(..., alias="MONGO_URL")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: str) -> List[int]:
        """
        Parses a comma-separated string of admin IDs into a list of integers.
        """
        if isinstance(v, str):
            try:
                return [int(admin_id.strip()) for admin_id in v.split(",")]
            except ValueError:
                raise ValueError("ADMIN_IDS must be a comma-separated list of integers.")
        return v

    @property
    def webhook_url(self) -> str:
        """
        Constructs the full webhook URL.
        """
        return f"{self.webhook_host}{self.webhook_path.format(bot_token=self.bot_token)}"


# Load settings from the environment
# This instance will be imported in other parts of the application
settings = Settings()
