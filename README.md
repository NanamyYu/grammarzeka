# Граммазека
Граммазека - квиз-бот по русскому языку, выполненный в качестве курсового проекта студентками ПМИ ФКН НИУ ВШЭ Гареевой Алисой и Шатской Лизой.

Путем вопросов на правильность написания он помогает запоминать сложные слова и не ошибаться.

Бот хостится тут: [https://t.me/grammarzeka_bot](https://t.me/grammarzeka_bot)

## Команды

`/start` - выдает приветственное сообщение. Формат: `/start`

`/quiz` - начинает викторину на знание русского языка. Формат: `/quiz` 

`/help` - выдает сообщение-шпаргалку с объяснением, что это за бот и какие команды он умеет выполнять. Формат: `/help`

## Установка своего бота
Для начала клонируйте репозиторий себе на устройство:
```
git clone https://github.com/NanamyYu/grammarzeka
cd grammarzeka
```
Установите все зависимости:
```
python3 -m pip install requirements.txt
```
Создайте бота с помощью [@BotFather](https://t.me/BotFather). Сохраните его токен в системных переменных под именем `GRAMMARZEKA_TOKEN`.

Запустите бота:
```
python3 main.py
```
