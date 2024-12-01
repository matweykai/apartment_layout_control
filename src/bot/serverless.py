import json
from typing import Any, Dict
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application
from utils.logger import init_logger

logger = init_logger(__name__)

def init_app(application: Application) -> FastAPI:
    """Initialize FastAPI application."""
    app = FastAPI()
    
    @app.post("/")
    async def handle_webhook(request: Request) -> Dict[str, Any]:
        """Handle webhook POST requests from Yandex Cloud API Gateway."""
        try:
            event = await request.json()
            logger.info(f"Received webhook event: {event}")
            
            # Create a list to store coroutines
            tasks = []
            
            # Process messages from queue
            if 'messages' in event:
                for message in event['messages']:
                    if 'details' in message and 'message' in message['details']:
                        body = message['details']['message']['body']
                        update_data = json.loads(body)
                        logger.info(f"Processing update data: {update_data}")
                        
                        # Process update with the bot application
                        update = Update.de_json(update_data, application.bot)
                        if update:
                            # Add task to list instead of awaiting immediately
                            tasks.append(application.process_update(update))
            
            # Wait for all updates to be processed
            if tasks:
                await asyncio.gather(*tasks)
            
            return {"statusCode": 200, "body": "OK"}
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            return {"statusCode": 500, "body": str(e)}

    return app
