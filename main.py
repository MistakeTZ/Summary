import asyncio, logging
import sys
from database.model import DB

from loader import dp, bot


# Запуск бота
async def main() -> None:

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    raise KeyboardInterrupt


# Одновременное выполнение нескольких асинхронных функций
async def multiple_tasks():
    from webhook import run_api
    from utils.protfolio import send_form
    
    input_coroutines = [main(), run_api(send_form)]
    res = await asyncio.gather(*input_coroutines)
    return res


# Запуск и остановка бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(multiple_tasks())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    print("Exiting")

    try:
        DB.unload_database()
    except:
        print("Database closing failed")
