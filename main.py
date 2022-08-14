import telebot
from telebot import types
import random
import json
import os
import logging
import jsonlines
import pandas

token = os.getenv("GRAMMARZEKA_TOKEN")
bot = telebot.TeleBot(token)

# Base logger
logger = logging.getLogger('grammarzeka')
logger.setLevel(logging.INFO)
logging.basicConfig(filename = "mylog.log", format = "%(asctime)s\t%(levelname)s\t%(funcName)s\t%(lineno)d\t%(message)s")


# Загрузка сообщений
with jsonlines.open('labs/jsonl/alisa_selezneva.jsonl') as f:
    sentences = pandas.DataFrame(f)

# questions = ["В новогоднюю ночь будет много ____.", "____ нужно делать обследование всего организма.", "На избирательном участке нам выдали специальные ____, которые нужно было заполнить и опустить в тумбу."]
# answers = [["Феерверков", "Фейерверков", "Феирверков", "Фейирверков"], ["Переодически", "Переодичиски", "Периодически", "Периодичиски"], ["Бюлетени", "Бюллитени", "Бюллетени", "Бюлитени"]]
# answersmask = [1, 2, 2]


# Default buttons
end_button=types.InlineKeyboardButton(text="Закончить", callback_data="end")


with open("message_templates.json", "r") as f:
    temp_text = json.load(f)


@bot.message_handler(commands=['start'])
def start_message(message):
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
    num = random.choice(range(15223))
    markup=types.InlineKeyboardMarkup()
    numword = random.choice(range(len(sentences['complex_words'][num])))
    markup.add(types.InlineKeyboardButton(text=sentences['complex_words'][num][numword]['word'], callback_data="T"))
    for i in range(len(sentences['complex_words'][num][numword]['distortions'])):
        markup.add(types.InlineKeyboardButton(text=sentences['complex_words'][num][numword]['distortions'][i], callback_data="F"))
    skip_button=types.InlineKeyboardButton(text="Пропустить", callback_data="skip"+str(num))
    easy_button=types.InlineKeyboardButton(text="Слишком простой вопрос", callback_data="easy"+str(num))
    markup.add(skip_button, easy_button, end_button)
    bot.send_message(chat_id=call.message.chat.id, text=sentences['sentence'][num].replace(sentences['complex_words'][num][numword]['word'],  "\_\_\_\_"), reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data[0] == "T" or call.data[0] == "F":
            # num = int(call.data[1])
            next_q=types.InlineKeyboardMarkup()
            next_button=types.InlineKeyboardButton(text="Следующий вопрос", callback_data="skip")
            next_q.add(next_button, end_button)
            if call.data[0] == "T":
                get_message_for_logfile("Question passed")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*Правильно!*\n\nПродолжим?", reply_markup=next_q, parse_mode='Markdown')
            else:
                get_message_for_logfile("Question failed")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*Неверно.*\n\nПродолжим?", reply_markup=next_q, parse_mode='Markdown')
        elif call.data[:4] == "skip":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, parse_mode='Markdown')
            if len(call.data) > 4:
                question(call, int(call.data[4]))
            else:
                question(call)
        elif call.data == "end":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, parse_mode='Markdown')
            bot.send_message(chat_id=call.message.chat.id, text=temp_text["quiz_end"])
        elif call.data[:4] == "easy":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, parse_mode='Markdown')
            num = int(call.data[4])
            get_message_for_logfile("Easy question", num + 1)
            question(call, num)

def get_message_for_logfile(message, user_id=None, num=None):
    logger.info(message + "\t" + str(num))


bot.infinity_polling()
get_message_for_logfile("Bot started")