import telebot
import json
from telebot import types
import random
import json

with open('config.json', 'r') as f:
    data = json.load(f)
    token = data['token']
bot = telebot.TeleBot(token)

questions = ["В новогоднюю ночь будет много ____.", "____ нужно делать обследование всего организма.", "На избирательном участке нам выдали специальные _____, которые нужно было заполнить и опустить в тумбу."]
answers = [["феерверков", "фейерверков", "феирверков", "фейирверков"], ["переодически", "переодичиски", "периодически", "периодичиски"], ["бюлетени", "бюллитени", "бюллетени", "бюлитени"]]
answersmask = [1, 2, 2]


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Меня зовут Граммазека, я бот, который проверяет знания русского языка с помощью викторин. Чтобы узнать, что я могу, набери /help.', parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "*Граммазека* (то есть я) - бот для проверки знания русского языка. Путем вопросов на правильность написания слова он помогает запоминать сложные слова и не ошибаться. \n \n _Список команд:_ \n /quiz - начинает викторину на знание русского языка. Формат: `/quiz` \n /help - выдает это сообщение. Формат: `/help`", parse_mode='Markdown')

@bot.message_handler(commands=['quiz'])
def quiz(message):
    start_quiz=types.InlineKeyboardMarkup()
    start_button=types.InlineKeyboardButton(text="Старт", callback_data="skip")
    start_quiz.add(start_button)
    bot.send_message(chat_id=message.chat.id, text="Начнем викторину! Я буду присылать предложения с пропущенным словом, а Вам надо будет выбрать, какой вариант пропущенного слова верен.", reply_markup=start_quiz)


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
    markup.add(skip_button, end_button)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=questions[num], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data[0] == "T" or call.data[0] == "F":
            num = int(call.data[1])
            next_q=types.InlineKeyboardMarkup()
            next_button=types.InlineKeyboardButton(text="Следующий вопрос", callback_data="skip"+str(num))
            end_button=types.InlineKeyboardButton(text="Закончить", callback_data="end")
            next_q.add(next_button, end_button)
            if call.data[0] == "T":
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Молодец. Продолжим?", reply_markup=next_q)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Неверно. Правильный ответ: " + str(answers[num][answersmask[num]]) + ".\nПродолжим?", reply_markup=next_q)
        elif call.data[:4] == "skip":
            if len(call.data) > 4:
                question(call, int(call.data[4]))
            else:
                question(call)
        elif call.data == "end":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Викторина завершена. Если хотите, чтобы я снова задал Вам вопросы, напишите /quiz.")

bot.infinity_polling()