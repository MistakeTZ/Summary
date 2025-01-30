from aiogram import F
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types.input_media_photo import InputMediaPhoto

from config import get_config
from os import path, listdir
from support.messages import get_text, add_mes, send_message
from loader import bot, dp
from . import kb


async def send_portfolio(user_id, page=0, previous=None):
    cases = get_config("cases")
    page = 0 if page >= len(cases) else page
    page = len(cases) - 1 if page < 0 else page
    now_case = cases[page]
    link = "" if "link" not in now_case else get_text("case_link", now_case["link"])
    
    image = path.join("support", "assets", now_case["image"])

    if previous:
        media = InputMediaPhoto(media=FSInputFile(image), caption=get_text("case",
                            now_case["name"], now_case["description"], link))
        await bot.edit_message_media(chat_id=user_id, message_id=previous, media=media, reply_markup=kb.works(page, len(cases)))
    else:
        mes = await bot.send_photo(user_id, photo=FSInputFile(image),
                caption=get_text("case", now_case["name"], now_case["description"],
                                link), reply_markup=kb.works(page, len(cases)))
        add_mes(user_id, mes.message_id)
