# Dice Catch Bot

## Description
This bot is a simple script that receives messages from a Telegram bot and make bets on a dice game.

## Requirements
- Python 3.12 or higher
- Pipenv
- Virtualenv
- Telegram Bot API Key
- Telegram Chat ID
- Segurobet Account

## Run Locally

1. Install venv
```bash
sudo apt-get install python3-venv
```

2. Init virtual environment
```bash
python3 -m venv dice-catch-venv
```

3. Activate the virtual environment
```bash
source dice-catch-venv/bin/activate
```

4. Install pipenv to manage dependencies
```bash
pip install pipenv
```


4. Install the dependencies
```bash
pipenv install
```

5. Adjust variables in the .env file
```bash
PIPENV_VERBOSITY=-1

TELEGRAM_NOTIFY_LIST=12131313,13131313

TELEGRAM_API_KEY=AXAXAXAXAXXAXAX

SEGUROBET_CATCH_URL=https://segurobet.com.br...
SEGUROBET_CATCH_USERNAME=user
SEGUROBET_CATCH_PASSWORD=password
```

6. Run the script
```bash
pipenv run python main.py
```