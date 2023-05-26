from aiogram import types, Dispatcher
from aiogram.types import ContentType
from aiogram.dispatcher.filters import Text

from ..database import extract_all_id
from ..create_bot import bot


async def admin_message(message: types.Message):
    users_id = extract_all_id()

    try:
        users_id.remove(1080255064)
    except ValueError:
        pass

    for user_id in users_id:
        await bot.send_message(chat_id=user_id, text=message.text)


async def admin_send_photo(message: types.Message):
    users_id = extract_all_id()

    try:
        users_id.remove(1080255064)
    except ValueError:
        pass

    for user_id in users_id:
        await bot.send_photo(chat_id=user_id, photo=message.photo[0].file_id, caption='')


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_message, (lambda msg: msg.from_user.id == 1080255064),
                                commands=['all'], content_types=ContentType.TEXT)
    dp.register_message_handler(admin_send_photo, (lambda msg: msg.from_user.id == 1080255064),
                                commands=['all'], content_types=ContentType.PHOTO)
