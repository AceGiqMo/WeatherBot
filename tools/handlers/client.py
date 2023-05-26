from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from ..database import find_location, find_region, insert_user_data, extract_location, extract_weather_photo
from ..extra_functions import numbercase
from sqlite3 import OperationalError, DatabaseError

import requests, secrets
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from datetime import datetime, timedelta

directions = {'С-В': 'Северо-Восточный',
                          'Ю-В': 'Юго-Восточный', 'Ю-З': 'Юго-Западный', 'С-З': 'Северо-Западный',
                          'С': 'Северный', 'В': 'Восточный', 'Ю': 'Южный', 'З': 'Западный'}

months_translate = {'января': 'January', 'февраля': 'February', 'марта': 'March', 'апреля': 'April', 'мая': 'May',
                                'июня': 'June', 'июля': 'July', 'августа': 'August', 'сентября': 'September', 'октября': 'October',
                                'ноября': 'November', 'декабря': 'December'}

temperature_emoji = {range(-100, -9): '\U0001F976', range(-9, 6): '\U0001F62C',
                                 range(6, 16): '\U0001F60C', range(16, 26): '\U0001F929',
                                 range(26, 100): '\U0001F975'}


class FSMLocation(StatesGroup):
    location_input = State()


async def location_request(callback: types.CallbackQuery):
    await callback.message.answer('Введите название необходимого вам города/села\U0001F30D\U0001F4DD')
    await callback.answer()
    await FSMLocation.location_input.set()


async def chosen_location(message: types.Message, state: FSMContext):
    try:
        loc_query = find_location(message.text)

        if len(loc_query) > 1:
            region_query = find_region(loc_query[0].rus_locality)
            print(region_query)

            region_kb = InlineKeyboardMarkup(row_width=1)
            buttons = [InlineKeyboardButton(text=region.region_name,
                                            callback_data=f'reg_{region.region_name}_{loc_query[0].rus_locality}')
                       for region in region_query]
            region_kb.add(*buttons)

            await message.answer(f'\U00002728*Я нашёл {len(loc_query)} {numbercase(len(loc_query))} с названием '
                                 f'"{loc_query[0].rus_locality}"*.\n Выберите регион, в котором находится '
                                 f'необходимый вам город/село \U0001F30D\U0001F4CC',
                                 reply_markup=region_kb, parse_mode='Markdown')

        else:
            insert_user_data(message.from_user.id, loc_query[0].rus_locality)
            await message.answer(f'Город/село "{loc_query[0].rus_locality}" успешно установлен \U00002705')

        await state.finish()

    except IndexError:
        await message.answer('\U0001F30D\U0000274C Извините, я не нашёл город/село с таким названием\U0001F937\n'
                             'Проверьте, может вы допустили ошибку при написании. \U0001F914')
        await state.finish()

    except OperationalError | DatabaseError:
        await message.answer('Возникли технические неполадки... \U0001F61E\U0001F527\n'
                             'Попробуйте позже.')
        await state.finish()


async def chosen_region(callback: types.CallbackQuery):
    callback_split = callback.data.removeprefix('reg_').split('_')
    region_name, locality_name = callback_split

    try:
        insert_user_data(callback.from_user.id, locality_name, region=region_name)
        await callback.message.answer(f'Город/село "{locality_name} ({region_name})" успешно установлен \U00002705')
        await callback.answer()

    except OperationalError | DatabaseError:
        await callback.message.answer('Возникли технические неполадки... \U0001F61E\U0001F527\n'
                                      'Попробуйте позже.')
        await callback.answer()


async def weather_now(callback: types.CallbackQuery):
    try:
        loc_info = extract_location(callback.from_user.id)

        with requests.Session() as session:
            session.headers = {'User-Agent': UserAgent().chrome}
            response = session.get(f'https://world-weather.ru/pogoda/russia/{loc_info.formatted_eng_locality}/')

        if response.status_code == 200:
            bs = BeautifulSoup(response.text, 'html.parser')
            weather_info = bs.find('div', 'weather-now-info')
            weather_description = bs.find('div', id='weather-now-description')

            try:
                sunrise_sunset = bs.find('div', 'weather-now horizon').find('ul').find_all('li')[0]

                sunrise = sunrise_sunset.text[:sunrise_sunset.text.index('З') - 1]
                sunset = sunrise_sunset.text[sunrise_sunset.text.index('З'):]

                sunrise = datetime.strptime(sunrise, 'Восход: %H:%M')
                sunset = datetime.strptime(sunset, 'Заход: %H:%M')
            except AttributeError | IndexError:
                sunrise = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
                sunset = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)

            try:
                date_time = weather_info.find_all('b')[-1].text

                for (rus, eng) in months_translate.items():
                    date_time = date_time.replace(rus, eng)

                date_time = datetime.strptime(date_time, '%H:%M, %d %B')
            except IndexError:
                date_time = datetime.now()

            try:
                temp_emoji = ''
                temperature = weather_info.find('div', id='weather-now-number').text

                for (temp_range, emoji) in temperature_emoji.items():
                    if int(temperature[:-1]) in temp_range:
                        temp_emoji = emoji
                        break
            except AttributeError:
                temperature = 'нет информации о температуре'

            try:
                water_temperature = bs.find('div', 'weather-now-info').find('a').text
            except AttributeError:
                water_temperature = 'Нет информации о температуре воды'

            try:
                weather = weather_info.find('span', id='weather-now-icon')['title']
                weather_media = secrets.choice(extract_weather_photo(weather))

                if sunrise.hour <= date_time.hour <= sunset.hour:
                    weather_emoji = eval(f'u"{weather_media.day_emoji}"')
                    weather_image = weather_media.day_image_id
                else:
                    weather_emoji = eval(f'u"{weather_media.night_emoji}"')
                    weather_image = weather_media.night_image_id

            except TypeError:
                weather = 'нет информации о погоде'
                weather_media = secrets.choice(extract_weather_photo(weather))
                weather_emoji = eval(f'u"{weather_media.day_emoji}"')
                weather_image = weather_media.day_image_id


            info_keys = [obj.text for obj in weather_description.find_all('dt')]
            info_values = [obj.text for obj in weather_description.find_all('dd')]

            weather_desc_dict = {key: value for (key, value) in zip(info_keys, info_values)}

            try:
                for (key, value) in directions.items():
                    copied = weather_desc_dict['Ветер']
                    weather_desc_dict['Ветер'] = weather_desc_dict['Ветер'].replace(key, value)

                    if copied != weather_desc_dict['Ветер']:
                        break
            except KeyError:
                pass

            date_format = datetime.strftime(date_time, '%d %B, %H:%M')

            for (rus, eng) in months_translate.items():
                date_format = date_format.replace(eng, rus)

            await callback.message.answer_photo(
                    photo=weather_image,
                    caption=f"<b>{loc_info.rus_locality} ({loc_info.region_name})</b>\n"
                    f"<b>Погода на {date_format}</b>\n\n"
                    f"На данный момент {weather.lower()} {weather_emoji}\n\n"
                    f"Температура: <u>{temperature} {temp_emoji}</u>\n\n"
                    f"<i>Ощущается как:</i> <u>{weather_desc_dict.get('Ощущается', 'Нет информации')}</u>\n"
                    f"<i>Температура воды:</i> <u>{water_temperature}</u>\n"
                    f"<i>Атмосферное давление:</i> <u>{weather_desc_dict.get('Давление', 'Нет информации')}</u>\n"
                    f"<i>Влажность воздуха:</i> <u>{weather_desc_dict.get('Влажность', 'Нет информации')}</u>\n"
                    f"<i>Ветер (скорость, направление):</i> <u>{weather_desc_dict.get('Ветер', 'Нет информации')}</u>\n"
                    f"<i>Облачность:</i> <u>{weather_desc_dict.get('Облачность', 'Нет информации')}</u>\n"
                    f"<i>Видимость:</i> <u>{weather_desc_dict.get('Видимость', 'Нет информации')}</u>\n\n"
                    f"Удачного вам дня! Спасибо, что пользуетесь этим ботом \U0001F60A\U0000270C",
                    parse_mode='HTML')

            await callback.answer()

        else:
            await callback.message.answer('Не удалось получить информацию о погоде в данной местности...'
                                          '\U0001F30D\U0000274C\nПопробуйте позже.')
            await callback.answer()

    except OperationalError | DatabaseError:
        await callback.message.answer('Возникли технические неполадки... \U0001F61E\U0001F527\n'
                                      'Попробуйте позже.')
        await callback.answer()


async def weather_day(callback: types.CallbackQuery):
    try:
        days = []
        days_count = int(callback.data[-1])
        output = ''

        loc_info = extract_location(callback.from_user.id)
        output += f'<b>{loc_info.rus_locality} ({loc_info.region_name})</b>\n\n'

        with requests.Session() as session:
            session.headers = {'User-Agent': UserAgent().chrome}
            response = session.get(f'https://world-weather.ru/pogoda/russia/{loc_info.formatted_eng_locality}/')

        if response.status_code != 200:
            raise Exception('Unsuccessful parsing')

        bs = BeautifulSoup(response.text, 'html.parser')
        weather_info = bs.find('div', 'weather-now-info')

        try:
            date_time = weather_info.find_all('b')[-1].text

            for (rus, eng) in months_translate.items():
                date_time = date_time.replace(rus, eng)

            date_time = datetime.strptime(date_time, '%H:%M, %d %B')
            date_time = date_time.replace(year=datetime.now().year)
        except IndexError:
            date_time = datetime.now()

        if not days_count:
            days.append(date_time.strftime('%d-%B').lower())
        else:
            for _ in range(days_count):
                date_time += timedelta(days=1)
                days.append(date_time.strftime('%d-%B').lower())

        for day in days:
            with requests.Session() as session:
                session.headers = {'User-Agent': UserAgent().chrome}
                response = session.get(f'https://world-weather.ru/pogoda/'
                                       f'russia/{loc_info.formatted_eng_locality}/{day}/')

            if response.status_code != 200:
                raise Exception('Unsuccessful parsing')

            bs = BeautifulSoup(response.text, 'html.parser')

            weather_info = bs.find('div', id='content-left')

            date = weather_info.find('h2').text

            parse_results: list[dict] = []
            for daytime in ['night', 'morning', 'day', 'evening']:
                result_dict = dict(daytime='', temp='', feel_temp='', pressure='', wind_speed='', humidity='')
                weather_values_parse = weather_info.find('tr', daytime).find_all('td')
                result_dict = {key: value.text for (key, value) in zip(result_dict.keys(), weather_values_parse)}

                result_dict['wind_direction'] = weather_info.find('tr', daytime).find_all('span')[1]['title'].title()
                result_dict['weather'] = weather_info.find('tr', daytime).find('div')['title']

                weather_media = secrets.choice(extract_weather_photo(result_dict['weather']))

                if daytime in ['morning', 'day']:
                    result_dict['weather_emoji'] = eval(f'u"{weather_media.day_emoji}"')
                else:
                    result_dict['weather_emoji'] = eval(f'u"{weather_media.night_emoji}"')

                for (temp_range, emoji) in temperature_emoji.items():
                    if int(result_dict['temp'][:-1]) in temp_range:
                        result_dict['temp_emoji'] = emoji
                        break

                parse_results.append(result_dict)

            output += (f"<b>Погода на {date}</b>\n"
                       f"____________________________________")
            if days_count != 7:
                for res in parse_results:
                    output += (f"\n<u><b>{res['daytime']}:</b></u>\n\n"
                       f"{res['weather']} {res['weather_emoji']}\n\n"
                       f"Температура: <u>{res['temp']} {res['temp_emoji']}</u>\n\n"
                       f"<i>Ощущается как:</i> <u>{res['feel_temp']}</u>\n"
                       f"<i>Атмосферное давление:</i> <u>{res['pressure']} мм рт. ст.</u>\n"
                       f"<i>Влажность воздуха:</i> <u>{res['humidity']}</u>\n"
                       f"<i>Ветер (скорость, направление):</i> <u>{res['wind_speed']}, {res['wind_direction']}</u>\n")
                else:
                    output += f"____________________________________\n\n"
            else:
                for res in parse_results:
                    output += (f"\n<u><b>{res['daytime']}:</b></u>\n\n"
                       f"{res['weather']} {res['weather_emoji']}\n"
                       f"Температура: <u>{res['temp']} {res['temp_emoji']}</u>\n")
                else:
                    output += f"____________________________________\n\n\n"
        else:
            output += "Удачного вам дня! Спасибо, что пользуетесь этим ботом \U0001F60A\U0000270C"

            await callback.message.answer(output, parse_mode='HTML')
            await callback.answer()

    except OperationalError | DatabaseError:
        await callback.message.answer('Возникли технические неполадки... \U0001F61E\U0001F527\n'
                                      'Попробуйте позже.')
        await callback.answer()

    except Exception:
        await callback.message.answer('Не удалось получить информацию о погоде в данной местности...'
                                      '\U0001F30D\U0000274C\nПопробуйте позже.')
        await callback.answer()


def register_client_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(location_request, text='set_loc')
    dp.register_message_handler(chosen_location, state=FSMLocation.location_input)
    dp.register_callback_query_handler(chosen_region, Text(startswith='reg_'))
    dp.register_callback_query_handler(weather_now, text='weather_now')
    dp.register_callback_query_handler(weather_day, Text(startswith='weather_day'))
