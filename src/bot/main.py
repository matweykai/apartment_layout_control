from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application

from bot.config import config, RunMode
from bot.handlers.message_handlers import setup_handlers
from utils.logger import init_logger


load_dotenv()


def create_application() -> Application:
    """Create and configure the Application."""
    logger = init_logger(__name__)

    if config.DEBUG:
        logger.debug('DEBUG MODE IS ON. TURN IT OFF IN PROD!!!')

    application = Application.builder().token(config.BOT_TOKEN).build()

    logger.info('Setting up handlers...')
    setup_handlers(application)
    logger.info('Handlers setup complete')

    return application


def run_webhook(application: Application) -> None:
    """Run the bot in webhook mode."""
    application.bot.set_webhook(url=config.WEBHOOK_URL)
    application.run_webhook(
        listen=config.WEBHOOK_LISTEN,
        port=config.WEBHOOK_PORT,
        url_path=config.WEBHOOK_PATH,
        webhook_url=config.WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES,
    )


def run_polling(application: Application) -> None:
    """Run the bot in polling mode."""
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def main() -> None:
    """Start the bot."""
    application = create_application()

    if config.RUN_MODE == RunMode.POLLING:
        run_polling(application)
    elif config.RUN_MODE == RunMode.WEBHOOK:
        run_webhook(application)


def run_bot():
    """Run the bot in the appropriate mode."""
    main()
