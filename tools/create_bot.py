import os
from aiogram.bot import Bot

from .log import logging

bot = Bot(token=os.getenv('TOKEN'))


async def bot_is_launched(_):
    logging.info('Bot is online now...')
