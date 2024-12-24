import io
import json

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import config
from bot.handlers.vllm import VLM
from utils.logger import init_logger

from bot.handlers.commands import start, help_command
from telegram.ext import Application, CommandHandler, MessageHandler, filters


logger = init_logger(__name__)
vllm_model = VLM(config)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    photo_file = await update.message.photo[-1].get_file()

    photo_buffer = io.BytesIO(b'')
    await photo_file.download_to_memory(photo_buffer)

    logger.info(f'{user.first_name} sent a photo')
    model_answer = await vllm_model.process_image(photo_buffer)

    model_answer = model_answer.replace('json', '').replace('```', '').strip()

    # Parse json
    json_answer = json.loads(model_answer)

    if json_answer['is_damaged']:
        await update.message.reply_text(
            f"""На вашей стене обнаружен дефект: {json_answer['defect_type']}.\n
**Рекомендации по ремонту:** {json_answer['suggestions']}\n
Но всегда лучше провести консультацию со специалистом""",
            parse_mode='Markdown',
        )
    else:
        await update.message.reply_text(
            'Ваша стена в хорошем состоянии',
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    logger.info(f'{user.first_name} sent text: {text}')

    raw_model_text = await vllm_model.process_text(text)
    prep_model_text = raw_model_text.replace('#', '')

    await update.message.reply_text(
        prep_model_text, parse_mode='Markdown',
    )


def setup_handlers(application: Application) -> None:
    """Setup all handlers for the application."""
    # Command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))

    # Add handler for user messages
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT, handle_text))
