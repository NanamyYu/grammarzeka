import telebot
import json
from telebot import types

with open('config.json', 'r') as f:
    data = json.load(f)
    token = data['token']
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Меня зовут Граммазека, я бот, который проверяет знания русского языка с помощью викторин. Чтобы узнать, что я могу, набери ```/help```.')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Амогус.')

@bot.message_handler(commands=['quiz'])
def quiz(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    answer1=types.KeyboardButton("Ответ 1")
    answer2=types.KeyboardButton("Ответ 2")
    answer3=types.KeyboardButton("Ответ 3")
    answer4=types.KeyboardButton("Ответ 4")
    markup.add(answer1)
    markup.add(answer2)
    markup.add(answer3)
    markup.add(answer4)
    bot.send_message(message.chat.id, 'Вопрос', reply_markup=markup)

bot.infinity_polling()