import telebot
from telebot import types
import random
import json
import os
import logging
import jsonlines
import pandas
import time
from logging.handlers import TimedRotatingFileHandler

token = os.getenv("GRAMMARZEKA_TOKEN")
bot = telebot.TeleBot(token)

# Base logger
logger = logging.getLogger('grammarzeka')
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler(
    "log.log", when="h", interval=1, backupCount=12
)
handler.setFormatter(logging.Formatter("%(asctime)s\t%(levelname)s\t%(lineno)d\t%(message)s"))
handler.setLevel(logging.INFO)
logger.addHandler(handler)



# Загрузка сообщений
with jsonlines.open('labs/jsonl/alisa_selezneva.jsonl') as f:
    sentences = pandas.DataFrame(f)

# Default buttons
end_button=types.InlineKeyboardButton(text="Закончить", callback_data="end")

# Question setup
num = None
numword = None
all_questions = {i for i in range(sentences.shape[0] - 1)}

with open("message_templates.json", "r") as f:
    temp_text = json.load(f)


@bot.message_handler(commands=['start'])
def start_message(message):
    global history
    read_history()
    if str(message.chat.id) not in history.keys():
        get_message_for_logfile("New user", message.chat.id)
        history[str(message.chat.id)] = {}
        history[str(message.chat.id)]["Successful"] = []
        history[str(message.chat.id)]["Easy"] = []
        history[str(message.chat.id)]["Now"] = None
        write_history()
    bot.send_message(message.chat.id, temp_text["hello_message"], parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, temp_text["help_message"], parse_mode='Markdown')

@bot.message_handler(commands=['quiz'])
def quiz(message):
    start_quiz=types.InlineKeyboardMarkup()
    start_button=types.InlineKeyboardButton(text="Старт", callback_data="skip")
    start_quiz.add(start_button)
    bot.send_message(chat_id=message.chat.id, text=temp_text["quiz_start"], reply_markup=start_quiz)

def question(call, exc=None):
    # numquest = [0, 1, 2]
    # if exc != None:
    #     numquest.remove(exc)
    global num, numword
    read_history()
    num = random.choice(list(all_questions - set(history[str(call.message.chat.id)]["Successful"]) - set(history[str(call.message.chat.id)]["Easy"])))
    history[str(call.message.chat.id)]["Now"] = num
    write_history()
    markup=types.InlineKeyboardMarkup()
    numword = random.choice(range(len(sentences['complex_words'][num])))
    true_button = random.choice(range(len(sentences['complex_words'][num][numword]['distortions']) + 1))
    fake_button = 0
    for i in range(len(sentences['complex_words'][num][numword]['distortions']) + 1):
        if i == true_button:
            markup.add(types.InlineKeyboardButton(text=sentences['complex_words'][num][numword]['word'], callback_data="T"))
        else:
            markup.add(types.InlineKeyboardButton(text=sentences['complex_words'][num][numword]['distortions'][fake_button], callback_data="F"))
            fake_button += 1
    skip_button=types.InlineKeyboardButton(text="Пропустить", callback_data="skip"+str(num))
    easy_button=types.InlineKeyboardButton(text="Слишком простой вопрос", callback_data="easy"+str(num))
    markup.add(skip_button, easy_button, end_button)
    bot.send_message(chat_id=call.message.chat.id, text="❓" + sentences['sentence'][num].replace(sentences['complex_words'][num][numword]['word'],  "\_\_\_\_"), reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global num, numword, history
    if num == None:
        num = history[str(call.message.chat.id)]["Now"]
    if call.message:
        if call.data[0] == "T" or call.data[0] == "F":
            # num = int(call.data[1])
            next_q=types.InlineKeyboardMarkup()
            next_button=types.InlineKeyboardButton(text="Следующий вопрос", callback_data="skip")
            next_q.add(next_button, end_button)
            if call.data[0] == "T":
                read_history()
                history[str(call.message.chat.id)]["Successful"].append(num)
                write_history()
                read_stats()
                stats[str(num)][0] += 1
                write_stats()
                get_message_for_logfile("Question passed")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❗️" + sentences['sentence'][num].replace(sentences['complex_words'][num][numword]['word'],  sentences['complex_words'][num][numword]['word'].upper()) + "\n\n✅Правильно!✅\n\nПродолжим?", reply_markup=next_q, parse_mode='Markdown')
            else:
                read_stats()
                stats[str(num)][1] += 1
                write_stats()
                get_message_for_logfile("Question failed")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❗️" + sentences['sentence'][num].replace(sentences['complex_words'][num][numword]['word'],  sentences['complex_words'][num][numword]['word'].upper()) + "\n\n❌Неверно.❌\nПравильный ответ: " + sentences['complex_words'][num][numword]['word'] + ".\n\nПродолжим?", reply_markup=next_q, parse_mode='Markdown')
        elif call.data[:4] == "skip":
            read_history()
            history[str(call.message.chat.id)]["Now"] = None
            write_history()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, parse_mode='Markdown')
            if len(call.data) > 4:
                question(call, int(call.data[4]))
            else:
                question(call)
        elif call.data == "end":
            read_history()
            history[str(call.message.chat.id)]["Now"] = None
            write_history()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
            bot.send_message(chat_id=call.message.chat.id, text=temp_text["quiz_end"])
        elif call.data[:4] == "easy":
            read_history()
            history[str(call.message.chat.id)]["Easy"].append(num)
            write_history()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
            get_message_for_logfile("Easy question", num + 1)
            question(call, num)

def get_message_for_logfile(message, user_id=""):
    if num != None:
        logger.info(message + "\t" + str(num))
    else:
        logger.info(message + "\t" + str(user_id))


def read_history():
    global history
    with open('history.json') as f:
        history = json.load(f)
    
def write_history():
    global history
    with open('history.json', 'w') as f:
        json.dump(history, f)

def read_stats():
    global stats
    with open('stats.json') as f:
        stats = json.load(f)

def write_stats():
    global stats
    with open('stats.json', 'w') as f:
        json.dump(stats, f)

# Passed and failed counts
stats = {i: (0, 0) for i in range(sentences.shape[0])}
try:
    read_stats()
except:
    write_stats()

# Users history
history = {}
try:
    read_history()
except:
    write_history()

get_message_for_logfile("Bot started")

bot.infinity_polling()
