import aiohttp
from typing import Any
from bot.api.http import make_post_request


async def start_farm(http_client: aiohttp.ClientSession, auth_token: str) -> dict[Any, Any]:
    response_json = await make_post_request(
        http_client,
        'https://api.dormint.io/tg/farming/start',
        {"auth_token": auth_token},
        'start farm',
    )
    return response_json


async def claim_farm(
    http_client: aiohttp.ClientSession,
    auth_token: str
) -> dict[Any, Any]:
    response_json = await make_post_request(
        http_client,
        'https://api.dormint.io/tg/farming/claimed',
        {"auth_token": auth_token},
        'claim farm',
    )
    return response_json
