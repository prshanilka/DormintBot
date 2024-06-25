import asyncio
from urllib.parse import  parse_qs, urlparse
from pyrogram import Client
from typing import Optional, List
from pyrogram.types import Message, InlineKeyboardButton
from bot.utils.logger import logger


async def get_last_message(app: Client, bot_username: str) -> Optional[Message]:
    """Get the last message from the bot."""
    async for message in app.get_chat_history(bot_username, limit=1):
        return message
    return None


def check_message_for_url(message: Message) -> Optional[str]:
    """Check if the message contains the specific inline keyboard structure with a URL."""
    if hasattr(message, "reply_markup") and message.reply_markup:
        inline_keyboard: List[List[InlineKeyboardButton]
                              ] = message.reply_markup.inline_keyboard
        if inline_keyboard and inline_keyboard[0][0].web_app and inline_keyboard[0][0].web_app.url:
            return inline_keyboard[0][0].web_app.url
    return None


async def send_start_command(app: Client, bot_username: str) -> None:
    """Send the /start command to the bot."""
    await app.send_message(bot_username, "/start")
    logger.info(f'Sleep 30s')
    await asyncio.sleep(delay=30)


async def extract_tg_auth_token(url: str) -> str:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Extract the tg_auth_token
    tg_auth_token = query_params.get("tg_auth_token", [None])[0]
    return tg_auth_token


async def generate_token(tg_client: Client, bot_username: str) -> str | None:
    
    async with tg_client:
        # Get the last message from the bot
        last_message = await get_last_message(tg_client, bot_username)
        if not last_message:
            print("No messages found.")
            return

        url = check_message_for_url(last_message)
        if url:
            extracted_token = await extract_tg_auth_token(url)
            return extracted_token
        else:
            logger.info(
                f'Required structure not found, sending /start'
            )
            await send_start_command(tg_client, bot_username)

            # Recheck the last message
            last_message = await get_last_message(tg_client, bot_username)
            if not last_message:
                logger.error(
                    f'No messages found after sending /start.'
                )
                return None

            url = check_message_for_url(last_message)
            if url:
                extracted_token = await extract_tg_auth_token(url)
                return extracted_token
            else:
                logger.error(
                    f'URL not found even after sending /start.'
                )
                return None
