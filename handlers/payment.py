from datetime import datetime

from aiogram import F
from aiogram.types import Message, PreCheckoutQuery
from aiogram.utils.markdown import hlink

from database.model import Payment
from tasks import kb
from tasks.loader import bot, dp, settings


# Согласие на оплату
@dp.pre_checkout_query()
async def pre_checkout_query_handler(query: PreCheckoutQuery):
    payload = query.invoice_payload
    if payload == "payload" or payload == "test_payment":
        await bot.answer_pre_checkout_query(query.id, ok=True)

    elif payload.startswith("predoplata_"):
        zapis_id = int(payload.split("_")[1])
        DB.commit(
            "update payments set payment_id = ?, payment_amount = ?, payment_date = ? where id = ?",
            [query.id, query.total_amount, datetime.now(), zapis_id],
        )
        await bot.answer_pre_checkout_query(query.id, ok=True)


# Успешная оплата
@dp.message(F.successful_payment)
async def successful_payment_handler(msg: Message):
    successful_payment = msg.successful_payment

    if (
        successful_payment.invoice_payload == "payload"
        or successful_payment.invoice_payload == "test_payment"
    ):
        await sender.message(msg, "succeful_payment", kb.buttons("back"))
    else:
        await sender.message(
            msg, "succeful_predoplata", kb.buttons("back", "back_no_history")
        )
        zapis_id = int(successful_payment.invoice_payload.split("_")[1])
        user_data = DB.get(
            "select telegram_id, have_tz, product, payment_id, payment_amount from payments where id = ?",
            [zapis_id],
            True,
        )
        link = hlink(msg.from_user.first_name, "tg://user?id=" + str(user_data[0]))
        await bot.sender.message(
            get_env("manager"),
            sender.text(
                "to_manager",
                link,
                zapis_id,
                user_data[2],
                "есть" if user_data[1] else "нет",
                user_data[4] // 100,
                user_data[3],
            ),
        )

        DB.commit(
            "update payments set payment_confirmed = ?, provider_payment_charge_id = ?, telegram_payment_charge_id = ? where id = ?",
            [
                True,
                successful_payment.provider_payment_charge_id,
                successful_payment.telegram_payment_charge_id,
                zapis_id,
            ],
        )


# Оплата
async def pay(id):
    mes_id = await bot.send_invoice(
        id,
        "Проверка оплаты",
        sender.text("description"),
        "test_payment",
        "RUB",
        [{"label": "Руб", "amount": int(get_env("pay")) * 100}],
        provider_token=settings.shop_token,
    )


# Оплата реальная
async def real_pay(user_id, zapis_id):
    invoice = await bot.send_invoice(
        user_id,
        "Предоплата бота",
        sender.text("pred_desc"),
        "predoplata_" + str(zapis_id),
        "RUB",
        [{"label": "Руб", "amount": int(get_env("cost")) * 100}],
        provider_token=get_env("shop_real_token"),
    )
