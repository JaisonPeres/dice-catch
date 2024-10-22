# Dice Catch Bot

## Description
This bot is a simple script that receives messages from a Telegram bot and make bets on a dice game.

## Requirements
- Python 3.12 or higher
- Pipenv
- Virtualenv
- AWS S3 Bucket
- AWS Credentials
- Database URL

## Run Locally

1. Install venv
```bash
sudo apt-get install python3-venv
```

2. Init virtual environment
```bash
python3 -m venv payface-venv
```

3. Activate the virtual environment
```bash
source payface-venv/bin/activate
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
BUCKET_NAME=your-bucket-name
CSV_FILE_INPUT=your-csv-file-name.csv
CSV_FILE_OUTPUT=output.csv
```

6. Run the script
```bash
pipenv run python script-file-example.py
```