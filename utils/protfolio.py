from aiogram import F
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types.input_media_photo import InputMediaPhoto

from os import path, listdir
from support.messages import get_text, add_mes, send_message
from loader import bot, dp
from . import kb


async def send_portfolio(user_id):
    mes = await bot.send_message(user_id, get_text("examples"), kb.works())
    add_mes(user_id, mes.message_id)


# Выбор примера работы
@dp.callback_query(F.data.startswith("work_"))
async def work_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    await send_message(clbck, clbck.data, kb.two_buttons("screens", "screens_" + clbck.data[-1], "back", "back"), None, None, get_text("work_add"))


# Вывод скриншотов
@dp.callback_query(F.data.startswith("screens_"))
async def screen_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    num = clbck.data[-1]
    path_folder = path.join("support", "assets", "photos_" + num)
    files = listdir(path_folder)

    photos = [InputMediaPhoto(media=FSInputFile(path=path.join(path_folder, files[file])), caption="photo_" + str(file)) for file in range(len(files))]
    mes_id = await clbck.message.answer_media_group(media=photos)
    [add_mes(clbck.from_user.id, mes.message_id) for mes in mes_id]

    await send_message(clbck, "screens_label", kb.buttons("back"), None, None, get_text("example_works").split("_")[int(num)][4:])
