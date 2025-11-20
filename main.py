import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import AiohttpAPIServer, SimpleRequestHandler
from aiohttp import web

from config import settings


# --- Main Application Logic ---

@asynccontextmanager
async def lifespan(bot: Bot, dp: Dispatcher):
    """
    Context manager for application startup and shutdown logic.
    Sets and deletes the webhook.
    """
    # On startup
    webhook_url = settings.webhook_url
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        secret_token=None  # For simplicity, no secret token is used
    )
    logging.info(f"Webhook set to: {webhook_url}")
    yield
    # On shutdown
    await bot.delete_webhook()
    logging.info("Webhook deleted.")


# --- Handlers ---

async def start_handler(message: types.Message):
    """
    Handler for the /start command.
    """
    await message.answer("Bot is running! This is a test message.")


# --- Main Function ---

async def main():
    """
    Initializes and runs the bot application.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        stream=sys.stdout,
    )

    # Initialize Bot and Dispatcher
    bot = Bot(token=settings.bot_token, parse_mode="HTML")
    dp = Dispatcher()

    # Register handlers
    dp.message.register(start_handler, CommandStart())

    # Create aiohttp web application
    app = web.Application()
    
    # Create an instance of the AiohttpAPIServer
    webhook_server = AiohttpAPIServer(
        dispatcher=dp,
        bot=bot,
        # You can specify custom logic for handling updates here if needed
    )

    # Create a SimpleRequestHandler and register it on a specific path
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_handler.register(app, path=settings.webhook_path.format(bot_token=settings.bot_token))

    # Mount the server on the application using a context manager
    async with lifespan(bot, dp):
        # Start the web server
        await webhook_server.start(app)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually")
