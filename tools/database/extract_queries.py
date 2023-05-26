import sqlite3 as sql
import os

from collections import namedtuple
from ..extra_functions import format_weather


def find_location(loc_name) -> list[namedtuple]:
    loc_name = '-'.join([obj.title() for obj in loc_name.split('-')])       # Йошкар-ола -> Йошкар-Ола

    conn = sql.connect(f'{os.getcwd()}\\tools\\database\\russian_localities.db')
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM localities "
                f"WHERE REPLACE(REPLACE(REPLACE(rus_locality, '-', ' '), 'й', 'и'), 'ё', 'е') = "
                f"REPLACE(REPLACE(REPLACE('{loc_name}', '-', ' '), 'й', 'и'), 'ё', 'е');")

    result = []

    for (rus_locality, formatted_eng_locality, region_id) in cur.fetchall():
        Row = namedtuple('Row', ['rus_locality', 'formatted_eng_locality', 'region_id'])
        result.append(Row(rus_locality, formatted_eng_locality, region_id))

    return result


def find_region(loc_name) -> list[namedtuple]:
    conn = sql.connect(f'{os.getcwd()}\\tools\\database\\russian_localities.db')
    cur = conn.cursor()

    cur.execute(f"SELECT region_name FROM regions "
                f"WHERE region_id IN (SELECT region_id FROM localities WHERE rus_locality = '{loc_name}');")

    result = []

    for region_name in cur.fetchall():
        Row = namedtuple('Row', ['region_name'])
        result.append(Row(region_name[0]))

    return result


def extract_location(user_id):
    conn = sql.connect(f'{os.getcwd()}\\tools\\database\\russian_localities.db')
    cur = conn.cursor()

    cur.execute(f"SELECT rus_locality, formatted_eng_locality, region_name FROM localities AS loc "
                f"JOIN regions AS reg ON (loc.region_id = reg.region_id) "
                f"WHERE formatted_eng_locality = (SELECT chosen_city FROM users_data "
                f"WHERE user_id = {user_id});")

    rus_locality, formatted_eng_locality, region_name = cur.fetchone()
    Row = namedtuple('Row', ['rus_locality', 'formatted_eng_locality', 'region_name'])
    result = Row(rus_locality, formatted_eng_locality, region_name)

    return result


def extract_weather_photo(weather):
    conn = sql.connect(f'{os.getcwd()}\\tools\\database\\russian_localities.db')
    cur = conn.cursor()

    weather = format_weather(weather)

    cur.execute(f"SELECT day_image_id, night_image_id, emj1.emoji_unicode AS day_emoji, "
                f"emj2.emoji_unicode AS night_emoji FROM weather_format wf "
                f"JOIN emojis emj1 ON (wf.day_emoji_id = emj1.emoji_id) "
                f"JOIN emojis emj2 ON (wf.night_emoji_id = emj2.emoji_id) "
                f"WHERE keywords = '{weather}';")

    result = []

    for day_image_id, night_image_id, day_emoji, night_emoji in cur.fetchall():
        Row = namedtuple('Row', ['day_image_id', 'night_image_id', 'day_emoji', 'night_emoji'])
        result.append(Row(day_image_id, night_image_id, day_emoji, night_emoji))

    return result


def extract_all_id():
    conn = sql.connect(f'{os.getcwd()}\\tools\\database\\russian_localities.db')
    cur = conn.cursor()

    cur.execute('SELECT user_id FROM users_data')

    result = [_id[0] for _id in cur.fetchall()]

    return result
