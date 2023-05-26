def numbercase(number):
    if number in range(2, 5):
        return 'города/села'
    return 'городов/сёл'


def format_weather(weather):
    weather_dic = {'Ясно': 'Ясно', 'Облачно': 'Облачность', 'Пасмурно': 'Пасмурно', 'Дождь': 'Дождь',
                   'Снег': 'Снег', 'Гроза': 'Гроза', 'Туман': 'Туман'}

    for (key, value) in weather_dic.items():
        if key.lower() in weather.lower():
            weather = value
            break
    else:
        weather = 'Default'

    return weather
