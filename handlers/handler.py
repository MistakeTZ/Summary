import asyncio

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hlink

import tasks.kb as kb
from tasks.loader import bot, dp, sender
from tasks.states import UserState
from utils.menu import send_menu
from utils.payment import pay
from utils.protfolio import send_project


@dp.message(F.text == sender.text("my_cases"))
async def cases_handler(msg: Message):
    await send_project(msg.from_user.id)


@dp.message(F.text == "private_content")
async def cases_handler(msg: Message):
    await sender.message(msg.from_user.id, "private")


@dp.message(F.text == sender.text("pay_test"))
async def payment_text_handler(msg: Message):
    user_id = msg.from_user.id
    await sender.message(user_id, "text_payment")
    await asyncio.sleep(2)
    await sender.message(user_id, "test_payment")
    await pay(user_id)


@dp.message(F.text == sender.text("database"))
async def database_handler(msg: Message):
    user_id = msg.from_user.id
    await sender.message(
        user_id,
        "databases",
        kb.buttons(True, "back"),
    )


@dp.message(F.text == sender.text("course"))
async def course_handler(msg: Message):
    user_id = msg.from_user.id
    await sender.message(user_id, "choose_currency", kb.currency())


@dp.message(F.text == sender.text("format"))
async def format_handler(msg: Message):
    user_id = msg.from_user.id
    await sender.message(
        user_id,
        "formatting",
        kb.buttons(True, "back"),
    )


@dp.message(F.text == sender.text("embedded_browser"))
async def browser_handler(msg: Message):
    user_id = msg.from_user.id
    await sender.message(user_id, "site", kb.site())


@dp.message(F.text == sender.text("work_conditions"))
async def work_handler(msg: Message):
    user_id = msg.from_user.id
    await sender.message(user_id, "to_pay", kb.buttons(True, "back"))


@dp.message(F.text == sender.text("anket"))
@dp.callback_query(F.data == "anket")
async def anket_handler(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    await sender.message(user_id, "how_your_name", kb.remove())
    await state.set_state(UserState.info)
    await state.set_data({"state": "name"})

    if not isinstance(msg, Message):
        await msg.message.edit_reply_markup()


@dp.message(UserState.info)
async def info_handler(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    data = await state.get_data()

    match data.get("state"):
        case "name":
            await sender.message(
                user_id,
                "your_gender",
                kb.reply_table(2, *sender.text("genders").split("/")),
                msg.text,
            )
            data["name"] = msg.text
            data["state"] = "gender"

        case "gender":
            try:
                gender = sender.text("genders").split("/").index(msg.text)
            except ValueError:
                await sender.message(
                    user_id,
                    "your_gender",
                    kb.reply_table(2, *sender.text("genders").split("/")),
                    data["name"],
                )
                return
            await sender.message(
                user_id,
                "write_phone",
                kb.phone(),
            )
            data["gender"] = msg.text
            data["state"] = "phone"

        case "phone":
            if not msg.contact:
                await sender.message(
                    user_id,
                    "write_phone",
                    kb.phone(),
                )
                return
            await sender.message(
                user_id,
                "your_email",
                kb.remove(),
            )
            data["phone"] = msg.contact.phone_number
            data["state"] = "email"

        case "email":
            if not msg.entities:
                await sender.message(
                    user_id,
                    "wrong_email",
                    kb.remove(),
                )
                return
            ent = msg.entities[0]
            if ent.type != "email":
                await sender.message(
                    user_id,
                    "wrong_email",
                    kb.remove(),
                )
                return

            data["email"] = msg.text[ent.offset : ent.offset + ent.length]
            data["state"] = "message"
            await sender.message(
                user_id,
                "write_message",
            )

        case "message":
            if not msg.text:
                await sender.message(
                    user_id,
                    "write_message",
                )
                return
            else:
                data["message"] = msg.html_text
                await sender.message(
                    user_id,
                    "confirm_data",
                    kb.buttons(True, "confirm", "confirm_data", "edit", "anket"),
                    user_id,
                    data["name"],
                    data["gender"],
                    data["phone"],
                    data["email"],
                    msg.html_text,
                )

    await state.set_data(data)


@dp.message(Command("menu"))
@dp.message()
async def command_settings(msg: Message) -> None:
    await send_menu(msg.from_user.id)
