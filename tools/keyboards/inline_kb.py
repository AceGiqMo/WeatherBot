from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

set_location_kb = InlineKeyboardMarkup(row_width=1)

set_location_button = InlineKeyboardButton(text='Установить город/село', callback_data='set_loc')
set_location_kb.add(set_location_button)

main_menu_kb = InlineKeyboardMarkup(row_width=1)

menu_button1 = InlineKeyboardButton(text='Изменить город/село', callback_data='set_loc')
menu_button2 = InlineKeyboardButton(text='Узнать погоду на данный момент', callback_data='weather_now')
menu_button3 = InlineKeyboardButton(text='Погода на сегодня', callback_data='weather_day0')
menu_button4 = InlineKeyboardButton(text='Погода на завтра', callback_data='weather_day1')
menu_button5 = InlineKeyboardButton(text='Погода на неделю', callback_data='weather_day7')

main_menu_kb.add(menu_button1, menu_button2).row(menu_button3, menu_button4).add(menu_button5)
