import io
import json

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import config
from bot.handlers.vllm import VLM
from utils.logger import init_logger


logger = init_logger(__name__)
vllm_model = VLM(config)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    photo_file = await update.message.photo[-1].get_file()

    photo_buffer = io.BytesIO(b"")
    await photo_file.download_to_memory(photo_buffer)

    logger.info(f"{user.first_name} sent a photo")
    model_answer = await vllm_model.process_image(photo_buffer)

    model_answer = model_answer.replace('json', '').replace('```', '').strip()

    # Parse json
    json_answer = json.loads(model_answer)

    if json_answer['is_damaged']:
        await update.message.reply_text(
            f"На вашей стене обнаружен дефект: {json_answer['defect_type']}.\n\n**Рекомендации по ремонту:** {json_answer['suggestions']}\n\nНо всегда лучше провести консультацию со специалистом",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "Ваша стена в хорошем состоянии"
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    logger.info(f"{user.first_name} sent text: {text}")

    raw_model_text = await vllm_model.process_text(text)
    prep_model_text = raw_model_text.replace('#', '')

    await update.message.reply_text(
        prep_model_text, parse_mode="Markdown",
    )
