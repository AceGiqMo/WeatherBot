import sqlite3 as sql
import os

from typing import NoReturn


def insert_user_data(user_id: int, location, region='') -> NoReturn:
    conn = sql.connect(f'{os.getcwd()}\\tools\\database\\russian_localities.db')
    cur = conn.cursor()

    query_fragment = ''

    if region:
        query_fragment = f" AND region_id = (SELECT region_id FROM regions WHERE region_name = '{region}')"

    cur.execute(f"SELECT formatted_eng_locality FROM localities "
                f"WHERE rus_locality = '{location}'{query_fragment};")

    urn = cur.fetchone()[0]

    cur.execute(f"SELECT user_id FROM users_data WHERE user_id = {user_id};")

    if cur.fetchone():
        cur.execute(f"UPDATE users_data SET chosen_city = '{urn}' "
                    f"WHERE user_id = {user_id};")
    else:
        cur.execute(f"INSERT INTO users_data (user_id, chosen_city) "
                    f"VALUES ({user_id}, '{urn}');")

    conn.commit()
    conn.close()
