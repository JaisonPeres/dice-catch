from telebot_router import TeleBot
import os
from segurobet import Segurobet
from datetime import datetime
from csv_writer import CsvWriter

seg = Segurobet()
app = TeleBot(__name__)

signals = {
    '🔴': 'red',
    '🔵': 'blue'
}

telegram_notify_list = os.environ.get('TELEGRAM_NOTIFY_LIST')
notify_list = [telegram_notify_list.split(',')]

value_to_bet = 5

timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
csv_file_log = f'./log-{timestamp}.csv'

# FUTURE CONFIG TO BET
@app.route('/command ?(.*)')
def example_command(message: dict, cmd: str):
    chat_from = message['chat']['id']
    msg = "Command Recieved: {}".format(cmd)
    app.send_message(chat_from, msg)


@app.route('(?!/).+')
def receive(message: dict):
    chat_from = message['chat']['id'] if 'id' in message['chat'] else ''
    chat_title = message['chat']['title'] if 'title' in message['chat'] else ''
    date = message['date'] if 'date' in message else ''
    user_msg = message['text'] if 'text' in message else ''

    if checkMessageOld(date):
        print(f'Message is old: {date}')
        return

    print(chat_title, f'"{chat_from}"', user_msg, parseDate(date))

    csv_writer = CsvWriter(csv_file_log)
    
    for signal, color in signals.items():
        if signal in user_msg:
            notify(f'Making bet on {color} with value {value_to_bet}')
            results = seg.makeBet(color, value_to_bet)
            csv_writer.add_row({
                'chat title': chat_title,
                'chat id': chat_from,
                'message': user_msg,
                'color': color,
                'value': value_to_bet,
                'date': parseDate(date),
                'results': results
            })
            break

def parseDate(date: str):
    return datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')

def checkMessageOld(date: int):
    date = datetime.fromtimestamp(date)
    now = datetime.now()
    return (now - date).seconds > 60

def notify(message: str):
    for notify in notify_list:
        app.send_message(notify, message)

if __name__ == '__main__':
    app.config['api_key'] = os.environ['TELEGRAM_API_KEY']
    app.poll(debug=True)