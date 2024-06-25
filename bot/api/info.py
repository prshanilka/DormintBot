
import aiohttp
from typing import Any
from bot.api.http import make_post_request


async def get_info(
    http_client: aiohttp.ClientSession,
    auth_token: str
) -> dict[Any, Any] | Any:
    response_json = await make_post_request(
        http_client,
        'https://api.dormint.io/tg/farming/status',
        {"auth_token": auth_token},
        'farm status',
        sleep=1200
    )
    return response_json
