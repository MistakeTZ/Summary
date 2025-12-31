from aiogram.fsm.state import State, StatesGroup


# Файл состояний FSM
class UserState(StatesGroup):
    default = State()
    admin = State()
    license = State()
    email = State()
    name = State()
    phone = State()
    photo = State()
    product = State()
