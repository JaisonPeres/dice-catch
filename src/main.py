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
    if checkMessageOld(date):
        return
    logger.warning('Webdrive started')
    notify('Webdrive started')
    notify_init_bot()
    seg.init(IS_SANDBOX)

@app.route('/stop')
def stop_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if checkMessageOld(date):
        return
    notify('Webdrive stopped')
    logger.warning('Webdrive stopped')
    seg.stop()

@app.route('/refresh')
def refresh_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if checkMessageOld(date):
        return
    notify('Webdrive refreshing...')
    logger.warning('Webdrive refreshing...')
    seg.refresh()

@app.route('/help')
def help_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if checkMessageOld(date):
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

    if checkMessageOld(date):
        return

    logger.info(f'{chat_title} "{chat_from}" {user_msg} {parseDate(date)}')

    base_log = {
        'chat_title': chat_title,
        'chat_id': chat_from,
        'message': user_msg,
        'date': parseDate(date),
    }
    
    processMessage(user_msg, base_log)

def processMessage(message: str, base_log: dict):
    for signal_msg, signal_key in signals.items():
        if signal_msg in message:
            base_log['signal'] = signal_key
            processSignal(signal_key, base_log)
            break
    for result_msg, result_key in results.items():
        if result_msg in message:
            base_log['result'] = result_key
            processResult(result_key, base_log)
            break

def processSignal(signal: str, base_log: dict):
    signal_file = CsvFile(f'./log-signal-{timestamp}.csv')
    logger.info(f'Received signal: {signal}')
    notify(f'Making bet on {signal} with value {value_to_bet}')
    result = seg.bet(signal, value_to_bet)
    result = str(result).replace(',', '-').replace('[', '').replace(']', '').replace(' ', '').replace("'", "")
    signal_file.add_row({**base_log, result: result})
    pass

def processResult(result: str, base_log: dict):
    result_file = CsvFile(f'./log-result-{timestamp}.csv')
    result_file.add_row({**base_log})
    countResult(result)
    pass

def countResult(result_key: str):
    count_result_file = CsvFile(count_results_file)

    result_id = uuid.uuid4()
    result_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_red = 0
    total_green = 0
    icon = '🟩' if result_key == 'green' else '🟥'

    if os.path.isfile(count_results_file):
        df = count_result_file.load()
        if 'result' not in df.columns:
            df['result'] = ''
            if result_key == 'red':
                total_red = 1
                # max_red_counter.increment()
            elif result_key == 'green':
                total_green = 1
                # max_red_counter.reset()
            count_result_file.add_row({
                'icon': icon,
                'id': result_id,
                'date': result_date,
                'result': result_key,
                'total_green': total_green,
                'total_red': total_red
            })
            notify(f'✅ {total_green} ❌ {total_red}')
            return

        total_red = len(df[df['result'] == 'red'])
        total_green = len(df[df['result'] == 'green'])
    
    if result_key == 'red':
        total_red += 1
    elif result_key == 'green':
        total_green += 1

    logger.info(f'Total green: {total_green}')
    logger.info(f'Total red: {total_red}')

    notify(f'✅ {total_green} ❌ {total_red}')

    count_result_file.add_row({
        'icon': icon,
        'id': result_id,
        'date': result_date,
        'result': result_key,
        'total_red': total_red,
        'total_green': total_green
    })


def parseDate(date: str):
    return datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')

def checkMessageOld(date: int):
    date = datetime.fromtimestamp(date)
    return date < init_date

def notify(message: str):
    for notify in notify_list:
        app.send_message(notify, message)

def exit_handler():
    logger.warning('Exiting...')
    sys.exit(0)

def notify_init_bot():
    message = [
        '🚨 WEBDRIVER STARTED 🚨\n',
        f'🕹️ Mode: {"DEMO" if IS_SANDBOX else "REAL"}\n',
        f'📅 Starting at: {init_date_str}\n',
        f'💵 Value: {value_to_bet}\n',
        '⏱️ Waiting for signals and results...'
    ]
    notify(''.join(message))

if __name__ == '__main__':
    user_input = input("Init bot with DEMO MODE enabled? (y/n): ")
    if user_input.lower() == "y":
        IS_SANDBOX = True
    else:
        IS_SANDBOX = False

    logger.clear()
    logger.title('Dice Catch')
    logger.subtitle('Bot for catching dice signals and auto make bets\n')
    logger.info(f'Starting at: {init_date_str}')
    logger.success('Bot listening')
    logger.success('Waiting for /start command')
    app.config['api_key'] = telegram_api_key
    notify('Bot started')
    notify(' /start to start the webdriver')
    app.poll(debug=True)