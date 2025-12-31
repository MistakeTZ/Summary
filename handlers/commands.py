import asyncio
from datetime import datetime
from os import path

from aiogram.filters import Command, CommandStart, Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hlink

from database.model import DB
from handlers import kb
from tasks.loader import dp, sender
from tasks.states import UserState

from ..utils.protfolio import send_portfolio


# Команда старта бота
@dp.message(CommandStart())
async def command_start_handler(msg: Message, state: FSMContext) -> None:
    id = msg.from_user.id
    print(id)
    user = DB.get("select id from users where telegram_id = ?", [id])
    if user:
        await sender.message_with_times("hi_again", msg.from_user.first_name, 0.06, msg)
    else:
        DB.commit(
            "insert into users (telegram_id, name, registered) values (?, ?, ?)",
            [id, msg.from_user.full_name, datetime.now()],
        )
        await sender.message_with_times("hi", msg.from_user.first_name, 0.06, msg)

    # await message(id, msg, "how_feels", kb.split_text("emotions"), nodelete=True)
    license_ = sender.text("license").split("лицензионное соглашение")
    await msg.answer(
        text=license_[0]
        + hlink(
            "лицензионное соглашение",
            "https://ru.wikipedia.org/wiki/Пользовательское_соглашение",
        )
        + license_[1],
        reply_markup=kb.reply("accept"),
        # reply_markup=kb.link("Лицензионное соглашение", "https://ru.wikipedia.org/wiki/Пользовательское_соглашение"),
        disable_web_page_preview=True,
    )
    await state.set_state(UserState.license)


# Команда меню
@dp.message(Command("menu"))
async def command_settings(msg: Message, state: FSMContext) -> None:
    await sender.message(
        msg,
        "menu",
        kb.menu(),
        state=state,
        new_state=UserState.default,
        photo=path.join("support", "assets", "oleg.jpg"),
        nodelete=True,
        set_menu=True,
    )


# Отправить сообщение с задержками между символами
async def send_message_with_times(message, name, delay, msg: Message):
    string = sender.text(message, name)
    new_mes = await msg.answer(string[0])
    await msg.delete()
    await asyncio.sleep(delay)

    for i in range(1, len(string) - 1, 2):
        if string[i + 1] != " ":
            await new_mes.edit_text(string[: i + 1])
        await asyncio.sleep(delay)

    await new_mes.edit_text(string)


# Команда портфолио
@dp.message(Command("portfolio"))
async def portfolio_command(msg: Message, state: FSMContext) -> None:
    await send_portfolio(msg.from_user.id)
