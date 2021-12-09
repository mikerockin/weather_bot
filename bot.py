import telebot
from pyowm.owm import OWM


bot = telebot.TeleBot('')

def weather(city):
    owm = OWM('324ec9d2d156f6e482a1fcf3e81d6588')
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(city)
    weather = observation.weather
    temperature = weather.temperature('celsius')
    pressure = weather.pressure
    pressure_norm = round(pressure['press'] * 0.75006375541921)
    wind = weather.wind()
    return temperature, wind['speed'], pressure_norm


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/weather':
        bot.send_message(message.from_user.id, 'Введите название города')
        bot.register_next_step_handler(message, get_weather)
    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'Список комманд для бота : ')
        bot.send_message(message.from_user.id, f'/weather - Узнать прогноз погоды по городу,\n'
                         f'/help - Просмотреть список комманд для бота\n')
    else:
        bot.send_message(message.from_user.id, 'Введите /help')


def get_weather(message):
    city = message.text
    try:
        w = weather(city)
        bot.send_message(message.from_user.id, f'В городе {city} сейчас {round(w[0]["temp"])} градусов, ощущается как {round(w[0]["feels_like"])}\n'
                                               f'Скорость ветра : {round(w[1])} м/с \n'
                                               f'Атмосферное давление : {w[2]} мм/рт.с\n')
        bot.send_message(message.from_user.id, "Введите название города")
        bot.register_next_step_handler(message, get_weather)
    except Exception:
        bot.send_message(message.from_user.id, 'Ooops... Город не найден в базе, попробуйте ещё раз')
        bot.send_message(message.from_user.id, "Введите название города")
        bot.register_next_step_handler(message, get_weather)

bot.polling()
