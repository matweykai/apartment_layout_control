import os
from dataclasses import dataclass
from enum import Enum, auto

class ModelProvider(Enum):
    MISTRAL = auto()
    OPENAI = auto()

class RunMode(Enum):
    POLLING = auto()
    WEBHOOK = auto()
    SERVERLESS = auto()

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Bot running mode
    RUN_MODE: RunMode = RunMode[os.getenv("RUN_MODE", "WEBHOOK").upper()]
    
    # Webhook settings (used when RUN_MODE=webhook)
    WEBHOOK_HOST: str = os.getenv("WEBHOOK_HOST", None)  # e.g., "https://your-domain.com"
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", None)
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", None)
    WEBHOOK_PORT: int = int(os.getenv("PORT", "80"))
    WEBHOOK_LISTEN: str = os.getenv("WEBHOOK_LISTEN", "0.0.0.0")

    # Model settings
    MODEL_PROVIDER: ModelProvider = ModelProvider[os.getenv("MODEL_PROVIDER", "MISTRAL").upper()]
    
    # Mistral settings
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_VISUAL_MODEL: str = os.getenv("MISTRAL_VISUAL_MODEL", "pixtral-12b-2409")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "open-mistral-nemo")
    MISTRAL_API_BASE: str = os.getenv("MISTRAL_API_BASE", "https://api.mistral.ai/v1")
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-vision-preview")
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    def __post_init__(self):
        """Validate the configuration after initialization"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        if self.RUN_MODE not in [RunMode.POLLING, RunMode.WEBHOOK, RunMode.SERVERLESS]:
            raise ValueError("RUN_MODE must be either 'polling', 'webhook', or 'serverless'")
        
        if self.RUN_MODE == RunMode.WEBHOOK and not self.WEBHOOK_HOST:
            raise ValueError("WEBHOOK_HOST is required when RUN_MODE is 'webhook'")

        # Validate model-specific settings
        if self.MODEL_PROVIDER == ModelProvider.MISTRAL and not self.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY environment variable is required when using Mistral")
            
        if self.MODEL_PROVIDER == ModelProvider.OPENAI and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required when using OpenAI")

# Create the global config instance
config = Config()
