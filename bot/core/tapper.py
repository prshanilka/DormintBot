import asyncio
import heapq
import math
from random import randint

import aiohttp
from aiohttp_proxy import ProxyConnector
from bot.api.auth import generate_token
from bot.api.farm import claim_farm, start_farm
from bot.api.info import get_info
from pyrogram import Client

from bot.config import settings
from bot.utils.logger import logger
from bot.exceptions import InvalidSession

from bot.utils.scripts import get_headers, is_jwt_valid
from bot.utils.tg_web_data import get_tg_web_data
from bot.utils.proxy import check_proxy


class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client

    async def run(self, proxy: str | None) -> None:
        token = ""
        headers = get_headers(name=self.tg_client.name)
        Fetched = False
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None
        http_client = aiohttp.ClientSession(
            headers=headers, connector=proxy_conn
        )

        if proxy:
            await check_proxy(
                http_client=http_client,
                proxy=proxy,
                session_name=self.session_name,
            )

        tg_web_data = await get_tg_web_data(
            tg_client=self.tg_client,
            proxy=proxy,
            session_name=self.session_name,
        )

        while True:
            try:
                if http_client.closed:
                    if proxy_conn:
                        if not proxy_conn.closed:
                            proxy_conn.close()

                    proxy_conn = (
                        ProxyConnector().from_url(proxy) if proxy else None
                    )

                    http_client = aiohttp.ClientSession(
                        headers=headers, connector=proxy_conn
                    )

                token = await generate_token(tg_client=self.tg_client, bot_username="dormint_bot")
                if not token:
                    logger.error(f'{self.session_name} | Getting token failed')
                    if Fetched:
                        break
                    logger.info(
                        f'{self.session_name} | Sleep 120s'
                    )
                    await asyncio.sleep(delay=120)
                    Fetched = True
                    continue

                info = await get_info(http_client=http_client, auth_token=token)
                info_status = info.get("status")
                if not info_status == 'ok':
                    sleep_time = 120
                    if info_status == 'sleep':
                        sleep_time = info.get("sleep", 120)
                    logger.info(f'Sleep {sleep_time}s')
                    await asyncio.sleep(delay=sleep_time)

                logger.info(
                    f'Your current balance is: {info["sleepcoin_balance"]}')
                farming_left = info.get("farming_left")
                # farming_speed = info.get("farming_speed")
                farming_status = info.get("farming_status")

                if farming_status == "farming_status_started":
                    # farming_left_seconds = farming_left / farming_speed
                    farming_left_seconds_ceil = math.ceil(farming_left) + randint(
                        a=30,
                        b=120,
                    )
                    logger.info(
                        f'{self.session_name} | Sleep until farm finishes {farming_left_seconds_ceil:,}s'
                    )
                    await asyncio.sleep(delay=farming_left_seconds_ceil)
                    continue

                if farming_status == "farming_status_finished":
                    claim_farm_data = await claim_farm(http_client=http_client, auth_token=token)
                    status = claim_farm_data.get("status")
                    if (status == "ok"):
                        logger.info(
                            f'{self.session_name} | Farm value claimed'
                        )
                    else:
                        logger.error(
                            f'{self.session_name} | Farm value claim error'
                        )
                        await asyncio.sleep(delay=60)
                        continue
                    sleep_after_claim = randint(a=3, b=30)
                    logger.info(f'Sleep {sleep_after_claim}s')
                    await asyncio.sleep(delay=sleep_after_claim)

                if farming_status == "farming_status_not_started":
                    claim_farm_data = await start_farm(http_client=http_client, auth_token=token)
                    status = claim_farm_data.get("status")
                    if (status == "ok"):
                        logger.info(
                            f'{self.session_name} | Farm started'
                        )
                    else:
                        logger.error(
                            f'{self.session_name} | Farm start error'
                        )
                        await asyncio.sleep(delay=60)
                        continue

                await http_client.close()
                if proxy_conn:
                    if not proxy_conn.closed:
                        proxy_conn.close()

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f'{self.session_name} | Unknown error: {error}')
                await asyncio.sleep(delay=1200)

            else:
                sleep_between_clicks = randint(
                    a=settings.SLEEP_BETWEEN_TAP[0],
                    b=settings.SLEEP_BETWEEN_TAP[1],
                )
                logger.info(f'Sleep {sleep_between_clicks}s')
                await asyncio.sleep(delay=sleep_between_clicks)


async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f'{tg_client.name} | Invalid Session')
