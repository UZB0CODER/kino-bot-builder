from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime
from pydantic import ValidationError

# Config faylidan sozlamalarni olamiz
from config import CONFIG
from db.models import Trigger

class MongoService:
    """MongoDB bilan ishlash uchun yagona sinf."""
    
    def __init__(self):
        # MongoDB ga ulanish
        self.client = AsyncIOMotorClient(CONFIG.MONGO_URL)
        # Ma'lumotlar bazasini tanlash
        self.db = self.client[CONFIG.MONGO_DATABASE]
        # Triggers kolleksiyasini tanlash
        self.collection = self.db.triggers
        self.collection_name = "triggers"
    
    async def create_indexes(self):
        """Kolleksiyaga tezkor qidiruv va takrorlanmaslik uchun indekslarni o'rnatish."""
        # Trigger maydoni bo'yicha noyob (unique) indeks yaratish
        await self.collection.create_index(
            "trigger", 
            unique=True, 
            name="trigger_unique_index"
        )
        print(f"MongoDB: '{self.collection_name}' kolleksiyasida indekslar yaratildi.")

    async def add_trigger(self, data: Trigger) -> bool:
        """Yangi triggerni ma'lumotlar bazasiga qo'shish."""
        try:
            # Pydantic modelni dict ga o'tkazamiz
            document = data.model_dump(by_alias=True, exclude_none=True)
            result = await self.collection.insert_one(document)
            return result.inserted_id is not None
        except Exception as e:
            print(f"Trigger qo'shishda xato (ehtimol trigger mavjud): {e}")
            return False

    async def get_trigger(self, trigger_key: str) -> Optional[Trigger]:
        """Trigger kaliti bo'yicha javobni topish."""
        document = await self.collection.find_one({"trigger": trigger_key})
        if document:
            document.pop('_id', None) 
            try:
                return Trigger.model_validate(document)
            except ValidationError as e:
                print(f"Model validatsiya xatosi: {e}")
                return None
        return None

    async def get_triggers_by_category(self, category_name: str) -> List[Trigger]:
        """Bo'lim nomi bo'yicha triggerlarni yuklash (masalan, '1-25')."""
        triggers: List[Trigger] = []
        cursor = self.collection.find({"category": category_name})
        async for document in cursor:
            document.pop('_id', None)
            try:
                triggers.append(Trigger.model_validate(document))
            except ValidationError as e:
                continue
        return triggers

    async def delete_trigger(self, trigger_key: str) -> bool:
        """Triggerni ma'lumotlar bazasidan o'chirish."""
        result = await self.collection.delete_one({"trigger": trigger_key})
        return result.deleted_count > 0

# Global obyekt yaratamiz, shunda boshqa fayllarda `from db.mongo import db_service` deb ishlata olamiz
db_service = MongoService()