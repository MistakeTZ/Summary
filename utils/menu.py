import logging

from tasks import kb
from tasks.config import get_config
from tasks.loader import sender


async def send_menu(user_id):
    try:
        await sender.send_cached_media(
            user_id,
            "photo",
            get_config("main_photo"),
            "menu",
            kb.menu(),
        )
    except Exception as e:
        logging.error(e)
        await sender.send_media(
            user_id,
            "photo",
            "oleg.jpg",
            "menu",
            kb.menu(),
        )
