from aiogram import F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.types.reaction_type_emoji import ReactionTypeEmoji
from aiogram.utils.markdown import hlink
from loader import dp, bot

import os
from config import add_mes
import asyncio
from datetime import datetime

from database.model import DB
import utils.kb as kb
import utils.user as user
from support.messages import send_message, get_text
from states import UserState
    

# Установка электронной почты
@dp.message(UserState.email)
async def profile(msg: Message, state: FSMContext):
    id = msg.from_user.id
    email = ""
    if msg.entities:
        ent = msg.entities[0]
        if ent.type == "email":
            email = msg.text[ent.offset:ent.offset + ent.length]
    if not email:
        await send_message(msg, "wrong_email")
        return
    
    user.users[str(id)].email = email
    await send_message(msg, "email_given", None, state, UserState.default)
    await asyncio.sleep(2)
    use = user.users[str(id)]
    await send_message(msg, "your_data", None, None, None, 
                       hlink(use.name, "tg://user?id=" + str(use.id)),
                       get_text(use.sex).lower(),
                       use.phone,
                       use.email,
                       "" if use.photo != -1 else "отсутствует")
    if use.photo != -1:
        await bot.copy_message(id, id, use.photo)
    await asyncio.sleep(5)
    await send_message(msg, "info_give", kb.buttons("back_to_menu", "back"))

# Ввод имени
@dp.message(UserState.name)
async def profile(msg: Message, state: FSMContext):
    id = msg.from_user.id
    user.add_user(id, msg.text)
    await send_message(msg, "your_sex", kb.sex(), state, UserState.default, msg.text)


# Отправка телефона
@dp.message(UserState.phone)
async def profile(msg: Message, state: FSMContext):
    id = msg.from_user.id
    if msg.contact:
        user.users[str(id)].phone = msg.contact.phone_number
        await send_message(msg, "phone_get", ReplyKeyboardRemove(), state, UserState.photo)
        await state.set_state(UserState.photo)
        await send_message(msg, "send_photo", kb.buttons("skip", "skip_photo"))
    else:
        await send_message(msg, "wrong_phone")


# Отправка фото
@dp.message(UserState.photo)
async def profile(msg: Message, state: FSMContext):
    id = msg.from_user.id
    if msg.photo:
        user.users[str(id)].photo = msg.message_id
        await send_message(msg, "photo_sended", None, state, UserState.email)


# Подтверждение лицензии
@dp.message(UserState.license)
async def profile(msg: Message, state: FSMContext):
    if msg.text.lower() == get_text("accept").lower():
        await msg.react([ReactionTypeEmoji(emoji="👍")])
        photo = FSInputFile(path=os.path.join("support", "assets", "oleg.jpg"))
        await asyncio.sleep(1)

        mes_id = await msg.answer_photo(photo, reply_markup=ReplyKeyboardRemove())
        # add_mes(msg.from_user.id, mes_id.message_id)
        await send_message(msg, "license_menu", kb.menu(), None, None, get_text("menu"), nodelete=True, set_menu=True)
    else:
        await send_message(msg, "not_accept", nodelete=True)


# Ввод продукта
@dp.message(UserState.product, F.text)
async def profile(msg: Message, state: FSMContext):
    await send_message(msg, "have_TZ", kb.two_buttons("yes", "tz_y", "no", "tz_n"))
    DB.commit('insert into payments (telegram_id, product, registered) values (?, ?, ?)', [msg.from_user.id, msg.text, datetime.now()])
