import asyncio
import logging

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from aiogram.types.callback_query import CallbackQuery

from database.model import Currency, User
from tasks import kb
from tasks.loader import bot, dp, sender, session
from utils import currency
from utils.menu import send_menu
from utils.protfolio import send_project


@dp.callback_query(F.data == "confirm_license")
async def confirm_license(clbck: CallbackQuery):
    user_id = clbck.from_user.id
    await sender.edit_message(
        clbck.message,
        "license",
        None,
        sender.text("accepted"),
    )
    user = session.query(User).filter_by(telegram_id=user_id).first()
    if user:
        user.get_license = True
        session.commit()

    await send_menu(user_id)
    await asyncio.sleep(2)
    await clbck.message.delete()


@dp.callback_query(F.data.startswith("project"))
async def project_handler(clbck: CallbackQuery):
    data = clbck.data.split("_")
    await send_project(
        clbck.from_user.id,
        int(data[1]),
        int(data[2]),
        clbck.message,
    )


# Возвращение в меню
@dp.callback_query(F.data == "back")
async def menu_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    await send_menu(clbck.from_user.id)
    await clbck.message.delete()


# Выбор актива
@dp.callback_query(F.data.startswith("token_"))
async def currency_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    token = session.query(Currency).filter_by(token=clbck.data.split("_")[1]).first()
    user_id = clbck.from_user.id
    try:
        buffer, last_price = currency.make_graph(token.token, token.name)

        await bot.send_photo(
            user_id,
            BufferedInputFile(buffer.read(), f"{token.token}.jpg"),
            caption=sender.text("price", token.name, last_price),
            reply_markup=kb.buttons(True, "back"),
        )
        buffer.close()
    except Exception as e:
        logging.error(e)
        await sender.message(user_id, "price_error", kb.buttons(True, "back"))
    finally:
        await clbck.message.delete()
