from aiogram.filters import Command, CommandStart, Filter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from loader import dp, bot
from os import path
import asyncio

from config import add_user, add_mes
import utils.kb as kb
from support.messages import message, send_message, get_text
from states import UserState


# Добавление в отправленные
class AddToSended(Filter):
    async def __call__(self, message: Message, state: FSMContext):
        print(message.from_user.id)
        add_mes(message.from_user.id, message.message_id)
        return True


# Команда старта бота
@dp.message(AddToSended(), CommandStart())
async def command_start_handler(msg: Message, state: FSMContext) -> None:
    id = msg.from_user.id
    print(id)
    if add_user(id):
        await send_message_with_times("hi_again", msg.from_user.first_name, 0.06, msg)
    else:
        await send_message_with_times("hi", msg.from_user.first_name, 0.06, msg)

    await message(msg, "how_feels", kb.split_text("emotions"), nodelete=True)


# Команда меню
@dp.message(Command("menu"))
async def command_settings(msg: Message, state: FSMContext) -> None:
    await send_message(msg, "menu", kb.menu(), state=state, new_state=UserState.default, photo=path.join("support", "assets", "oleg.jpg"))


# Отправить сообщение с задержками между символами
async def send_message_with_times(message, name, delay, msg: Message):
    string = get_text(message, name)
    new_mes = await msg.answer(string[0])
    await msg.delete()
    await asyncio.sleep(delay)

    for i in range(1, len(string) - 1):
        if string[i + 1] != ' ':
            await new_mes.edit_text(string[:i + 1])
        await asyncio.sleep(delay)

    await new_mes.edit_text(string)
    