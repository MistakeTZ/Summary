import abc
import asyncio
from os.path import exists, join

from aiogram import Bot
from aiogram.types import FSInputFile, Message


# Загрузчик сообщений
class MessageSender:

    # Все доступные сообщения
    messages = {}
    bot: Bot

    def __init__(self, bot, manager) -> None:
        """Определение бота."""
        self.bot = bot
        self.manager = manager

    @abc.abstractmethod
    def load_messages(self, path_to_file: str = None):
        """Метод загружает все сообщения из файла."""
        return

    # Получение текста сообщения по ключу с указанием аргументов
    def text(self, key: str, *args) -> str:
        if key in self.messages:
            return self.messages[key].format(*args)

        print(f"Key {key} not found")
        return self.messages["default"]

    # Отправка сообщения пользователю
    async def message(self, chat_id: int, key: str, reply_markup=None, *args):
        text = self.text(key, *args)
        await self.bot.send_message(
            chat_id,
            text,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )

    # Отправить сообщение с задержками между символами
    async def broadcasting_message(
        self,
        chat_id: int,
        delay: float,
        key: str,
        reply_markup=None,
        *args,
    ):
        text = self.text(key, *args)
        mes = await self.bot.send_message(
            chat_id,
            text[:2],
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )

        for i in range(4, len(text), 2):
            await asyncio.sleep(delay)
            try:
                await mes.edit_text(
                    text[:i],
                    reply_markup=reply_markup,
                )
            except:
                pass

    # Изменение сообщения
    async def edit_message(
        self,
        msg: Message,
        key: str,
        reply_markup=None,
        *args,
    ):
        text = self.text(key, *args)
        await msg.edit_text(text, reply_markup=reply_markup)

    # Отправление кешированного медиа
    async def send_cached_media(
        self,
        chat_id: int,
        media_type: str,
        media: str,
        key: str = None,
        reply_markup=None,
        *args,
    ):
        if key:
            text = self.text(key, *args)
        else:
            text = None

        kwargs = {
            "chat_id": chat_id,
            media_type: media,
            "caption": text,
            "reply_markup": reply_markup,
        }

        await getattr(self.bot, f"send_{media_type}")(**kwargs)

    # Открытие медиа
    async def send_media(
        self,
        chat_id: int,
        media_type: str,
        media: str,
        key: str = None,
        reply_markup=None,
        path: str = None,
        name: str = None,
        *args,
    ):
        if key:
            text = self.text(key, *args)
        else:
            text = None

        if name:
            name = name + "." + media.split(".")[1]
        else:
            name = media

        if path:
            path = join(path, media)
        else:
            path = join("support", "assets", media)

        media_file = FSInputFile(path=path, filename=name)
        kwargs = {
            "chat_id": chat_id,
            media_type: media_file,
            "caption": text,
            "reply_markup": reply_markup,
        }

        try:
            await getattr(self.bot, f"send_{media_type}")(**kwargs)
        except Exception as e:
            await self.bot.send_message(self.manager, str(e))
            raise e


# Загрузчик сообщений из JSON файла
class JSONMessageSender(MessageSender):

    # Загрузка всех сообщений
    def load_messages(self, path_to_file: str = None):
        import json

        # Файл не предопределен
        if not path_to_file:
            path_to_file = join("support", "messages.json")

        # Файл не найден
        if not exists(path_to_file):
            raise ValueError("Message file not found")

        # Загрузка сообщений
        with open(path_to_file, encoding="utf8") as file:
            self.messages = json.load(file)

        # Сообщение об успешной загрузке
        if "succeful_load" in self.messages:
            print(self.messages["succeful_load"])

        return True
