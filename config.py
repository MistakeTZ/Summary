import os
import json
from dotenv import load_dotenv


config_file = {}
messages = {}
menus = {}

# Загрузка файла окружения
def load_env():
    load_dotenv()


# Получение текста из файла окружения по ключу
def get_env(key):
    return os.getenv(key)


# Чтение из файла конфигурации
def get_config(*args, config=None):
    """
    Gets a value from the config based on a path of keys.

    Args:
        *args: The keys to access in the config.
        config: The config to access. If not provided, the global config is used.

    Returns:
        The value at the provided path, or False if the path does not exist.
    """
    if config is None:
        config = config_file

    if args[0] in config:
        if len(args) == 1:
            return config[args[0]]
        return get_config(*args[1:], config=config[args[0]])

    return False
        

# Загрузка файла конфигурации
def load_config():
    global config_file
    with open(os.path.join("support", "config.json"), encoding='utf-8') as file:
        config_file = json.load(file)


# Добавление сообщения
def add_mes(id, message_id):
    if str(id) in messages:
        messages[str(id)].append(message_id)
    else:
        messages[str(id)] = [message_id]


# Установка меню
def set_menu(id, message_id):
    menus[str(id)] = message_id


# Получение меню
def get_menu(id):
    if str(id) in menus:
        return menus[str(id)]
    else:
        return 0


# Очистка сообщений
def clear_mes(id):
    if str(id) in messages:
        tmp_arr = messages[str(id)]
        messages[str(id)] = []
        return tmp_arr
    else:
        return []
