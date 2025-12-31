import logging

from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.model import User
from tasks import kb
from tasks.config import get_config
from tasks.loader import dp, sender, session
from tasks.states import UserState
from utils.menu import send_menu
from utils.protfolio import send_project


@dp.message(CommandStart())
async def command_start_handler(msg: Message, state: FSMContext) -> None:
    user_id = msg.from_user.id
    user = session.query(User).filter_by(telegram_id=user_id).first()
    command = msg.text.split()[-1] if msg.text != "/start" else None

    if not user:
        logging.info(f"New user: {user_id}")
        user = User(
            telegram_id=user_id,
            name=msg.from_user.full_name,
            username=msg.from_user.username,
        )
        if user_id in get_config("admins"):
            user.role = "admin"
        session.add(user)
        session.commit()
        key = "hi_again"
    else:
        key = "hi"

    if not command:
        await sender.message(user_id, "greetings")
        await sender.broadcasting_message(
            user_id,
            0.06,
            key,
            None,
            msg.from_user.first_name,
        )

    await state.set_state(UserState.default)
    if msg.text.split()[-1] == "portfolio":
        await send_project(user_id)
        return
    if not user.get_license:
        await sender.message(
            user_id,
            "license",
            kb.buttons(True, "accept", "confirm_license"),
            "",
        )
        return

    await send_menu(user_id)
    await msg.delete()


# Команда меню
@dp.message(Command("menu"))
async def command_settings(msg: Message, state: FSMContext) -> None:
    await send_menu(msg.from_user.id)
    await msg.delete()


# Команда портфолио
@dp.message(Command("portfolio"))
async def portfolio_command(msg: Message, state: FSMContext) -> None:
    await send_project(msg.from_user.id)
