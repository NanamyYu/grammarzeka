import telebot
import json
from telebot import types

with open('config.json', 'r') as f:
    data = json.load(f)
    token = data['token']
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет\! Меня зовут Граммазека, я бот, который проверяет знания русского языка с помощью викторин\. Чтобы узнать, что я могу, набери `/help`\.', parse_mode='MarkdownV2')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Амогус.')

@bot.message_handler(commands=['quiz'])
def quiz(message):
    start_quiz=types.InlineKeyboardMarkup()
    start_button=types.InlineKeyboardButton(text="Старт", callback_data="skip")
    start_quiz.add(start_button)
    bot.send_message(chat_id=message.chat.id, text="Начнем викторину! Я буду присылать предложения с пропущенным словом, а Вам надо будет выбрать, какой вариант пропущенного слова верен.", reply_markup=start_quiz)


def question(call):
    markup=types.InlineKeyboardMarkup()
    answer1=types.InlineKeyboardButton(text="Неправильный ответ", callback_data="False")
    answer2=types.InlineKeyboardButton(text="Правильный ответ", callback_data="True")
    answer3=types.InlineKeyboardButton(text="Неправильный ответ", callback_data="False")
    answer4=types.InlineKeyboardButton(text="Неправильный ответ", callback_data="False")
    skip_button=types.InlineKeyboardButton(text="Пропустить", callback_data="skip")
    markup.add(answer1, answer2, answer3, answer4, skip_button)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вопрос", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "True" or call.data == "False":
            next_q=types.InlineKeyboardMarkup()
            next_button=types.InlineKeyboardButton(text="Следующий вопрос", callback_data="skip")
            next_q.add(next_button)
            if call.data == "True":
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Молодец.", reply_markup=next_q)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Дурак, что ли? Написано же, неправильный ответ. Зачем сюда нажимать вообще?", reply_markup=next_q)
        elif call.data == "skip":
            question(call)

bot.infinity_polling()