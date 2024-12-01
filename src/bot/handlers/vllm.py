import base64
import io

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage

from bot.config import Config, ModelProvider
from bot.handlers.prompts import get_prompt, PromptType
from utils.logger import init_logger


class VLM:
    def __init__(self, config: Config):
        self._vision_prompt = get_prompt(PromptType.IMAGE)
        self._text_prompt = ChatPromptTemplate([('system', get_prompt(PromptType.TEXT)), ('user', '{input}')])
        self._logger = init_logger(self.__class__.__name__)

        if config.MODEL_PROVIDER == ModelProvider.OPENAI:
            self._model = ChatOpenAI(
                model=config.OPENAI_MODEL,
                openai_api_key=config.OPENAI_API_KEY,
                openai_api_base=config.OPENAI_API_BASE,
            )
        elif config.MODEL_PROVIDER == ModelProvider.MISTRAL:
            self._model = ChatMistralAI(
                model=config.MISTRAL_VISUAL_MODEL,
                mistral_api_key=config.MISTRAL_API_KEY,
                mistral_api_base=config.MISTRAL_API_BASE,
            )
        else:
            raise ValueError(f"Unsupported model provider: {config.MODEL_PROVIDER}")

    async def process_image(self, image_bytes: io.BytesIO) -> str:
        image_bytes.seek(0)
        prep_image = base64.b64encode(image_bytes.read()).decode("UTF-8")

        messages = [
            HumanMessage(
                content=[
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{prep_image}",
                    },
                    {"type": "text", "text": self._vision_prompt},
                ]
            ),
        ]

        try:
            response = await self._model.ainvoke(messages)
            self._logger.debug(f"Model answer: {response.content}")
        except Exception as ex:
            self._logger.error(f"Error during vision model request. Info: {ex}")
            raise

        return response.content
    
    async def process_text(self, user_text: str) -> str:
        llm_chain = self._text_prompt | self._model

        try:
            response = await llm_chain.ainvoke(input=user_text)
            self._logger.debug(f"Model answer: {response.content}")
        except Exception as ex:
            self._logger.error(f"Error during vision model request. Info: {ex}")
            raise

        return response.content
