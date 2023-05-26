import asyncio

from aiogram.dispatcher import Dispatcher
from aiogram import types

from ..keyboards import set_location_kb, main_menu_kb
from ..database import location_is_set, extract_location
from ..log import logging

from sqlite3 import OperationalError, DatabaseError


async def set_location(message: types.Message):
    await message.answer(f'Доброго времени суток, {message.from_user.first_name or "пользователь"}! \U0001F601\n\n'
                         f'Кто я такой? \U0001F914 Я бот, который поможет вам с прогнозом погоды для вашего'
                         f'города/села. \U0001F31E\U0001F31D\n\n'
                         f'На данный момент у меня нет информации о вашем месте жительства, поэтому перед началом'
                         f'работы установите, пожалуйста, город/село, где вы проживаете\U0001F609\U0001F447',
                         reply_markup=set_location_kb)


async def weather_menu(message: types.Message):
    locality_info = extract_location(message.from_user.id)
    loc_name = locality_info.rus_locality

    await message.answer(f'\U0001F60E *Приветствую, {message.from_user.first_name or "пользователь"}!*\n\n'
                         f'\U0001F30D На данный момент вы следите за погодой в городе/селе *"{loc_name}"*\n\n'
                         f'Какую информацию хотите получить?\U0001F3AF',
                         reply_markup=main_menu_kb, parse_mode='Markdown')


async def default_handler(message: types.Message):
    try:
        if location_is_set(message.from_user.id):
            awaited_func = asyncio.create_task(weather_menu(message))
        else:
            awaited_func = asyncio.create_task(set_location(message))

        await awaited_func

    except OperationalError | DatabaseError as exc:
        logging.error('A definite problem with the database', exc_info=exc)
        await message.answer('Возникли технические неполадки... \U0001F61E\U0001F527\n'
                             'Попробуйте позже.')


def register_other_handlers(dp: Dispatcher):
    dp.register_message_handler(default_handler)
