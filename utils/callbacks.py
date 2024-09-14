from aiogram import F
from aiogram.types import FSInputFile
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink
from loader import dp, bot
import asyncio
from os import path, listdir

from config import add_mes, clear_mes, get_menu, get_env

from utils import currency
from utils import payment
import utils.kb as kb
import utils.user as user
from support.messages import get_text, send_message
from states import UserState
from database.model import DB


# Возвращение в меню
@dp.callback_query(F.data == "back")
async def menu_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UserState.default)
    id = clbck.from_user.id
    try:
        await bot.edit_message_reply_markup(chat_id=id, message_id=get_menu(id), reply_markup=kb.menu())
    except:
        await send_message(clbck, "menu", kb.menu(), photo=path.join("support", "assets", "oleg.jpg"), nodelete=True, set_menu=True)
    
    try:
        await bot.delete_messages(id, clear_mes(clbck.from_user.id))
    except:
        pass


# Возвращение в меню без очистки истории
@dp.callback_query(F.data == "back_no_history")
async def menu_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UserState.default)
    id = clbck.from_user.id
    try:
        clear_mes(id)
    except:
        pass

    await send_message(clbck, "menu", kb.menu(), photo=path.join("support", "assets", "oleg.jpg"), nodelete=True, set_menu=True)
    


# Выбран эмодзи
@dp.callback_query(F.data.startswith("emotions_"))
async def emotion_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    emote = get_text("emotions").split().index(clbck.data[-1])
    await clbck.message.answer(clbck.data[-1])
    await send_message(clbck, "emotions_" + str(emote), nodelete=True)

    await asyncio.sleep(2)
    license_ = get_text("license").split("лицензионное соглашение")
    await clbck.message.answer(text=license_[0] + hlink("лицензионное соглашение", "https://youtu.be/dQw4w9WgXcQ") + license_[1],
                               reply_markup=kb.reply("accept"), disable_web_page_preview=True)
    await state.set_state(UserState.license)


# Выбор в меню
@dp.callback_query(F.data.startswith("menu_"))
async def menu_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    choice = clbck.data.split("_")[-1]

    match choice:
        case "zakaz":
            await zakaz(clbck)

        case "pay":
            await pay(clbck)

        case "format":
            await formatting(clbck)

        case "cur":
            await currence(clbck)

        case "browser":
            await browser(clbck)

        case "info":
            await info(clbck, state)

        case "db":
            await database(clbck)

        case "graph":
            await graph(clbck)
            
        case "help":
            await help(clbck)

        case "examples":
            await send_message(clbck, "examples", kb.works())

        case _:
            await clbck.answer(get_text("not_realize"))


# Заказ бота
async def zakaz(clbk: CallbackQuery):
    await send_message(clbk, "about_zakaz", kb.two_buttons("make_zakaz", "make_zakaz", "back", "back"))


# Оплата
async def pay(clbk: CallbackQuery):
    await send_message(clbk, "text_payment")
    await asyncio.sleep(5)
    await send_message(clbk, "test_payment")
    await payment.pay(clbk.from_user.id)


# Базы данных
async def database(clbck: CallbackQuery):
    await clbck.message.edit_reply_markup()
    mes_id = await clbck.message.answer(get_text("databases", hlink("библиотеки Python", "https://github.com/aiogram/aiogram")), 
                                reply_markup=kb.buttons("back"), disable_web_page_preview=True)
    add_mes(clbck.from_user.id, mes_id.message_id)


# Составление графа
async def graph(clbck: CallbackQuery):
    await send_message(clbck, "graphs")
    photos = [InputMediaPhoto(media=FSInputFile(path=path.join("support", "assets", "matplot_{}.png".format(num))), 
                                caption="matplot_" + str(num)) for num in range(1, 4)]
    mes_id = await clbck.message.answer_media_group(media=photos)
    [add_mes(clbck.from_user.id, mes.message_id) for mes in mes_id]

    await asyncio.sleep(4)
    await send_message(clbck, "also", kb.buttons("back")) 



# Форматирование текста
async def formatting(clbk: CallbackQuery):
    await clbk.message.edit_reply_markup()
    mes_id = await clbk.message.answer(text=get_text("formatting", hlink("ссылка", "t.me/o_l_ebedev")), reply_markup=kb.buttons("back"), disable_web_page_preview=True)
    add_mes(clbk.from_user.id, mes_id.message_id)


# Курс
async def currence(clbk: CallbackQuery):
    await send_message(clbk, "choose_currency", kb.currency())


# Оплата и поддержка
async def help(clbk: CallbackQuery):
    await send_message(clbk, "to_pay", kb.buttons("back"))


# Оформления заказа
@dp.callback_query(F.data == "make_zakaz")
async def zakaz_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    await send_message(clbck, "write_product", kb.buttons("back"), state, UserState.product)


# Есть ли ТЗ
@dp.callback_query(F.data.startswith("tz_"))
async def zakaz_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    tz = clbck.data.split("_")[-1] == "y"
    user_id = DB.get('select id from payments where telegram_id = ? order by registered desc', [clbck.from_user.id], True)
    DB.commit('update payments set have_tz = ? where id = ?', [tz, user_id[0]])
    await send_message(clbck, "need_to_pay", kb.pay_kb(), state, UserState.default, get_env("cost"))


# Согласие на оплату
@dp.callback_query(F.data == "predoplata")
async def zakaz_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    user_id = DB.get('select id from payments where telegram_id = ? order by registered desc', [clbck.from_user.id], True)
    await payment.real_pay(clbck.from_user.id, user_id[0])


# Выбор актива
@dp.callback_query(F.data.startswith("currency_"))
async def currency_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    data = clbck.data.split("_")
    try:
        price = currency.make_graph(data[2], data[1])

        mes_id = await clbck.message.answer("<b><code>" + data[1] + "</code></b>")
        add_mes(clbck.from_user.id, mes_id.message_id)
        await send_message(clbck, "price", kb.buttons("back"), None, None, price, photo=path.join("temp", "shares.png"))
    except:
        await send_message(clbck, "price_error", kb.buttons("back"))


# Встроенный браузер
async def browser(clbk: CallbackQuery):
    await send_message(clbk, "site", kb.site())

# Сбор информации
async def info(clbk: CallbackQuery, state):
    await send_message(clbk, "how_your_name", None, state, UserState.name)

# Выбор пола
@dp.callback_query(F.data.startswith("sex_"))
async def currency_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    user.users[str(clbck.from_user.id)].sex = clbck.data 
    await send_message(clbck, "write_phone", kb.phone(), state, UserState.phone)

# Нет питомца
@dp.callback_query(F.data == "skip_photo", UserState.photo)
async def photo_handler(clbck: CallbackQuery, state: FSMContext) -> None:
    user.users[str(clbck.from_user.id)].photo = -1 
    await send_message(clbck, "no_photo", None, state, UserState.email)

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
