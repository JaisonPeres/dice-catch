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
    '🔴': 'banker',
    '🔵': 'player',
}

results = {
    '✅': 'green',
    '❌': 'red'
}

telegram_api_key = os.environ['TELEGRAM_API_KEY']
telegram_notify_list = os.environ['TELEGRAM_NOTIFY_LIST']
notify_list = telegram_notify_list.split(',')
value_to_bet = 5.0
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
    logger.warning('Webdrive is starting...')
    notify('Carregando jogo...')
    seg.init(IS_SANDBOX)
    amount = seg.getAmountFloat()
    notify_init_bot(amount)

@app.route('/stop')
def stop_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if checkMessageOld(date):
        return
    if (seg.isStarted()):
        notify('Encerrando jogo...')
        logger.warning('Webdrive is stopping...')
        seg.stop()
        logger.warning('Webdrive stopped')
        notify('Jogo encerrado')
    else:
        notify('Jogo não iniciado')
        logger.warning('Webdrive not started')

@app.route('/refresh')
def refresh_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if checkMessageOld(date):
        return
    notify('Atualizando o jogo...')
    logger.warning('Webdrive refreshing...')
    seg.refresh()

@app.route('/restart')
def refresh_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if checkMessageOld(date):
        return
    notify('Reiniciando o jogo...')
    logger.warning('Webdrive restarting...')
    seg.stop()
    seg.init(IS_SANDBOX)

@app.route('/help')
def help_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if checkMessageOld(date):
        return
    message = [
        'BOT HELPER\n\n',
        '/help - Exibe comandos\n',
        '/start - Inicia o jogo\n',
        '/stop - Encerra o jogo\n',
        '/refresh - Atualiza o jogo\n',
        '/restart - Reinicia o jogo\n',
        '/amount - Exibe o saldo da banca\n',
    ]

    notify(''.join(message))

@app.route('/amount')
def help_command(message: dict):
    date = message['date'] if 'date' in message else ''
    if checkMessageOld(date):
        return
    amout = seg.getAmount()

    notify(f'💵 Saldo: {amout}')

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
        'date': parseDate(date)
    }
    
    processMessage(user_msg, base_log)

def processMessage(message: str, base_log: dict):
    for signal_msg, signal_key in signals.items():
        if signal_msg in message:
            base_log['signal'] = signal_key
            processSignal(signal_key, base_log)
            break
    # for result_msg, result_key in results.items():
    #     if result_msg in message:
    #         base_log['result'] = result_key
    #         processResult(result_key, base_log)
    #         break

def processSignal(signal: str, base_log: dict):
    signal_file = CsvFile(f'./log-signal-{timestamp}.csv')
    logger.info(f'Received signal: {signal}')
    icon = '🔴' if signal == 'banker' else '🔵'
    notify(f'✨ Fazendo aposta em {icon} {signal} com o valor {floatToCurrency(value_to_bet)} ...')
    result = seg.bet(signal, value_to_bet)
    if result == None:
        notify('❌ Erro ao fazer aposta')
        signal_file.add_row({**base_log, 'error': 'Erro ao fazer aposta'})
        return
    processResult(signal, result)
    signal_file.add_row({**base_log})
    logger.info(f'Result: {result}')
    pass

def processResult(signal: str, result: dict):
    winner = result['winner']
    if winner == 'banker':
        winner = '🔴 Banker'
    elif winner == 'player':
        winner = '🔵 Player'
    elif winner == 'tie':
        winner = '🟡 Tie'
    result_green = 'green' in result and type(result['green']) == bool and result['green'] == True or False
    result_green = '✅ Green' if result_green else '❌ Red'
    result_amount = result['amount']
    red_counter = result['red_counter']
    green_counter = result['green_counter']
    tie_counter = result['tie_counter']
    result_label = '⚠️ Empate' if winner == '🟡 Tie' else result_green
    message = [
        f'{result_label}\n',
        f'Resultado: {winner}\n',
        f'Saldo: {floatToCurrency(result_amount)}\n',
        'Placar\n',
        f'✅ Greens: {green_counter}\n',
        f'❌ Reds: {red_counter}\n',
        f'⚠️ Empates: {tie_counter}\n'
    ]
    notify(''.join(message))
    result_file = CsvFile(f'./log-result-{timestamp}.csv')
    result_file.add_row({
        'result': result_green,
        'signal': signal,
        'amount': result_amount,
        'winner': winner,
        'red_counter': red_counter,
        'green_counter': green_counter,
        'tie_counter': tie_counter
    })
    # countResult(result)
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

def floatToCurrency(value: float):
    a = '{:,.2f}'.format(value)
    b = a.replace(',','v')
    c = b.replace('.',',')
    return f'R$ {c}'.replace('v','.')

def notify(message: str):
    for notify in notify_list:
        app.send_message(notify, message)

def exit_handler():
    logger.warning('Exiting...')
    sys.exit(0)

def notify_init_bot(amount: float):
    message = [
        '🚨 Jogo Iniciado 🚨\n',
        f'Modo: {"DEMO" if IS_SANDBOX else "REAL"}\n',
        f'Iniciou às: {init_date_str}\n',
        f'Valor por aposta: {floatToCurrency(value_to_bet)}\n',
        f'Saldo: {floatToCurrency(amount)}\n'
    ]
    notify(''.join(message))
    notify('Aguardando sinais...')

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
    notify('Bot iniciado')
    notify('/start para iniciar o jogo')
    app.poll(debug=True)