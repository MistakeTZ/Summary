import logging

from database.model import Payment
from tasks import kb
from tasks.config import get_config
from tasks.loader import sender, session


async def send_menu(user_id):
    payment = session.query(Payment).filter_by(telegram_id=user_id).first()
    if payment:
        payment_text = "Приватный контент"
    else:
        payment_text = "Тест оплаты"
    try:
        await sender.send_cached_media(
            user_id,
            "photo",
            get_config("main_photo"),
            "menu",
            kb.menu(payment_text),
        )
    except Exception as e:
        logging.error(e)
        await sender.send_media(
            user_id,
            "photo",
            "oleg.jpg",
            "menu",
            kb.menu(payment_text),
        )
