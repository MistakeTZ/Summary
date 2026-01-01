from datetime import datetime

from aiogram import F
from aiogram.types import Message, PreCheckoutQuery

from database.model import Payment
from tasks import kb
from tasks.loader import bot, dp, sender, session, settings


# Согласие на оплату
@dp.pre_checkout_query()
async def pre_checkout_query_handler(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)


# Успешная оплата
@dp.message(F.successful_payment)
async def successful_payment_handler(msg: Message):
    successful_payment = msg.successful_payment
    user_id = msg.from_user.id

    await sender.message(user_id, "succeful_payment", kb.menu("private_content"))
    payment = Payment(
        telegram_id=user_id,
        product=successful_payment.invoice_payload,
        payment_amount=successful_payment.total_amount,
        provider_payment_charge_id=successful_payment.provider_payment_charge_id,
        telegram_payment_charge_id=successful_payment.telegram_payment_charge_id,
    )
    session.add(payment)
    session.commit()


# Оплата
async def pay(user_id):
    await bot.send_invoice(
        user_id,
        "Проверка оплаты",
        sender.text("description"),
        "test_payment",
        "RUB",
        [{"label": "Руб", "amount": 100 * 100}],
        provider_token=settings.shop_token,
    )
