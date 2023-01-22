# Telegram-bot

## Описание:
Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.
Присылает сообщения, когда статус изменен.

## Технологии:
Python 3.8
python-dotenv 0.19.0
python-telegram-bot 13.7

## Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
git clone https://github.com/AlexGriv/homework_bot.git
cd homework_bot
Cоздать и активировать виртуальное окружение:
python -m venv env
source env/bin/activate
Установить зависимости из файла requirements.txt:
python -m pip install --upgrade pip
pip install -r requirements.txt

## Записать в переменные окружения (файл .env) необходимые ключи:
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

## Запустить проект:
python homework.py
