import asyncio
import os
from datetime import datetime

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.markdown import hlink

import tasks.kb as kb
from tasks.loader import bot, dp, sender
from tasks.states import UserState
from utils.payment import pay
from utils.protfolio import send_project


@dp.message(F.text == "Мои кейсы")
async def cases_handler(msg: Message):
    await send_project(msg.from_user.id)


@dp.message(F.text == "Тест оплаты")
async def payment_text_handler(msg: Message):
    user_id = msg.from_user.id
    await sender.message(user_id, "text_payment")
    await asyncio.sleep(2)
    await sender.message(user_id, "test_payment")
    await pay(user_id)


# Установка электронной почты
@dp.message(UserState.email)
async def profile(msg: Message, state: FSMContext):
    id = msg.from_user.id
    email = ""
    if msg.entities:
        ent = msg.entities[0]
        if ent.type == "email":
            email = msg.text[ent.offset : ent.offset + ent.length]
    if not email:
        await sender.message(msg, "wrong_email")
        return

    user.users[str(id)].email = email
    await sender.message(msg, "email_given", None, state, UserState.default)
    await asyncio.sleep(2)
    use = user.users[str(id)]
    await sender.message(
        msg,
        "your_data",
        None,
        None,
        None,
        hlink(use.name, "tg://user?id=" + str(use.id)),
        sender.text(use.sex).lower(),
        use.phone,
        use.email,
        "" if use.photo != -1 else "отсутствует",
    )
    if use.photo != -1:
        await bot.copy_message(id, id, use.photo)
    await asyncio.sleep(5)
    await sender.message(msg, "info_give", kb.buttons("back_to_menu", "back"))


# Ввод имени
@dp.message(UserState.name)
async def profile(msg: Message, state: FSMContext):
    id = msg.from_user.id
    user.add_user(id, msg.text)
    await sender.message(msg, "your_sex", kb.sex(), state, UserState.default, msg.text)


# Отправка телефона
@dp.message(UserState.phone)
async def profile(msg: Message, state: FSMContext):
    id = msg.from_user.id
    if msg.contact:
        user.users[str(id)].phone = msg.contact.phone_number
        await sender.message(
            msg, "phone_get", ReplyKeyboardRemove(), state, UserState.photo
        )
        await state.set_state(UserState.photo)
        await sender.message(msg, "send_photo", kb.buttons("skip", "skip_photo"))
    else:
        await sender.message(msg, "wrong_phone")


# Отправка фото
@dp.message(UserState.photo)
async def profile(msg: Message, state: FSMContext):
    id = msg.from_user.id
    if msg.photo:
        user.users[str(id)].photo = msg.message_id
        await sender.message(msg, "photo_sended", None, state, UserState.email)


# Ввод продукта
@dp.message(UserState.product, F.text)
async def profile(msg: Message, state: FSMContext):
    await sender.message(msg, "have_TZ", kb.two_buttons("yes", "tz_y", "no", "tz_n"))
    DB.commit(
        "insert into payments (telegram_id, product, registered) values (?, ?, ?)",
        [msg.from_user.id, msg.text, datetime.now()],
    )
