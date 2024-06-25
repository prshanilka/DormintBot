import asyncio
from urllib.parse import unquote

from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import (
    AuthKeyUnregistered,
    FloodWait,
    Unauthorized,
    UserDeactivated,
)
from pyrogram.raw.functions.messages import RequestWebView

from bot.exceptions import InvalidSession
from bot.utils.logger import logger


async def get_tg_web_data(
    tg_client: Client, proxy: str | None, session_name: str
) -> str:
    if proxy:
        proxy = Proxy.from_str(proxy)
        proxy_dict = dict(
            scheme=proxy.protocol,
            hostname=proxy.host,
            port=proxy.port,
            username=proxy.login,
            password=proxy.password,
        )
    else:
        proxy_dict = None

    tg_client.proxy = proxy_dict

    try:
        if not tg_client.is_connected:
            try:
                await tg_client.connect()
            except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                raise InvalidSession(session_name)

        dialogs = tg_client.get_dialogs()
        async for dialog in dialogs:
            if (
                dialog.chat
                and dialog.chat.username
                and dialog.chat.username == 'dormint_bot'
            ):
                break

        while True:
            try:
                peer = await tg_client.resolve_peer('dormint_bot')
                break
            except FloodWait as fl:
                fls = fl.value

                logger.warning(f'{session_name} | FloodWait {fl}')
                fls *= 2
                logger.info(f'{session_name} | Sleep {fls}s')

                await asyncio.sleep(fls)

        web_view = await tg_client.invoke(
            RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=False,
                url='https://dormint.io/',
            )
        )

        auth_url = web_view.url
        tg_web_data = unquote(
            string=unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split(
                    '&tgWebAppVersion', maxsplit=1
                )[0]
            )
        )

        if tg_client.is_connected:
            await tg_client.disconnect()

        return tg_web_data

    except InvalidSession as error:
        raise error

    except Exception as error:
        logger.error(
            f'{session_name} | Unknown error during Authorization: {error}'
        )
        await asyncio.sleep(delay=3)
