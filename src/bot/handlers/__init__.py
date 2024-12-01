# Empty file to make the directory a Python package
from .message_handlers import handle_photo, handle_text
from .commands import start, help_command
from telegram.ext import Application, CommandHandler, MessageHandler, filters


def setup_handlers(application: Application) -> None:
    """Setup all handlers for the application."""
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Add handler for user messages
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT, handle_text))
