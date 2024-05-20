import os
import telebot
from aiogram import types
import requests
from telebot import types
import uuid
from yookassa import Payment
from validate_email import validate_email
import random
import string
import config
from loguru import logger
import time
class Customer:
    def __init__(self, payment_id, refToChannel, email, flag, isTriedPromo, isPutPhoto):
        self.payment_id = payment_id
        self.refToChannel = refToChannel
        self.email = email
        self.flag = flag
        self.isTriedPromo = isTriedPromo
        self.isPutPhoto = isPutPhoto
class Beat:
    def __init__(self, genre, bpm, key, tags, audio_file, audio_name, file_name, photo, photo_file_name):
        self.genre = genre
        self.bpm = bpm
        self.key = key
        self.tags = tags
        self.audio_file = audio_file
        self.audio_name = audio_name
        self.file_name = file_name
        self.photo = photo
        self.photo_file_name = photo_file_name

bot = telebot.TeleBot(config.TOKEN, parse_mode=None, threaded=False)
customer = Customer("None", "None", "None", 0, 0, 0)
beat = Beat("None", 6, "None", "None", "None","None", "None", "None", "None")
logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="1 week", compression="zip")

@bot.message_handler(commands=['help'])
def command_terms(message):
    bot.send_message(message.chat.id,
                     'Привет! Этот бот создан для автоматизированной публикации битов в канал Be at Space🚀\n'
                     'Мы постарались максимально ускорить процедуру офромления анкеты бита, чтобы Вы потратили как можно меньше своего времени\n'
                     'Бот поможет Вам заполнить все необходимые поля и скинет ссылку на оплату через сервис ЮКасса.\n'
                     'После подтверждения оплаты бит автоматически появится в канале, всё просто!\n'
                     '❗️Но есть три правила, которые необходимо соблюдать:'
                     '1. Запрещается ретранслировать в канал политическую повестку. Fuck politics.\n'
                     '2. Запрещается ретранслировать в канал аудиодорожки, отличные от битов.\n'
                     '3. Запрещается выкладывать чужие биты, оставляя ссылку на свои соцсети.\n'
                     'Надеемся, что нас ждёт плодотворное сотрудничество!'
                     'Если у Вас остались вопросы, то свяжитесь с администратором канала @olliethebroke')
@bot.message_handler(commands=['infobeat'])
def command_terms(message):
    bot.send_message(message.chat.id,
                     'Как узнать BPM и тональность бита❓\n'
                     'Вы можете воспользоваться сервисом определения BPM и тональности, вот ссылка⬇️\n'
                     'https://vocalremover.org/ru/key-bpm-finder\n'
                     'Рекомендуем указывать корректную информацию о Вашем бите, это поможет покупателям быстрее найти именно Ваш бит\n')
def download_mp3_file(file_id):
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{config.TOKEN}/{file_info.file_path}"
    r = requests.get(file_url, stream=True)
    if r.status_code == 200:
        beat.file_name = file_info.file_path.split('/')[-1]
        with open(beat.file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)
        return beat.file_name
    return None
def download_photo(file_id):
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{config.TOKEN}/{file_info.file_path}"
    r = requests.get(file_url, stream=True)
    if r.status_code == 200:
        beat.photo_file_name = file_info.file_path.split('/')[-1]
        with open(beat.photo_file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)
        return beat.photo_file_name
    return None
@bot.message_handler(commands = ['start', 'newbeat'])
def greetings(message):
    if(customer.isPutPhoto):
        os.remove(beat.photo)
    if(customer.flag):
        os.remove(beat.audio_file)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    continueButton = types.KeyboardButton("Давай начнём🔥")
    markup.row(continueButton)
    bot.send_message(message.chat.id,"Здравствуйте!\nЯ - бот канала Be at Space. Я помогу Вам разместить Ваши биты, чтоб их увидело как можно больше людей", reply_markup = markup)
    markup.one_time_keyboard = True
    bot.register_next_step_handler(message, getGenre)
    customer.isTriedPromo = 0
def getGenre(message):
    if not message.text:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        continueButton = types.KeyboardButton("Давай начнём🔥")
        markup.row(continueButton)
        bot.send_message(message.chat.id, "Нажмите на кнопку Давай начнём🔥, чтобы начать заполнение анкеты бита", reply_markup=markup)
        bot.register_next_step_handler(message, getGenre)
        return
    if message.text == 'Давай начнём🔥':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Hip-Hop🚫🧢")
        button2 = types.KeyboardButton("RnB🎤")
        button3 = types.KeyboardButton("Drill🥷🏿")
        button4 = types.KeyboardButton("Trap🐍")
        button5 = types.KeyboardButton("Electronic📟")
        button6 = types.KeyboardButton("Rock🎸")
        markup.row(button1)
        markup.row(button2)
        markup.row(button3)
        markup.row(button4)
        markup.row(button5)
        markup.row(button6)
        markup.one_time_keyboard = True
        bot.send_message(message.chat.id, "Какой жанр у Вашего бита? Выберите из предложенных или напишите самостоятельно", reply_markup = markup)
        bot.register_next_step_handler(message, checkButton)
    elif message.text == '/newbeat' or message.text == '/start':
        greetings(message)
    elif message.text == '/infobeat':
        bot.send_message(message.chat.id,
                         'Как узнать BPM и тональность бита❓\n'
                         'Вы можете воспользоваться сервисом определения BPM и тональности, вот ссылка⬇️\n'
                         'https://vocalremover.org/ru/key-bpm-finder\n'
                         'Рекомендуем указывать корректную информацию о Вашем бите, это поможет покупателям быстрее найти именно Ваш бит\n')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        continueButton = types.KeyboardButton("Давай начнём🔥")
        markup.row(continueButton)
        bot.send_message(message.chat.id, "Нажмите на кнопку Давай начнём🔥, чтобы начать заполнение анкеты бита")
        bot.register_next_step_handler(message, getGenre)
        return
    elif message.text == '/help':
        bot.send_message(message.chat.id,
                         'Привет! Этот бот создан для автоматизированной публикации битов в канал Be at Space🚀\n'
                         'Мы постарались максимально ускорить процедуру офромления анкеты бита, чтобы Вы потратили как можно меньше своего времени\n'
                         'Бот поможет Вам заполнить все необходимые поля и скинет ссылку на оплату через сервис ЮКасса.\n'
                         'После подтверждения оплаты бит автоматически появится в канале, всё просто!\т'
                         '❗️Но есть три правила, которые необходимо соблюдать:'
                         '1. Запрещается ретранслировать в канал политическую повестку. Fuck politics.\n'
                         '2. Запрещается ретранслировать в канал аудиодорожки, отличные от битов.\n'
                         '3. Запрещается выкладывать чужие биты, оставляя ссылку на свои соцсети.\n'
                         'Надеемся, что нас ждёт плодотворное сотрудничество!'
                         'Если у Вас остались вопросы, то свяжитесь с администратором канала @olliethebroke')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        continueButton = types.KeyboardButton("Давай начнём🔥")
        markup.row(continueButton)
        bot.send_message(message.chat.id, "Нажмите на кнопку Давай начнём🔥, чтобы начать заполнение анкеты бита")
        bot.register_next_step_handler(message, getGenre)
        return
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        continueButton = types.KeyboardButton("Давай начнём🔥")
        markup.row(continueButton)
        bot.send_message(message.chat.id, "Нажмите на кнопку Давай начнём🔥, чтобы начать заполнение анкеты бита")
        bot.register_next_step_handler(message, getGenre)
        return
def checkButton(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Hip-Hop🚫🧢")
    button2 = types.KeyboardButton("RnB🎤")
    button3 = types.KeyboardButton("Drill🥷🏿")
    button4 = types.KeyboardButton("Trap🐍")
    button5 = types.KeyboardButton("Electronic📟")
    button6 = types.KeyboardButton("Rock🎸")
    markup.row(button1)
    markup.row(button2)
    markup.row(button3)
    markup.row(button4)
    markup.row(button5)
    markup.row(button6)
    markup.one_time_keyboard = True
    if not message.text:
        bot.send_message(message.chat.id, "Пожалуйста, напишите жанр текстом", reply_markup=markup)
        bot.register_next_step_handler(message, checkButton)
        return
    if message.text == '/newbeat' or message.text == '/start':
        greetings(message)
        return
    elif message.text == '/infobeat':
        bot.send_message(message.chat.id,
                         'Как узнать BPM и тональность бита❓\n'
                         'Вы можете воспользоваться сервисом определения BPM и тональности, вот ссылка⬇️\n'
                         'https://vocalremover.org/ru/key-bpm-finder\n'
                         'Рекомендуем Вам указывать корректную информацию о Вашем бите, это поможет покупателям быстрее найти именно Ваш бит\n')
        bot.send_message(message.chat.id,
                         "Какой жанр у Вашего бита? Выберите из предложенных или напишите самостоятельно",
                         reply_markup=markup)
        bot.register_next_step_handler(message, checkButton)
        return
    elif message.text == '/help':
        bot.send_message(message.chat.id,
                         'Привет! Этот бот создан для автоматизированной публикации битов в канал Be at Space🚀\n'
                         'Мы постарались максимально ускорить процедуру офромления анкеты бита, чтобы Вы потратили как можно меньше своего времени\n'
                         'Бот поможет Вам заполнить все необходимые поля и скинет ссылку на оплату через сервис ЮКасса.\n'
                         'После подтверждения оплаты бит автоматически появится в канале, всё просто!\т'
                         '❗️Но есть три правила, которые необходимо соблюдать:'
                         '1. Запрещается ретранслировать в канал политическую повестку. Fuck politics.\n'
                         '2. Запрещается ретранслировать в канал аудиодорожки, отличные от битов.\n'
                         '3. Запрещается выкладывать чужие биты, оставляя ссылку на свои соцсети.\n'
                         'Надеемся, что нас ждёт плодотворное сотрудничество!'
                         'Если у Вас остались вопросы, то свяжитесь с администратором канала @olliethebroke')
        bot.send_message(message.chat.id,
                         "Какой жанр у Вашего бита? Выберите из предложенных или напишите самостоятельно",
                         reply_markup=markup)
        bot.register_next_step_handler(message, checkButton)
        return
    beat.genre = message.text.strip()
    bot.send_message(message.chat.id, "Введите BPM🥁")
    bot.register_next_step_handler(message, getBPM)
def getBPM(message):
    if not message.text:
        bot.send_message(message.chat.id, "BPM должен быть числом. Введите BPM ещё раз, пожалуйста")
        bot.register_next_step_handler(message, getBPM)
        return
    beat.bpm = message.text.strip()
    if beat.bpm == '/newbeat' or beat.bpm == '/start':
        greetings(message)
        return
    elif beat.bpm == '/infobeat':
        bot.send_message(message.chat.id,
                         'Как узнать BPM и тональность бита❓\n'
                         'Вы можете воспользоваться сервисом определения BPM и тональности, вот ссылка⬇️\n'
                         'https://vocalremover.org/ru/key-bpm-finder\n'
                         'Рекомендуем указывать корректную информацию о Вашем бите, это поможет покупателям быстрее найти именно Ваш бит\n')
        bot.send_message(message.chat.id, "Введите BPM🥁")
        bot.register_next_step_handler(message, getBPM)
        return
    elif beat.bpm == '/help':
        bot.send_message(message.chat.id,
                         'Привет! Этот бот создан для автоматизированной публикации битов в канал Be at Space🚀\n'
                         'Мы постарались максимально ускорить процедуру офромления анкеты бита, чтобы Вы потратили как можно меньше своего времени\n'
                         'Бот поможет Вам заполнить все необходимые поля и скинет ссылку на оплату через сервис ЮКасса.\n'
                         'После подтверждения оплаты бит автоматически появится в канале, всё просто!\т'
                         '❗️Но есть три правила, которые необходимо соблюдать:'
                         '1. Запрещается ретранслировать в канал политическую повестку. Fuck politics.\n'
                         '2. Запрещается ретранслировать в канал аудиодорожки, отличные от битов.\n'
                         '3. Запрещается выкладывать чужие биты, оставляя ссылку на свои соцсети.\n'
                         'Надеемся, что нас ждёт плодотворное сотрудничество!'
                         'Если у Вас остались вопросы, то свяжитесь с администратором канала @olliethebroke')
        bot.send_message(message.chat.id, "Введите BPM🥁")
        bot.register_next_step_handler(message, getBPM)
        return
    if not beat.bpm.isdigit():
        bot.send_message(message.chat.id, "BPM должен быть числом. Введите BPM ещё раз, пожалуйста")
        bot.register_next_step_handler(message, getBPM)
        return
    if(int(beat.bpm) > 1000):
        bot.send_message(message.chat.id, "Воу, полегче! Их уши не готовы к такому звуку\nДавайте поставим поменьше🥶")
        bot.register_next_step_handler(message, getBPM)
        return
    elif(int(beat.bpm) < 10):
        bot.send_message(message.chat.id, "Ух ты, никогда такого не слушал!\nДавайте поставим побольше🥶")
        bot.register_next_step_handler(message, getBPM)
        return
    bot.send_message(message.chat.id, "Какая тональность у Вашего бита?🎹")
    bot.register_next_step_handler(message, getKey)
def getKey(message):
    if not message.text:
        bot.send_message(message.chat.id, "Пожалуйста, напишите тональность текстом")
        bot.register_next_step_handler(message, getKey)
        return
    beat.key = message.text.strip()
    if beat.key == '/newbeat' or beat.key == '/start':
        greetings(message)
        return
    elif beat.key == '/infobeat':
        bot.send_message(message.chat.id,
                         'Как узнать BPM и тональность бита❓\n'
                         'Вы можете воспользоваться сервисом определения BPM и тональности, вот ссылка⬇️\n'
                         'https://vocalremover.org/ru/key-bpm-finder\n'
                         'Рекомендуем указывать корректную информацию о Вашем бите, это поможет покупателям быстрее найти именно Ваш бит\n')
        bot.send_message(message.chat.id, "Какая тональность у Вашего бита?🎹")
        bot.register_next_step_handler(message, getKey)
        return
    elif beat.key == '/help':
        bot.send_message(message.chat.id,
                         'Привет! Этот бот создан для автоматизированной публикации битов в канал Be at Space🚀\n'
                         'Мы постарались максимально ускорить процедуру офромления анкеты бита, чтобы Вы потратили как можно меньше своего времени\n'
                         'Бот поможет Вам заполнить все необходимые поля и скинет ссылку на оплату через сервис ЮКасса.\n'
                         'После подтверждения оплаты бит автоматически появится в канале, всё просто!\т'
                         '❗️Но есть три правила, которые необходимо соблюдать:'
                         '1. Запрещается ретранслировать в канал политическую повестку. Fuck politics.\n'
                         '2. Запрещается ретранслировать в канал аудиодорожки, отличные от битов.\n'
                         '3. Запрещается выкладывать чужие биты, оставляя ссылку на свои соцсети.\n'
                         'Надеемся, что нас ждёт плодотворное сотрудничество!'
                         'Если у Вас остались вопросы, то свяжитесь с администратором канала @olliethebroke')
        bot.send_message(message.chat.id, "Какая тональность у Вашего бита?🎹")
        bot.register_next_step_handler(message, getKey)
        return
    if len(beat.key) > 3 or beat.key.isdigit():
        bot.send_message(message.chat.id, "Пожалуйста, используйте до трёх символов, например, C#m или Fm")
        bot.register_next_step_handler(message, getKey)
        return
    bot.send_message(message.chat.id,
                     "Записал, следуюший шаг - нужно создать тэги, например: drake_type_beat drake rnb.\nОни нужны, чтобы покупатели могли сразу найти нужные биты с помощью поиска.\nВведите до трех тэгов, испозьзуя пробел в качестве разделителя")
    bot.register_next_step_handler(message, getTags)
def getTags(message):
    if not message.text:
        bot.send_message(message.chat.id, "Пожалуйста, напишите тэги текстом")
        bot.register_next_step_handler(message, getTags)
        return
    if message.text == '/newbeat' or message.text == '/start':
        greetings(message)
        return
    elif message.text == '/infobeat':
        bot.send_message(message.chat.id,
                         'Как узнать BPM и тональность бита❓\n'
                         'Вы можете воспользоваться сервисом определения BPM и тональности, вот ссылка⬇️\n'
                         'https://vocalremover.org/ru/key-bpm-finder\n'
                         'Рекомендуем указывать корректную информацию о Вашем бите, это поможет покупателям быстрее найти именно Ваш бит\n')
        bot.send_message(message.chat.id, "Нужно создать тэги, например: drake_type_beat drake rnb.\nОни нужны, чтобы покупатели могли сразу найти нужные биты с помощью поиска.\nВведите до трех тэгов, испозьзуя пробел в качестве разделителя")
        bot.register_next_step_handler(message, getTags)
        return
    elif message.text == '/help':
        bot.send_message(message.chat.id,
                         'Привет! Этот бот создан для автоматизированной публикации битов в канал Be at Space🚀\n'
                         'Мы постарались максимально ускорить процедуру офромления анкеты бита, чтобы Вы потратили как можно меньше своего времени\n'
                         'Бот поможет Вам заполнить все необходимые поля и скинет ссылку на оплату через сервис ЮКасса.\n'
                         'После подтверждения оплаты бит автоматически появится в канале, всё просто!\т'
                         '❗️Но есть три правила, которые необходимо соблюдать:'
                         '1. Запрещается ретранслировать в канал политическую повестку. Fuck politics.\n'
                         '2. Запрещается ретранслировать в канал аудиодорожки, отличные от битов.\n'
                         '3. Запрещается выкладывать чужие биты, оставляя ссылку на свои соцсети.\n'
                         'Надеемся, что нас ждёт плодотворное сотрудничество!'
                         'Если у Вас остались вопросы, то свяжитесь с администратором канала @olliethebroke')
        bot.send_message(message.chat.id, "Нужно создать тэги, например: drake_type_beat drake rnb.\nОни нужны, чтобы покупатели могли сразу найти нужные биты с помощью поиска.\nВведите до трех тэгов, испозьзуя пробел в качестве разделителя")
        bot.register_next_step_handler(message, getTags)
        return
    text = message.text.strip()
    if len(text) > 80:
        bot.send_message(message.chat.id, "Слишком длинные тэги. Давайте попробуем заново")
        bot.register_next_step_handler(message,getTags)
        return
    number = len(text.split(" "))
    text = text.split(" ")
    if(number == 1):
        beat.tags = "#" + text[0]
    elif(number == 2):
        beat.tags = "#" + text[0] + " " + "#" + text[1]
    elif(number == 3):
        beat.tags = "#" + text[0] + " " + "#" + text[1] + " " + "#" + text[2]
    elif(number > 3):
        beat.tags = "#" + text[0] + " " + "#" + text[1] + " " + "#" + text[2]
    else:
        beat.tags = " "
    bot.send_message(message.chat.id, "Отлично! Теперь нужно отправить мне сам бит в формате mp3. Помните, что размер не должен превышать 20МБ")
    bot.register_next_step_handler(message, download_audio)
def download_audio(message):
    if message.text:
        if message.text == '/newbeat' or message.text == '/start':
            greetings(message)
            return
        elif message.text == '/infobeat':
            bot.send_message(message.chat.id,
                             'Как узнать BPM и тональность бита❓\n'
                             'Вы можете воспользоваться сервисом определения BPM и тональности, вот ссылка⬇️\n'
                             'https://vocalremover.org/ru/key-bpm-finder\n'
                             'Рекомендуем Вам указывать корректную информацию о Вашем бите, это поможет покупателям быстрее найти именно Ваш бит\n')
            bot.send_message(message.chat.id,
                             "Пожалуйста, отправьте бит")
            bot.register_next_step_handler(message, download_audio)
            return
        elif message.text == '/help':
            bot.send_message(message.chat.id,
                             'Привет! Этот бот создан для автоматизированной публикации битов в канал Be at Space🚀\n'
                             'Мы постарались максимально ускорить процедуру офромления анкеты бита, чтобы Вы потратили как можно меньше своего времени\n'
                             'Бот поможет Вам заполнить все необходимые поля и скинет ссылку на оплату через сервис ЮКасса.\n'
                             'После подтверждения оплаты бит автоматически появится в канале, всё просто!\т'
                             '❗️Но есть три правила, которые необходимо соблюдать:'
                             '1. Запрещается ретранслировать в канал политическую повестку. Fuck politics.\n'
                             '2. Запрещается ретранслировать в канал аудиодорожки, отличные от битов.\n'
                             '3. Запрещается выкладывать чужие биты, оставляя ссылку на свои соцсети.\n'
                             'Надеемся, что нас ждёт плодотворное сотрудничество!'
                             'Если у Вас остались вопросы, то свяжитесь с администратором канала @olliethebroke')
            bot.send_message(message.chat.id,
                             "Пожалуйста, отправьте бит")
            bot.register_next_step_handler(message, download_audio)
            return
        else:
            bot.send_message(message.chat.id, "Пожалуйста, отправьте бит")
            bot.register_next_step_handler(message, download_audio)
            return
    if not message.audio:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте бит")
        bot.register_next_step_handler(message, download_audio)
        return
    beat.audio_name = message.audio.file_name
    file = bot.get_file(message.audio.file_id)
    beat.audio_file = download_mp3_file(file.file_id)
    if beat.audio_file is None:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте бит")
        bot.register_next_step_handler(message, download_audio)
        return
    customer.flag = 1
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    noPhotoButton = types.KeyboardButton("Продолжить без обложки")
    markup.add(noPhotoButton)
    markup.one_time_keyboard = True
    bot.send_message(message.chat.id, "Скачал!✅\nЕсли Вы хотите добавить обложку Вашему биту, то отправьте фотографию в чат", reply_markup=markup)
    bot.register_next_step_handler(message, getPhoto)


def getPhoto(message):
    if message.text:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        noPhotoButton = types.KeyboardButton("Продолжить без обложки")
        markup.add(noPhotoButton)
        markup.one_time_keyboard = True
        if message.text == '/newbeat' or message.text == '/start':
            greetings(message)
            return
        elif message.text == 'Продолжить без обложки':
            customer.isPutPhoto = 0
            bot.send_message(message.chat.id,
                             "Для того, чтобы покупатели могли связаться с Вами, им нужна ссылка на Ваши соцсети. Это может быть ТГ-канал или паблик ВК💸")
            bot.register_next_step_handler(message, getRef)
            return
        elif message.text == '/infobeat':
            bot.send_message(message.chat.id,
                             'Как узнать BPM и тональность бита❓\n'
                             'Вы можете воспользоваться сервисом определения BPM и тональности, вот ссылка⬇️\n'
                             'https://vocalremover.org/ru/key-bpm-finder\n'
                             'Рекомендуем Вам указывать корректную информацию о Вашем бите, это поможет покупателям быстрее найти именно Ваш бит\n')
            bot.send_message(message.chat.id,
                             "Пожалуйста, отправьте фотографию, либо нажмите на кнопку ниже", reply_markup=markup)
            bot.register_next_step_handler(message, getPhoto)
            return
        elif message.text == '/help':
            bot.send_message(message.chat.id,
                             'Привет! Этот бот создан для автоматизированной публикации битов в канал Be at Space🚀\n'
                             'Мы постарались максимально ускорить процедуру офромления анкеты бита, чтобы Вы потратили как можно меньше своего времени\n'
                             'Бот поможет Вам заполнить все необходимые поля и скинет ссылку на оплату через сервис ЮКасса.\n'
                             'После подтверждения оплаты бит автоматически появится в канале, всё просто!\т'
                             '❗️Но есть три правила, которые необходимо соблюдать:'
                             '1. Запрещается ретранслировать в канал политическую повестку. Fuck politics.\n'
                             '2. Запрещается ретранслировать в канал аудиодорожки, отличные от битов.\n'
                             '3. Запрещается выкладывать чужие биты, оставляя ссылку на свои соцсети.\n'
                             'Надеемся, что нас ждёт плодотворное сотрудничество!'
                             'Если у Вас остались вопросы, то свяжитесь с администратором канала @olliethebroke')
            bot.send_message(message.chat.id,
                             "Пожалуйста, отправьте фотографию, либо нажмите на кнопку ниже", reply_markup=markup)
            bot.register_next_step_handler(message, getPhoto)
            return
        else:
            bot.send_message(message.chat.id, "Пожалуйста, отправьте фотографию, либо нажмите на кнопку ниже", reply_markup=markup)
            bot.register_next_step_handler(message, getPhoto)
            return
    if not message.photo:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        noPhotoButton = types.KeyboardButton("Продолжить без обложки")
        markup.add(noPhotoButton)
        markup.one_time_keyboard = True
        bot.send_message(message.chat.id, "Пожалуйста, отправьте фотографию, либо нажмите на кнопку ниже", reply_markup=markup)
        bot.register_next_step_handler(message, getPhoto)
        return
    photo = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    beat.photo = download_photo(photo.file_id)
    customer.isPutPhoto = 1
    bot.send_message(message.chat.id,
                     "Для того, чтобы покупатели могли связаться с Вами, им нужна ссылка на Ваши соцсети. Это может быть ТГ-канал или паблик ВК💸", reply_markup=None)
    bot.register_next_step_handler(message, getRef)
def getRef(message):
    if not message.text:
        bot.send_message(message.chat.id, "Пожалуйста, напишите ссылку текстом")
        bot.register_next_step_handler(message, getRef)
        return
    if message.text == "/newbeat" or message.text == '/start':
        greetings(message)
        return
    elif message.text == '/infobeat':
        bot.send_message(message.chat.id,
                         'Как узнать BPM и тональность бита❓\n'
                         'Вы можете воспользоваться сервисом определения BPM и тональности, вот ссылка⬇️\n'
                         'https://vocalremover.org/ru/key-bpm-finder\n'
                         'Рекомендуем Вам указывать корректную информацию о Вашем бите, это поможет покупателям быстрее найти именно Ваш бит\n')
        bot.send_message(message.chat.id, "Для того, чтобы покупатели могли связаться с Вами, им нужна ссылка на Ваши соцсети. Это может быть ТГ-канал или паблик ВК💸")
        bot.register_next_step_handler(message, getRef)
        return
    elif message.text == '/help':
        bot.send_message(message.chat.id,
                         'Привет! Этот бот создан для автоматизированной публикации битов в канал Be at Space🚀\n'
                         'Мы постарались максимально ускорить процедуру офромления анкеты бита, чтобы Вы потратили как можно меньше своего времени\n'
                         'Бот поможет Вам заполнить все необходимые поля и скинет ссылку на оплату через сервис ЮКасса.\n'
                         'После подтверждения оплаты бит автоматически появится в канале, всё просто!\т'
                         '❗️Но есть три правила, которые необходимо соблюдать:'
                         '1. Запрещается ретранслировать в канал политическую повестку. Fuck politics.\n'
                         '2. Запрещается ретранслировать в канал аудиодорожки, отличные от битов.\n'
                         '3. Запрещается выкладывать чужие биты, оставляя ссылку на свои соцсети.\n'
                         'Надеемся, что нас ждёт плодотворное сотрудничество!'
                         'Если у Вас остались вопросы, то свяжитесь с администратором канала @olliethebroke')
        bot.send_message(message.chat.id, "Для того, чтобы покупатели могли связаться с Вами, им нужна ссылка на Ваши соцсети. Это может быть ТГ-канал или паблик ВК💸")
        bot.register_next_step_handler(message, getRef)
        return
    customer.refToChannel = message.text.strip()
    bot.send_message(message.chat.id, "Последний шаг, напишите Вашу электронную почту для формирования чека оплаты＠")
    bot.register_next_step_handler(message, getMail)
def getMail(message):
    if not message.text:
        bot.send_message(message.chat.id, "Пожалуйста, напишите почту текстом")
        bot.register_next_step_handler(message, getMail)
        return
    if message.text == "/newbeat" or message.text == '/start':
        greetings(message)
        return
    elif message.text == '/infobeat':
        bot.send_message(message.chat.id,
                         'Как узнать BPM и тональность бита❓\n'
                         'Вы можете воспользоваться сервисом определения BPM и тональности, вот ссылка⬇️\n'
                         'https://vocalremover.org/ru/key-bpm-finder\n'
                         'Рекомендуем Вам указывать корректную информацию о Вашем бите, это поможет покупателям быстрее найти именно Ваш бит\n')
        bot.send_message(message.chat.id, "Напишите Вашу электронную почту для формирования чека оплаты＠")
        bot.register_next_step_handler(message, getMail)
        return
    elif message.text == '/help':
        bot.send_message(message.chat.id,
                         'Привет! Этот бот создан для автоматизированной публикации битов в канал Be at Space🚀\n'
                         'Мы постарались максимально ускорить процедуру офромления анкеты бита, чтобы Вы потратили как можно меньше своего времени\n'
                         'Бот поможет Вам заполнить все необходимые поля и скинет ссылку на оплату через сервис ЮКасса.\n'
                         'После подтверждения оплаты бит автоматически появится в канале, всё просто!\т'
                         '❗️Но есть три правила, которые необходимо соблюдать:'
                         '1. Запрещается ретранслировать в канал политическую повестку. Fuck politics.\n'
                         '2. Запрещается ретранслировать в канал аудиодорожки, отличные от битов.\n'
                         '3. Запрещается выкладывать чужие биты, оставляя ссылку на свои соцсети.\n'
                         'Надеемся, что нас ждёт плодотворное сотрудничество!'
                         'Если у Вас остались вопросы, то свяжитесь с администратором канала @olliethebroke')
        bot.send_message(message.chat.id, "Напишите Вашу электронную почту для формирования чека оплаты＠")
        bot.register_next_step_handler(message, getMail)
        return
    customer.email = message.text.strip()
    valid = validate_email(customer.email, verify=True)
    if not valid:
        bot.send_message(message.chat.id,
                             "Не могу найти такую почту, попробуйте ввести почтовый адреc заново")
        bot.register_next_step_handler(message, getMail)
        return
    bot.send_message(message.chat.id,
                "Готово! Перейдите по ссылке ниже, чтобы оплатить размещение бита. После оплаты Вы сможете моментально опубликовать его в канале Be at Space🚀")
    getPayment(message)
def getPayment(message):
    payment = Payment.create({
        "amount": {
            "value": "100.00",
            "currency": "RUB"
        },
        "receipt": {
            "items": [{
                "description": "Оплата публикации бита",
                "amount": {
                    "value": "100.00",
                    "currency": "RUB"
                },
                "vat_code": 1,
                "quantity": 1
            }],
            "email": str(customer.email)
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://web.telegram.org/k/#@be_at_space_bot"
        },
        "capture": True,
        "description": "Оплата публикации бита"
    }, uuid.uuid4())
    customer.payment_id = payment.id
    confirmation_url = payment.confirmation.confirmation_url
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Перейти к оплате", url = confirmation_url))
    bot.send_message(message.chat.id, "Сумма оплаты составит 100 рублей. Вот ссылка⬇️", reply_markup=markup)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    paidButton = types.KeyboardButton("Опубликовать бит")
    markup.row(paidButton)
    if customer.isTriedPromo == 0:
        promokodButton = types.KeyboardButton("У меня есть промокод")
        markup.row(promokodButton)
    markup.one_time_keyboard = True
    bot.send_message(message.chat.id, "Когда завершите оплату, нажмите на кнопку Опубликовать бит", reply_markup=markup)
    bot.register_next_step_handler(message, checkIsPaid)

def checkIsPaid(message):
    if not message.text:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        paidButton = types.KeyboardButton("Опубликовать бит")
        markup.row(paidButton)
        markup.one_time_keyboard = True
        if customer.isTriedPromo == 0:
            promokodButton = types.KeyboardButton("У меня есть промокод")
            markup.row(promokodButton)
        bot.send_message(message.chat.id, "Когда завершите оплату, нажмите на кнопку Опубликовать бит", reply_markup=markup)
        bot.register_next_step_handler(message, checkIsPaid)
        return
    if message.text == "Опубликовать бит":
        status = Payment.find_one(customer.payment_id)
        if status.status == "succeeded":
            successful_payment(message)
        elif status.status == "canceled":
            bot.send_message(message.chat.id, "Что-то пошло не так! \nПопробуйте совершить платёж заново, предварительно проверив наличие нужной суммы на банковском счёте.\nЕсли у Вас есть вопросы, то свяжитесь с администратором канала @olliethebroke")
        elif status.status == "expired_on_confirmation":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            newBeat = types.KeyboardButton("/newbeat")
            markup.row(newBeat)
            markup.one_time_keyboard = True
            bot.send_message(message.chat.id,
                             "Платёж не может быть выполнен, так как срок его подтверждения истёк⏰.\nЗаполните анкету бита заново.\n Если у Вас есть вопросы, то свяжитесь с администратором канала @olliethebroke", reply_markup=markup)
            os.remove(beat.file_name)
        else:
            bot.send_message(message.chat.id, "Metro Boomin хотел украсть Ваш бит! Мы ему успешно помешали👮, но оплата так и не прошла...\n"
                                              "Попробуйте оплатить заново, если ошибка повторится, то попробуйте провести транзакцию позже\n"
                                                "Если у Вас есть вопросы, то свяжитесь с администратором канала @olliethebroke")
            bot.register_next_step_handler(message, checkIsPaid)
            return
    elif message.text == "У меня есть промокод" and customer.isTriedPromo == 0:
        bot.send_message(message.chat.id, "Круто! Введите промокод⬇️", reply_markup=None)
        bot.register_next_step_handler(message, checkPromo)
    elif message.text == '/newbeat' or message.text == '/start':
        greetings(message)
    else:
        bot.send_message(message.chat.id, "Когда завершите оплату, нажмите на кнопку Опубликовать бит")
        bot.register_next_step_handler(message, checkIsPaid)
        return
def successful_payment(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    newBeat = types.KeyboardButton("/newbeat")
    markup.row(newBeat)
    bot.send_message(message.chat.id,
                     f"Платеж прошел успешно!", reply_markup=markup)
    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJ4ldkyWq_TMuKcA15tFhPGRHF4Rg-RgAC9QAD9wLID0dGmGHRUMixLwQ")
    sendInfo()

def checkPromo(message):
    if not message.text:
        bot.send_message(message.chat.id, "Пожалуйста, напишите промокод текстом")
        bot.register_next_step_handler(message, checkPromo)
        return
    flag = 0
    customer.isTriedPromo = 1
    inputPromo = message.text.strip()
    newLine = ""
    with open("promos.txt", "r") as fP, open("new.txt", "w") as fN:
        line = fP.readline()
        line = line.split(" ")
        for i in range(5):
            if line[i] == inputPromo:
                flag = 1
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                newBeat = types.KeyboardButton("/newbeat")
                markup.row(newBeat)
                bot.send_message(message.chat.id,
                                 "Промокод успешно активирован🥳\nБит будет опубликован в канале в течение несольких секунд",
                                 reply_markup=markup)
                sendInfo()
            else:
                newLine += line[i] + " "
        if flag == 1:
            newLine += ''.join(random.choices(string.ascii_lowercase, k=10))
            text = "#Промокоды\n" + newLine
            bot.send_message(chat_id="@baseofclients", text=text)
        else:
            bot.send_message(message.chat.id,
                         "Промокод не найден🙁\nСейчас скину Вам ссылку для оплаты")
            getPayment(message)
        fN.write(newLine)
    fP.close()
    fN.close()
    os.remove("promos.txt")
    os.rename("new.txt", "promos.txt")
def sendInfo():
    if customer.flag == 1:
        caption = customer.refToChannel + "\n" + "Жанр: " + beat.genre + "\n" + "BPM: " + beat.bpm + "🥁\n" + "Тональность: " + beat.key + "🎹\n" + "Тэги: " + beat.tags
        with open(beat.audio_file, 'rb') as f, open(beat.photo, 'rb') as p:
            if (customer.isPutPhoto):
                bot.send_photo(chat_id="@be_at_space", photo=p)
            bot.send_audio(chat_id="@be_at_space", audio = f, caption=caption, title=beat.audio_name, protect_content=True)
    os.remove(beat.audio_file)
    if(customer.isPutPhoto):
        os.remove(beat.photo)
    customer.isTriedPromo = 0
    customer.isPutPhoto = 0
    customer.flag = 0
    text = "#Клиенты\n" + customer.payment_id + "\n" + customer.refToChannel + "\n" + customer.email
    bot.send_message(chat_id="@baseofclients", text=text)

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(e)
        time.sleep(5)


