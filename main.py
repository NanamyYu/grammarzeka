import telebot
from telebot import types
import random
import json
import os
import logging

token = os.getenv("GRAMMARZEKA_TOKEN")
bot = telebot.TeleBot(token)
user_id = [int(os.getenv("user_id"))]

# Base logger
logger = logging.getLogger('grammarzeka')
logger.setLevel(logging.INFO)
logging.basicConfig(filename = "mylog.log", format = "%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s")

logger.info("Bot started")

questions = ["В новогоднюю ночь будет много ____.", "____ нужно делать обследование всего организма.", "На избирательном участке нам выдали специальные ____, которые нужно было заполнить и опустить в тумбу."]
answers = [["Феерверков", "Фейерверков", "Феирверков", "Фейирверков"], ["Переодически", "Переодичиски", "Периодически", "Периодичиски"], ["Бюлетени", "Бюллитени", "Бюллетени", "Бюлитени"]]
answersmask = [1, 2, 2]

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
    numquest = [0, 1, 2]
    if exc != None:
        numquest.remove(exc)
    num = random.choice(numquest)
    markup=types.InlineKeyboardMarkup()
    for i in range(4):
        if i == answersmask[num]:
            markup.add(types.InlineKeyboardButton(text=answers[num][i], callback_data="T"+str(num)))
        else:
            markup.add(types.InlineKeyboardButton(text=answers[num][i], callback_data="F"+str(num)))
    skip_button=types.InlineKeyboardButton(text="Пропустить", callback_data="skip"+str(num))
    end_button=types.InlineKeyboardButton(text="Закончить", callback_data="end")
    easy_button=types.InlineKeyboardButton(text="Слишком простой вопрос", callback_data="easy"+str(num))
    markup.add(skip_button, easy_button, end_button)
    bot.send_message(chat_id=call.message.chat.id, text=questions[num], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data[0] == "T" or call.data[0] == "F":
            num = int(call.data[1])
            next_q=types.InlineKeyboardMarkup()
            next_button=types.InlineKeyboardButton(text="Следующий вопрос", callback_data="skip"+str(num))
            end_button=types.InlineKeyboardButton(text="Закончить", callback_data="end")
            next_q.add(next_button, end_button)
            right_answer = str(answers[num][answersmask[num]])
            if call.data[0] == "T":
                logger.info("Passed question: " + str(num + 1))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*Правильно!* \nПолностью предложение звучит так: \n_" + str(questions[num]).replace("____", right_answer) + "_\nПродолжим?", reply_markup=next_q, parse_mode='Markdown')
            else:
                logger.info("Failed question: " + str(num + 1))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*Неверно.* \nПравильный ответ: *" + right_answer + "*, а полностью предложение звучит так: \n_" + str(questions[num]).replace("____", right_answer) + "_\nПродолжим?", reply_markup=next_q, parse_mode='Markdown')
        elif call.data[:4] == "skip":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, parse_mode='Markdown')
            if len(call.data) > 4:
                question(call, int(call.data[4]))
            else:
                question(call)
        elif call.data == "end":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
            bot.send_message(chat_id=call.message.chat.id, text=temp_text["quiz_end"])
        elif call.data[:4] == "easy":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
            num = int(call.data[4])
            logger.info("Easy question: " + str(num + 1))
            question(call, num)



bot.infinity_polling()