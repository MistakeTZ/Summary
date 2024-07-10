import csv
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink
from states import UserState
from os import path
from config import add_mes, set_menu

messages = {}

# Загрузка всех сообщений
def load_messages():
    global messages
    with open(path.join("support", "messages.csv"), encoding='utf8') as f:
        reader = csv.reader(f)
        for line in reader:
            messages[line[0]] = line[1]

    if "succeful_load" in messages.keys():
        print(messages["succeful_load"])


# Получение текста сообщения по ключу
def get_text(key: str, *args) -> str:
    if key in messages.keys():
        return messages[key].replace("\\n", "\n").replace("\"\"", "\"").format(*args)
    return messages["default"]


# Отправка сообщения пользователю
async def message(id: int, msg: Message, key: str, reply_markup=None, *args, **kwargs):
    text = get_text(key, *args)
    mes_id = await msg.answer(text, reply_markup=reply_markup)

    if not "nodelete" in kwargs.keys():
        add_mes(id, mes_id.message_id)
    if "set_menu" in kwargs.keys():
        set_menu(id, mes_id.message_id)
    

# Отправка сообщения, клавиатуры и изменение состояния
async def send_message(msg: Message | CallbackQuery, text: str, reply_markup = None, state: FSMContext = None, new_state: UserState = None, *args, **kwargs):
    id = msg.from_user.id
    if type(msg) == CallbackQuery:
        msg = msg.message
        try:
            await msg.edit_reply_markup()
        except:
            pass
    if state != None:
        await state.set_state(new_state)
    if "photo" in kwargs.keys():
        photo = FSInputFile(path=kwargs["photo"])
        mes_id = await msg.answer_photo(photo)
        if not "set_menu" in kwargs.keys():
            add_mes(id, mes_id.message_id)

    await message(id, msg, text, reply_markup, *args, **kwargs)
