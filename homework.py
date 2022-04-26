import logging
import time
import os
from http import HTTPStatus

import requests
import telegram

from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error as error:
        logging.error(f'Ошибка отправки сообщения {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            response.raise_for_status()
        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()
        return response.json()
    except TypeError as error:
        logger.error(f'Object of type bytes is not JSON serializable {error}')
    except requests.exceptions.TimeoutError as error:
        logger.error(f'Ошибка ожидания: {error}')
    except requests.exceptions.RequestException as error:
        logger.error(f'Сервер вернул ошибку: {error}')
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')


def check_response(response):
    """Проверка полученных данных."""
    if type(response) is not dict:
        raise TypeError('Response не формата  dict')
    elif len(response) == 0:
        raise Exception('Response пустой')
    elif 'homeworks' not in response:
        raise Exception('отсутствует переменная в homeworks')
    elif type(response['homeworks']) is not list:
        raise Exception('Тип homeworks не list')
    else:
        return response['homeworks']


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус работы."""
    try:
        homework_name = homework['homework_name']
    except KeyError as error:
        logger.error(f'Неверный ответ сервера: {error}')
        raise
    try:
        homework_status = homework['status']
    except KeyError as error:
        logger.error(f'Неверный ответ сервера: {error}')
        raise

    if ((homework_status is None) or (
            homework_status == '')) or (
                (homework_status not in HOMEWORK_STATUSES)):
        raise KeyError(f'Ключ homework_status некорректен: {homework_status}')

    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    for token in tokens:
        if token is None:
            logger.critical(
                f'отсутствует необходимая для запуска бота переменная {token}')
            return False
    return True


def main():
    """Основная работа бота."""
    logger.info('Бот запущен')
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
    except telegram.error.InvalidToken as error:
        logging.error(f'Невалидный токен {error}')
    except telegram.error as error:
        logging.error(f'Ошибка запуска бота {error}')
    current_timestamp = int(time.time())

    while True:
        try:
            if check_tokens():
                response = get_api_answer(current_timestamp)
                homework = check_response(response)
                if len(homework) > 0:
                    homeworks = homework[0]
                    send_message(bot, parse_status(homeworks))
                    logger.info('Сообщение отправлено')
                else:
                    logger.debug('Отсутствие в ответе новых статусов')
        except Exception as error:
            current_timestamp = int(time.time())
            message = f'Сбой в работе: {error}'
            send_message(bot, message)
        else:
            current_timestamp = int(time.time())
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
