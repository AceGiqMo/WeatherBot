from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tools.create_bot import bot, bot_is_launched
from tools.handlers import admin, client, other

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

admin.register_admin_handlers(dp)
client.register_client_handlers(dp)
other.register_other_handlers(dp)

executor.start_polling(dp, skip_updates=True, on_startup=bot_is_launched)
