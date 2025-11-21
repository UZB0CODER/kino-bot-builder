import sys
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Loyiha modullari
from config import CONFIG
from db.mongo import db_service

# Biz yaratgan routerlarni import qilamiz
from handlers.admin_menu import admin_router
from handlers.add_trigger import add_trigger_router
from handlers.edit_trigger import edit_trigger_router
from handlers.user_handler import user_router

# Logging sozlash
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# Bot va Dispatcher obyektlari
bot = Bot(token=CONFIG.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# --- ROUTERLARNI ULASH ---
# Tartib juda muhim! Maxsus handlerlar oldin, umumiy handlerlar keyin turishi kerak.

# 1. Admin menyusi va navigatsiyasi
dp.include_router(admin_router)

# 2. Yangi trigger qo'shish (Wizard)
dp.include_router(add_trigger_router)

# 3. Triggerlarni tahrirlash va o'chirish
dp.include_router(edit_trigger_router)

# 4. Oddiy foydalanuvchi handlerlari (Trigger qidirish)
# DIQQAT: Bu router eng oxirida bo'lishi kerak, chunki u barcha matnli xabarlarni ushlaydi (@user_router.message())
dp.include_router(user_router)


# --- STARTUP / SHUTDOWN ---

async def on_startup(bot: Bot):
    """Bot ishga tushganda bajariladigan ishlar"""
    # 1. DB indekslarini yaratish (tezkor qidiruv uchun)
    await db_service.create_indexes()
    
    # 2. Webhookni o'rnatish
    # drop_pending_updates=True -> Bot o'chiq payti yig'ilib qolgan eski xabarlarni tashlab yuboradi
    await bot.set_webhook(CONFIG.WEBHOOK_URL, drop_pending_updates=True)
    
    logging.info(f"🚀 Bot ishga tushdi! Webhook: {CONFIG.WEBHOOK_URL}")
    logging.info(f"Adminlar: {CONFIG.ADMIN_IDS}")

async def on_shutdown(bot: Bot):
    """Bot to'xtaganda bajariladigan ishlar"""
    # Webhookni o'chirish
    await bot.delete_webhook()
    logging.info("🛑 Webhook o'chirildi")
    
    # DB ulanishini yopish
    db_service.client.close()
    logging.info("MongoDB ulanishi yopildi")

# --- MAIN SERVER ---

def main():
    # Aiohttp web ilovasini yaratish
    app = web.Application()

    # Dispatcher va Webhook handlerini sozlash
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    
    # Webhook URL ga handlerni ulash (masalan: /webhook)
    webhook_requests_handler.register(app, path=CONFIG.WEBHOOK_PATH)
    
    # Aiogram kontekstini sozlash
    setup_application(app, dp, bot=bot)

    # Startup va Shutdown hodisalarini ulash
    app.on_startup.append(lambda app: on_startup(bot))
    app.on_shutdown.append(lambda app: on_shutdown(bot))

    # Serverni ishga tushirish
    # CONFIG.WEB_SERVER_PORT Railway tomonidan berilgan PORT (yoki default 8080) bo'ladi
    web.run_app(app, host=CONFIG.WEB_SERVER_HOST, port=CONFIG.WEB_SERVER_PORT)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot manually stopped")