from telebot_router import TeleBot
import os
from segurobet import Segurobet
from datetime import datetime
from csv_file import CsvFile
import uuid
from logger import Logger
import sys
from counter import Counter

seg = Segurobet()
app = TeleBot(__name__)
logger = Logger('Bot')

signals = {
    '🔴': 'red',
    '🔵': 'blue',
}

results = {
    '✅': 'green',
    '❌': 'red'
}

telegram_api_key = os.environ['TELEGRAM_API_KEY']
telegram_notify_list = os.environ['TELEGRAM_NOTIFY_LIST']
notify_list = telegram_notify_list.split(',')
value_to_bet = 5
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
count_results_file = f'./log-count-results-{timestamp}.csv'
init_date = datetime.now()
init_date_str = init_date.strftime('%Y-%m-%d %H:%M:%S')
IS_SANDBOX = True

max_red_counter = Counter(1)

@app.route('/start')
def start_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if preventOldMessages(date):
        return
    logger.warning('Webdrive started')
    notify('Webdrive started')
    notify_init_bot()
    seg.init(IS_SANDBOX)

@app.route('/stop')
def stop_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if preventOldMessages(date):
        return
    notify('Webdrive stopped')
    logger.warning('Webdrive stopped')
    seg.stop()

@app.route('/refresh')
def refresh_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if preventOldMessages(date):
        return
    notify('Webdrive refreshing...')
    logger.warning('Webdrive refreshing...')
    seg.refresh()

@app.route('/help')
def help_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if preventOldMessages(date):
        return
    message = [
        'BOT HELPER\n\n',
        '/start - Start the webdrive\n',
        '/stop - Stop the webdrive\n',
        '/refresh - Refresh the webdrive\n',
        '/help - Show this message\n',
    ]

    notify(''.join(message))

# PROCESS TELEGRAM MESSAGE
@app.route('(?!/).+')
def receive(message: dict):
    chat_from = message['chat']['id'] if 'id' in message['chat'] else ''
    chat_title = message['chat']['title'] if 'title' in message['chat'] else ''
    date = message['date'] if 'date' in message else ''
    user_msg = message['text'] if 'text' in message else ''

    if preventOldMessages(date):
        return

    # analyze message

def parseDate(date: str):
    return datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')

def preventOldMessages(date: int):
    date = datetime.fromtimestamp(date)
    return date < init_date

def notify(message: str):
    for notify in notify_list:
        app.send_message(notify, message)

if __name__ == '__main__':
    app.config['api_key'] = telegram_api_key
    app.poll(debug=True)