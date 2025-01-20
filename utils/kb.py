from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from support.messages import get_text
from datetime import datetime
from config import get_config, get_env
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Inline клавиатура с n количеством кнопок
# Вызывается, как buttons(Текст первой кнопки, Дата первой кнопки, Текст второй кнопки...)
def buttons(*args) -> InlineKeyboardMarkup:
    in_buttons = [[InlineKeyboardButton(text=get_text(args[i * 2]), callback_data=args[i * 2 + 1] if len(args) >= (i + 1) * 2 else args[i * 2])]
               for i in range((len(args) + 1) // 2)]
    return InlineKeyboardMarkup(inline_keyboard=in_buttons)


# Разбить текст на символы
def split_text(text, splitter=None) -> InlineKeyboardMarkup:
    phrase = get_text(text).split(splitter)

    in_buttons = [
               [InlineKeyboardButton(text=char, callback_data=text + "_" + char) for char in phrase]]
    return InlineKeyboardMarkup(inline_keyboard=in_buttons)


# Reply клавиатура
def reply(name) -> ReplyKeyboardMarkup:
    in_buttons = [[KeyboardButton(text=get_text(name))]]
    return ReplyKeyboardMarkup(keyboard=in_buttons, one_time_keyboard=True, resize_keyboard=True)


# Inline клавиатура с 2 кнопками в 1 ряд
def two_buttons(name1: str, data1: str, name2: str, data2: str):
    in_buttons = [[InlineKeyboardButton(text=get_text(name1), callback_data=data1),
               InlineKeyboardButton(text=get_text(name2), callback_data=data2)]]
    return InlineKeyboardMarkup(inline_keyboard=in_buttons)


# Телефон
def phone() -> ReplyKeyboardMarkup:
    in_buttons = [[KeyboardButton(text=get_text("give_phone"), request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=in_buttons, one_time_keyboard=True, resize_keyboard=True)


# Кнопки меню
def menu() -> InlineKeyboardMarkup:
    menu_buttons = get_config("menu")
    next_to_arr = False
    buttons = []

    for button_name in menu_buttons:
        button = menu_buttons[button_name]
        if button["size"] == 1:
            if not next_to_arr:
                next_to_arr = True
                buttons.append([])
            else:
                next_to_arr = False
        else:
            next_to_arr = False
            buttons.append([])

        buttons[-1].append(InlineKeyboardButton(text=button["name"],
                        callback_data=f"menu_{button_name}" if
                        "function" in button else None,
                        url=button["url"] if "url" in button else None))

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Клавиатура оплаты
def pay_kb() -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(text=get_text("predoplata"), callback_data="predoplata"),
        InlineKeyboardButton(text=get_text("write_me"), url="t.me/o_l_ebedev")],
        [InlineKeyboardButton(text=get_text("back"), callback_data="back")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def currency() -> InlineKeyboardMarkup:
    currencies = get_config("currency")
    keys = list(currencies.keys())
    values = list(currencies.values())

    buttons = [[InlineKeyboardButton(text=values[i], callback_data="currency_" + values[i] + "_" + keys[i]),
                InlineKeyboardButton(text=values[i + 1], callback_data="currency_" + values[i + 1] + "_" + keys[i + 1])]
               for i in range(0, len(currencies), 2)]
    buttons.append([InlineKeyboardButton(text=get_text("back"), callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def works() -> InlineKeyboardMarkup:
    works = get_text("example_works").split("_")

    buttons = [[InlineKeyboardButton(text=works[0], callback_data="work_0")], [InlineKeyboardButton(text=works[1], callback_data="work_1")], 
               [InlineKeyboardButton(text=works[2], callback_data="work_2")], [InlineKeyboardButton(text=works[3], callback_data="work_3")]]

    buttons.append([InlineKeyboardButton(text=get_text("back"), callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Ссылка на сайт
def site() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.button(
        text = get_text("link"), web_app=WebAppInfo(
            url = "https://telegram.org/blog"
        )
    )
    builder.button(
        text = get_text("back"), callback_data="back"
    )
    return builder.as_markup()

# Выбор пола
def sex() -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(text=get_text("sex_m"), callback_data="sex_m"),
        InlineKeyboardButton(text=get_text("sex_w"), callback_data="sex_m")],
        [InlineKeyboardButton(text=get_text("sex_h"), callback_data="sex_h")
        ]]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
