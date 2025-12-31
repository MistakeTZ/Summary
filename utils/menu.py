from tasks import kb
from tasks.loader import sender


async def send_menu(user_id):
    await sender.message(user_id, "menu", kb.menu())
