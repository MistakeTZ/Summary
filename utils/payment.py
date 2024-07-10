from aiogram import F
from aiogram.types import Message, PreCheckoutQuery
from loader import dp, bot
from config import get_env

import utils.kb as kb
from support.messages import get_text, send_message


# Согласие на оплату
@dp.pre_checkout_query()
async def pre_checkout_query_handler(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)


# Успешная оплата
@dp.message(F.successful_payment)
async def successful_payment_handler(msg: Message):
    await send_message(msg, "succeful_payment", kb.buttons("back"), nodelete=True)


# Оплата
async def pay(id):
    await bot.send_invoice(id, "Проверка оплаты", get_text("description"), "payload", "RUB", 
                           [{"label": "Руб", "amount": int(get_env("pay")) * 100}], provider_token=get_env("shop_token"))
