from gtts import gTTS
import telebot
import requests
from datetime import datetime
import time



bot = telebot.TeleBot('50843к43к4306963:AAGcW4343е3ее3е34еR21Nassz1UbZz9ZfZEARAtknSHZcaQ')
current_url = 'http://api.openweathermap.org/data/2.5/weather'
forecast_url = 'http://api.openweathermap.org/data/2.5/forecast'
appid = '1d4e5494a8к34к43к67b82f2a974aecd743к34к34к34270ae3'

def current_weather(city):
    response = requests.get(url=current_url, params=dict(q=city, APPID=appid, lang='ru', units='metric'))
    data = response.json()
    temp = (data['main']['temp'])
    temp_feels_like = (data['main']['feels_like'])
    wind = (data['wind']['speed'])
    pressure = (data['main']['pressure'])
    pressure_norm = round(pressure* 0.75006375541921)
    humidity = (data['main']['humidity'])
    conditions = (data['weather'][0]['description'])
    sunrise_unix = int((data['sys']['sunrise']))
    sunrise = time.strftime("%H:%M", time.localtime(int(sunrise_unix)))
    sunset_unix = int((data['sys']['sunset']))
    sunset = time.strftime("%H:%M", time.localtime(int(sunset_unix)))
    timezone = (data['timezone'])/3600
    return temp, temp_feels_like, wind, pressure_norm, humidity, conditions, sunrise, sunset, timezone

def tomorrow_weather(city):
    response = requests.get(url=forecast_url, params=dict(q=city, APPID=appid, lang='ru', units='metric'))
    data = response.json()
    wind = round((data['list'][8]['wind']['speed']))
    conditions =(data['list'][8]['weather'][0]['description'])
    temp = round((data['list'][8]['main']['temp']))
    temp_feels_like =round((data['list'][8]['main']['feels_like']))
    pressure = (data['list'][8]['main']['pressure'])
    pressure_norm = round(pressure * 0.75006375541921)
    humidity = (data['list'][8]['main']['humidity'])
    return wind, conditions, temp, temp_feels_like, pressure_norm, humidity

def for_three_days_weather_1(city):
    response = requests.get(url=forecast_url, params=dict(q=city, APPID=appid, lang='ru', units='metric'))
    data = response.json()
    date_unix_1 = (data['list'][8]['dt'])
    date_1 = (datetime.fromtimestamp(date_unix_1).strftime('%d.%m.%Y'))
    wind_1 = round((data['list'][8]['wind']['speed']))
    conditions_1 =(data['list'][8]['weather'][0]['description'])
    temp_1 = round((data['list'][8]['main']['temp']))
    temp_feels_like_1 =round((data['list'][8]['main']['feels_like']))
    pressure_1 = (data['list'][8]['main']['pressure'])
    pressure_norm_1 = round(pressure_1 * 0.75006375541921)
    humidity_1 = (data['list'][8]['main']['humidity'])
    return date_1, conditions_1, temp_1, temp_feels_like_1, wind_1,  pressure_norm_1, humidity_1

def for_three_days_weather_2(city):
    response = requests.get(url=forecast_url, params=dict(q=city, APPID=appid, lang='ru', units='metric'))
    data = response.json()
    date_unix_2 = (data['list'][16]['dt'])
    date_2 = (datetime.fromtimestamp(date_unix_2).strftime('%d.%m.%Y'))
    wind_2 = round((data['list'][16]['wind']['speed']))
    conditions_2 =(data['list'][16]['weather'][0]['description'])
    temp_2 = round((data['list'][16]['main']['temp']))
    temp_feels_like_2 =round((data['list'][16]['main']['feels_like']))
    pressure_2 = (data['list'][16]['main']['pressure'])
    pressure_norm_2 = round(pressure_2 * 0.75006375541921)
    humidity_2 = (data['list'][16]['main']['humidity'])
    return date_2, conditions_2, temp_2, temp_feels_like_2, wind_2,  pressure_norm_2, humidity_2

def for_three_days_weather_3(city):
    response = requests.get(url=forecast_url, params=dict(q=city, APPID=appid, lang='ru', units='metric'))
    data = response.json()
    date_unix_3 = (data['list'][24]['dt'])
    date_3 = (datetime.fromtimestamp(date_unix_3).strftime('%d.%m.%Y'))
    wind_3 = round((data['list'][24]['wind']['speed']))
    conditions_3 =(data['list'][24]['weather'][0]['description'])
    temp_3 = round((data['list'][24]['main']['temp']))
    temp_feels_like_3 =round((data['list'][24]['main']['feels_like']))
    pressure_3 = (data['list'][24]['main']['pressure'])
    pressure_norm_3 = round(pressure_3 * 0.75006375541921)
    humidity_3 = (data['list'][24]['main']['humidity'])
    return date_3, conditions_3, temp_3, temp_feels_like_3, wind_3,  pressure_norm_3, humidity_3


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/weather_today':
        bot.send_message(message.from_user.id, 'Введите название города')
        bot.register_next_step_handler(message, get_weather_now)
    elif message.text == '/weather_tomorrow':
        bot.send_message(message.from_user.id, 'Введите название города')
        bot.register_next_step_handler(message, get_weather_tomorrow)
    elif message.text == '/weather_for_three_days':
        bot.send_message(message.from_user.id, 'Введите название города')
        bot.register_next_step_handler(message, get_weather_for_three_days)
    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'Список комманд для бота : ')
        bot.send_message(message.from_user.id, f'/weather_today - Узнать текущий прогноз погоды \n'
                                               f'/weather_tomorrow - Погода на завтра \n'
                                               f'/weather_for_three_days - Погода на 3 дня \n')
    else:
        bot.send_message(message.from_user.id, 'Введите /help, дабы узнать список команд для бота')

def get_voice(message):
    text = message
    language = 'ru'
    speech = gTTS(text=text, lang=language, slow=False)
    speech.save('playme.mp3')


def get_weather_now(message):
    city = message.text
    try:
        w = current_weather(city)
        wn = (f' Сейчас в городе {city} :  {w[5]}\nТемпература воздуха: {round(w[0])} градусов, ощущается как: {round(w[1])}\nСкорость ветра: {round(w[2])} м/с \nАтмосферное давление: {w[3]}  мм ртутного столба.\n'
                                               f'Влажность : {w[4]} %\n'
                                               f'Рассвет : {w[6]} \n'
                                               f'Закат : {w[7]} \n'
                                               f'Часовой пояс: + {round(w[8])}')
        bot.send_message(message.from_user.id, wn)
        voice_weather_now = get_voice(wn)
        audio = open('playme.mp3', 'rb')
        bot.send_audio(message.from_user.id, audio)
        bot.send_message(message.from_user.id, f'/weather_today - Узнать текущий прогноз погоды \n'
                                               f'/weather_tomorrow - Погода на завтра \n'
                                               f'/weather_for_three_days - Погода на 3 дня \n')
    except Exception:
        bot.send_message(message.from_user.id, 'Ooops... Город не найден в базе, попробуйте ещё раз')
        bot.send_message(message.from_user.id, "Введите название города")
        bot.register_next_step_handler(message, get_weather_now)
    return wn


def get_weather_tomorrow(message):
    city = message.text
    try:
        t = tomorrow_weather(city)
        wt = (f' Завтра в городе {city} : {t[1]}\nТемпература воздуха: {round(t[2])} градусов, ощущается как: {round(t[3])}\nСкорость ветра: {round(t[0])} м/с\nАтмосферное давление: {t[4]}  мм ртутного столба\n'
                         f'Влажность: {t[5]} %')
        bot.send_message(message.from_user.id, wt)
        voice_weather_tomorrow = get_voice(wt)
        audio = open('playme.mp3', 'rb')
        bot.send_audio(message.from_user.id, audio)
        bot.send_message(message.from_user.id, f'/weather_today - Узнать текущий прогноз погоды \n'
                                               f'/weather_tomorrow - Погода на завтра \n'
                                               f'/weather_for_three_days - Погода на 3 дня \n')
    except Exception:
        bot.send_message(message.from_user.id, 'Ooops... Город не найден в базе, попробуйте ещё раз')
        bot.send_message(message.from_user.id, "Введите название города")
        bot.register_next_step_handler(message, get_weather_tomorrow)
    return wt


def get_weather_for_three_days(message):
    city = message.text
    try:
        ft = for_three_days_weather_1(city)
        ff = for_three_days_weather_2(city)
        td = for_three_days_weather_3(city)
        wftd_1 = (f' {ft[0]} в городе {city} : {ft[1]}\nТемпература воздуха: {round(ft[2])} градусов, ощущается как: {round(ft[3])}\nСкорость ветра: {round(ft[4])} м/с\nАтмосферное давление: {ft[5]}  мм ртутного столба\n'
            f'Влажность: {ft[6]} %')
        wftd_2 = (f' {ff[0]} в городе {city} : {ff[1]}\nТемпература воздуха: {round(ff[2])} градусов, ощущается как: {round(ff[3])}\nСкорость ветра: {round(ff[4])} м/с\nАтмосферное давление: {ff[5]}  мм ртутного столба\n'
            f'Влажность: {ff[6]} %')
        wftd_3 = (f' {td[0]} в городе {city} : {td[1]}\nТемпература воздуха: {round(td[2])} градусов, ощущается как: {round(td[3])}\nСкорость ветра: {round(td[4])} м/с\nАтмосферное давление: {td[5]}  мм ртутного столба\n'
            f'Влажность: {ft[6]} %')
        bot.send_message(message.from_user.id, wftd_1)
        bot.send_message(message.from_user.id, wftd_2)
        bot.send_message(message.from_user.id, wftd_3)
        voice_weather_first_day = get_voice(wftd_1 + wftd_2 + wftd_3)
        audio = open('playme.mp3', 'rb')
        bot.send_audio(message.from_user.id, audio)
        bot.send_message(message.from_user.id, f'/weather_today - Узнать текущий прогноз погоды \n'
                                               f'/weather_tomorrow - Погода на завтра \n'
                                               f'/weather_for_three_days - Погода на 3 дня \n')
    except Exception:
        bot.send_message(message.from_user.id, 'Ooops... Город не найден в базе, попробуйте ещё раз')
        bot.send_message(message.from_user.id, "Введите название города")
        bot.register_next_step_handler(message, get_weather_for_three_days)
    return wftd_1, wftd_2, wftd_3

bot.infinity_polling()
