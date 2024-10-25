import pyfiglet
from rich import print as rprint

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Logger:
    def __init__(self, context: str):
        self.context = context
        pass

    def info(self, message: str):
        print(f'{bcolors.OKCYAN}INFO: {bcolors.HEADER}[{self.context}] {bcolors.ENDC}{message}{bcolors.ENDC}')

    def error(self, message: str, details):
        print(f'{bcolors.FAIL}ERROR: {bcolors.HEADER}[{self.context}] {bcolors.ENDC}{message}{bcolors.ENDC}', details)

    def warning(self, message: str):
        print(f'{bcolors.WARNING}WARNING: {bcolors.HEADER}[{self.context}] {bcolors.ENDC}{message}{bcolors.ENDC}')
    
    def success(self, message: str):
        print(f'{bcolors.OKGREEN}SUCCESS: {bcolors.HEADER}[{self.context}] {bcolors.ENDC}{message}{bcolors.ENDC}')
    
    def title(self, message: str):
        rprint(pyfiglet.figlet_format(message, font='slant'))
    
    def subtitle(self, message: str):
        print(f'{bcolors.OKGREEN}{bcolors.BOLD}{message}{bcolors.ENDC}')

    def clear(self):
        print('\033[H\033[J')