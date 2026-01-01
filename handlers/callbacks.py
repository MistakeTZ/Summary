import asyncio
import logging
from os import path

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, FSInputFile
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.utils.markdown import hlink

from database.model import Currency, User
from tasks import kb
from tasks.config import get_config
from tasks.loader import bot, dp, sender, session
from tasks.states import UserState
from utils import currency, payment
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


# Выбран эмодзи
@dp.callback_query(F.data.startswith("emotions_"))
async def emotion_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    emote = sender.text("emotions").split().index(clbck.data[-1])
    await clbck.message.answer(clbck.data[-1])
    await sender.message(clbck, "emotions_" + str(emote), nodelete=True)

    await asyncio.sleep(2)
    license_ = sender.text("license").split("лицензионное соглашение")
    await clbck.message.answer(
        text=license_[0]
        + hlink("лицензионное соглашение", "https://youtu.be/dQw4w9WgXcQ")
        + license_[1],
        reply_markup=kb.reply("accept"),
        disable_web_page_preview=True,
    )
    await state.set_state(UserState.license)


# Выбор в меню
@dp.callback_query(F.data.startswith("menu_"))
async def menu_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    name = clbck.data[clbck.data.index("_") + 1 :]
    func = get_config("menu", name, "function")

    if not func:
        await clbck.answer(sender.text("not_realize"))
    else:
        # get the function by name
        method = eval(func)

        # call it like a regular function later
        args = [clbck, state]
        await method(*args)


# Заказ бота
async def zakaz(clbk: CallbackQuery, *args):
    await sender.message(
        clbk, "about_zakaz", kb.two_buttons("make_zakaz", "make_zakaz", "back", "back")
    )


# Составление графа
async def graph(clbck: CallbackQuery, *args):
    await sender.message(clbck, "graphs")
    photos = [
        InputMediaPhoto(
            media=FSInputFile(
                path=path.join("support", "assets", "matplot_{}.png".format(num))
            ),
            caption="matplot_" + str(num),
        )
        for num in range(1, 4)
    ]
    mes_id = await clbck.message.answer_media_group(media=photos)

    await asyncio.sleep(2)
    await sender.message(clbck, "also", kb.buttons(True, "back"))


# Форматирование текста
async def formatting(clbk: CallbackQuery, *args):
    await clbk.message.edit_reply_markup()
    mes_id = await clbk.message.answer(
        text=sender.text("formatting", hlink("ссылка", "t.me/o_l_ebedev")),
        reply_markup=kb.buttons(True, "back"),
        disable_web_page_preview=True,
    )


# Оплата и поддержка
async def help(clbk: CallbackQuery, *args):
    await sender.message(clbk, "to_pay", kb.buttons(True, "back"))


# Оформления заказа
@dp.callback_query(F.data == "make_zakaz")
async def zakaz_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    await sender.message(
        clbck, "write_product", kb.buttons(True, "back"), state, UserState.product
    )


# Есть ли ТЗ
@dp.callback_query(F.data.startswith("tz_"))
async def zakaz_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    tz = clbck.data.split("_")[-1] == "y"
    user_id = DB.get(
        "select id from payments where telegram_id = ? order by registered desc",
        [clbck.from_user.id],
        True,
    )
    DB.commit("update payments set have_tz = ? where id = ?", [tz, user_id[0]])
    await sender.message(
        clbck, "need_to_pay", kb.pay_kb(), state, UserState.default, get_env("cost")
    )


# Согласие на оплату
@dp.callback_query(F.data == "predoplata")
async def zakaz_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    user_id = DB.get(
        "select id from payments where telegram_id = ? order by registered desc",
        [clbck.from_user.id],
        True,
    )
    await payment.real_pay(clbck.from_user.id, user_id[0])


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
    except Exception as e:
        logging.error(e)
        await sender.message(user_id, "price_error", kb.buttons(True, "back"))
    finally:
        await clbck.message.delete()


# Встроенный браузер
async def browser(clbk: CallbackQuery, *args):
    await sender.message(clbk, "site", kb.site())


# Сбор информации
async def info(clbk: CallbackQuery, state, *args):
    await sender.message(clbk, "how_your_name", None, state, UserState.name)


# Выбор пола
@dp.callback_query(F.data.startswith("sex_"))
async def currency_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    user.users[str(clbck.from_user.id)].sex = clbck.data
    await sender.message(clbck, "write_phone", kb.phone(), state, UserState.phone)


# Нет питомца
@dp.callback_query(F.data == "skip_photo", UserState.photo)
async def photo_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    user.users[str(clbck.from_user.id)].photo = -1
    await sender.message(clbck, "no_photo", None, state, UserState.email)
