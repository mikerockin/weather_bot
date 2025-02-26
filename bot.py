import os
import uuid
from datetime import datetime
import time
import requests
import telebot
from gtts import gTTS
import sqlite3
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Подключение к SQLite
def get_db_connection():
    return sqlite3.connect('weather.db')

# Создание таблицы (если её нет)
def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            city TEXT NOT NULL,
            request_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    connection.close()

# Сохранение запроса в базу данных
def save_request(user_id, city, request_type):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "INSERT INTO weather_requests (user_id, city, request_type) VALUES (?, ?, ?)"
    values = (user_id, city, request_type)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

# Инициализация базы данных
init_db()

# Инициализация бота
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
current_url = 'http://api.openweathermap.org/data/2.5/weather'
forecast_url = 'http://api.openweathermap.org/data/2.5/forecast'
appid = os.getenv('OPENWEATHERMAP_API_KEY')

# Остальной код (функции get_weather_data, get_voice и т.д.)

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
        bot.send_message(message.from_user.id, 'Список команд для бота:\n'
                                              '/weather_today - Узнать текущий прогноз погоды\n'
                                              '/weather_tomorrow - Погода на завтра\n'
                                              '/weather_for_three_days - Погода на 3 дня')
    else:
        bot.send_message(message.from_user.id, 'Введите /help, чтобы узнать список команд для бота')

def get_weather_data(city, index=0):
    response = requests.get(url=forecast_url, params=dict(q=city, APPID=appid, lang='ru', units='metric'))
    data = response.json()
    item = data['list'][index]
    date_unix = item['dt']
    date = datetime.fromtimestamp(date_unix).strftime('%d.%m.%Y')
    wind = round(item['wind']['speed'])
    conditions = item['weather'][0]['description']
    temp = round(item['main']['temp'])
    temp_feels_like = round(item['main']['feels_like'])
    pressure = round(item['main']['pressure'] * 0.75006375541921)
    humidity = item['main']['humidity']
    return date, conditions, temp, temp_feels_like, wind, pressure, humidity

def get_voice(text):
    filename = 'playme.mp3'
    speech = gTTS(text=text, lang='ru', slow=False)
    speech.save(filename)
    return filename

def get_weather_now(message):
    city = message.text
    try:
        w = get_weather_data(city, index=0)
        wn = (
            f'Сейчас в городе {city}: {w[1]}\n'
            f'Температура воздуха: {w[2]} градусов, ощущается как: {w[3]}\n'
            f'Скорость ветра: {w[4]} м/с\n'
            f'Атмосферное давление: {w[5]} мм ртутного столба\n'
            f'Влажность: {w[6]} %'
        )
        bot.send_message(message.from_user.id, wn)
        audio_filename = get_voice(wn)
        with open(audio_filename, 'rb') as audio:
            bot.send_audio(message.from_user.id, audio)
        os.remove(audio_filename)

        # Сохраняем запрос в базу данных
        save_request(message.from_user.id, city, 'weather_today')
    except Exception as e:
        bot.send_message(message.from_user.id, f'Ooops... Произошла ошибка: {e}')
        bot.send_message(message.from_user.id, "Введите название города")
        bot.register_next_step_handler(message, get_weather_now)

def get_weather_tomorrow(message):
    city = message.text
    try:
        t = get_weather_data(city, index=8)
        wt = (
            f'Завтра в городе {city}: {t[1]}\n'
            f'Температура воздуха: {t[2]} градусов, ощущается как: {t[3]}\n'
            f'Скорость ветра: {t[4]} м/с\n'
            f'Атмосферное давление: {t[5]} мм ртутного столба\n'
            f'Влажность: {t[6]} %'
        )
        bot.send_message(message.from_user.id, wt)
        audio_filename = get_voice(wt)
        with open(audio_filename, 'rb') as audio:
            bot.send_audio(message.from_user.id, audio)
        os.remove(audio_filename)

        # Сохраняем запрос в базу данных
        save_request(message.from_user.id, city, 'weather_tomorrow')
    except Exception as e:
        bot.send_message(message.from_user.id, f'Ooops... Произошла ошибка: {e}')
        bot.send_message(message.from_user.id, "Введите название города")
        bot.register_next_step_handler(message, get_weather_tomorrow)

def get_weather_for_three_days(message):
    city = message.text
    try:
        t = get_weather_data(city, index=8)
        wt = (
            f'Завтра в городе {city}: {t[1]}\n'
            f'Температура воздуха: {t[2]} градусов, ощущается как: {t[3]}\n'
            f'Скорость ветра: {t[4]} м/с\n'
            f'Атмосферное давление: {t[5]} мм ртутного столба\n'
            f'Влажность: {t[6]} %'
        )
        bot.send_message(message.from_user.id, wt)
        audio_filename = get_voice(wt)
        with open(audio_filename, 'rb') as audio:
            bot.send_audio(message.from_user.id, audio)
        os.remove(audio_filename)

        # Сохраняем запрос в базу данных
        save_request(message.from_user.id, city, 'weather_tomorrow')
    except Exception as e:
        bot.send_message(message.from_user.id, f'Ooops... Произошла ошибка: {e}')
        bot.send_message(message.from_user.id, "Введите название города")
        bot.register_next_step_handler(message, get_weather_tomorrow)

bot.infinity_polling()