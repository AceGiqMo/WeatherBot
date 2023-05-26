import sqlite3 as sql
import os

from collections import namedtuple


def location_is_set(user_id: int):
    conn = sql.connect(f'{os.getcwd()}\\tools\\database\\russian_localities.db')
    cur = conn.cursor()

    cur.execute(f'SELECT * FROM users_data WHERE user_id = {user_id}')

    result = None

    if task := cur.fetchone():
        user_id, chosen_city = task
        Row = namedtuple('Row', ['user_id', 'chosen_city'])
        result = Row(user_id, chosen_city)

    return result if result else False
