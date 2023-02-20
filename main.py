import telebot
from telebot import types
import random
import json
import os
import logging
import jsonlines
import pandas
import datetime
import schedule
import time
import threading
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
        history[str(message.chat.id)]["Join"] = datetime.datetime.today().strftime("%d.%m.%Y %H:%M:%S")
        history[str(message.chat.id)]["Last seen"] = datetime.datetime.today().strftime("%d.%m.%Y %H:%M:%S")
        history[str(message.chat.id)]["Games"] = 0
        history[str(message.chat.id)]["QperGame"] = 0
        history[str(message.chat.id)]["Questions now"] = 0
        history[str(message.chat.id)]["QCount"] = 0
        history[str(message.chat.id)]["Difficulty"] = "middle"
        write_history()
    help(message)
    # bot.send_message(message.chat.id, temp_text["hello_message"], parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help(message):
    read_history()
    if str(message.chat.id) not in history.keys():
        bot.send_message(chat_id=message.chat.id, text=temp_text["forgor"])
        return
    bot.send_message(message.chat.id, temp_text["help_message"], parse_mode='Markdown')

@bot.message_handler(commands=['settings'])
def settings(message):
    markup=types.InlineKeyboardMarkup()
    dif_button=types.InlineKeyboardButton(text="Сложность", callback_data="dif")
    markup.add(dif_button)
    bot.send_message(chat_id=message.chat.id, text="Выберите пункт:", reply_markup=markup)

@bot.message_handler(commands=['quiz'])
def quiz(message):
    get_message_for_logfile("Game started", message.chat.id, needqnum=False)
    read_history()
    if str(message.chat.id) not in history.keys():
        bot.send_message(chat_id=message.chat.id, text=temp_text["forgor"])
        return
    start_quiz=types.InlineKeyboardMarkup()
    start_button=types.InlineKeyboardButton(text="Старт", callback_data="skip")
    start_quiz.add(start_button)
    bot.send_message(chat_id=message.chat.id, text=temp_text["quiz_start"], reply_markup=start_quiz)

def question(call):
    global numword
    read_history()
    history[str(call.message.chat.id)]["Questions now"] += 1
    history[str(call.message.chat.id)]["Now"] = random.choice(list(all_questions - set(history[str(call.message.chat.id)]["Successful"]) - set(history[str(call.message.chat.id)]["Easy"])))
    write_history()
    markup=types.InlineKeyboardMarkup()
    numword = int(sentences['using_word_id'][history[str(call.message.chat.id)]["Now"]])
    true_button = random.choice(range(len(sentences['complex_words'][history[str(call.message.chat.id)]["Now"]][numword]['distortions']) + 1))
    fake_button = 0
    for i in range(len(sentences['complex_words'][history[str(call.message.chat.id)]["Now"]][numword]['distortions']) + 1):
        if i == true_button:
            markup.add(types.InlineKeyboardButton(text=sentences['complex_words'][history[str(call.message.chat.id)]["Now"]][numword]['word'], callback_data="T"))
        else:
            fake_word = sentences['complex_words'][history[str(call.message.chat.id)]["Now"]][numword]['distortions'][fake_button]
            markup.add(types.InlineKeyboardButton(text=fake_word, callback_data="F" + fake_word))
            fake_button += 1
    skip_button=types.InlineKeyboardButton(text="Пропустить", callback_data="skip")
    easy_button=types.InlineKeyboardButton(text="Слишком просто", callback_data="easy")
    markup.add(skip_button, easy_button, end_button)
    bot.send_message(chat_id=call.message.chat.id, text="❓" + sentences['sentence'][history[str(call.message.chat.id)]["Now"]].replace(sentences['complex_words'][history[str(call.message.chat.id)]["Now"]][numword]['word'],  "\_\_\_\_"), reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global numword, history
    read_history()
    if str(call.message.chat.id) not in history.keys():
        bot.send_message(chat_id=call.message.chat.id, text=temp_text["forgor_q"])
        return
    history[str(call.message.chat.id)]["Last seen"] = datetime.datetime.today().strftime("%d.%m.%Y %H:%M:%S")
    write_history()
    if call.message:
        if call.data[0] == "T" or call.data[0] == "F":
            # num = int(call.data[1])
            next_q=types.InlineKeyboardMarkup()
            next_button=types.InlineKeyboardButton(text="Следующий вопрос", callback_data="skip")
            next_q.add(next_button, end_button)
            if call.data[0] == "T":
                read_history()
                history[str(call.message.chat.id)]["Successful"].append(history[str(call.message.chat.id)]["Now"])
                write_history()
                get_message_for_logfile("Question passed", history[str(call.message.chat.id)]["Now"], call.message.chat.id)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❗️" + sentences['sentence'][history[str(call.message.chat.id)]["Now"]].replace(sentences['complex_words'][history[str(call.message.chat.id)]["Now"]][numword]['word'],  sentences['complex_words'][history[str(call.message.chat.id)]["Now"]][numword]['word'].upper()) + "\n\n✅Правильно!✅\n\nПродолжим?", reply_markup=next_q)
            else:
                get_message_for_logfile("Question failed", history[str(call.message.chat.id)]["Now"], call.message.chat.id)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❗️" + sentences['sentence'][history[str(call.message.chat.id)]["Now"]].replace(sentences['complex_words'][history[str(call.message.chat.id)]["Now"]][numword]['word'],  sentences['complex_words'][history[str(call.message.chat.id)]["Now"]][numword]['word'].upper()) + "\n\n❌Неверно.❌\nПравильный ответ: " + sentences['complex_words'][history[str(call.message.chat.id)]["Now"]][numword]['word'] + ".\nТы выбрал: " + call.data[1:] + ".\n\nПродолжим?", reply_markup=next_q)
        elif call.data == "skip":
            read_history()
            history[str(call.message.chat.id)]["Now"] = None
            write_history()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
            if len(call.data) > 4:
                question(call)
            else:
                question(call)
        elif call.data == "end":
            get_message_for_logfile("Game ended", call.message.chat.id, needqnum=False)
            read_history()
            history[str(call.message.chat.id)]["Now"] = None
            history[str(call.message.chat.id)]["Games"] += 1
            history[str(call.message.chat.id)]["QperGame"] *= history[str(call.message.chat.id)]["Games"] - 1
            history[str(call.message.chat.id)]["QperGame"] += history[str(call.message.chat.id)]["Questions now"]
            history[str(call.message.chat.id)]["QperGame"] /= history[str(call.message.chat.id)]["Games"]
            history[str(call.message.chat.id)]["QCount"] += history[str(call.message.chat.id)]["Questions now"]
            history[str(call.message.chat.id)]["Questions now"] = 0
            write_history()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
            bot.send_message(chat_id=call.message.chat.id, text=temp_text["quiz_end"])
        elif call.data == "easy":
            read_history()
            history[str(call.message.chat.id)]["Easy"].append(history[str(call.message.chat.id)]["Now"])
            write_history()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
            get_message_for_logfile("Easy question", history[str(call.message.chat.id)]["Now"], call.message.chat.id)
            question(call)
        elif call.data == "dif":
            read_history()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Текущая сложность:" + history[str(call.message.chat.id)]["Difficulty"])

def get_message_for_logfile(message, num=None, user_id="", needqnum=True):
    if num != None and needqnum:
        logger.info(message + "\t" + str(num) + "\t" + str(user_id))
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

def log_saver():
    get_message_for_logfile("Logfile sended", needqnum=False)
    with open("log.log", "rb") as f:
        bot.send_document(chat_id=os.getenv("TG_ID"), document=f, caption="Log "+datetime.datetime.today().strftime("%d.%m.%Y %H:%M:%S"))

def sched_save():
    schedule.every(3595).seconds.do(log_saver)
    while True:
        schedule.run_pending()
        time.sleep(1)


# Users history
history = {}
try:
    read_history()
except:
    write_history()

get_message_for_logfile("Bot started")

threading.Thread(target=sched_save).start()

bot.infinity_polling()
