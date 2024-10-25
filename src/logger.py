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

    def info(self, message):
        print(f'{bcolors.OKBLUE}[{self.context}] {message}{bcolors.ENDC}')

    def error(self, message):
        print(f'{bcolors.FAIL}[{self.context}] {message}{bcolors.ENDC}')

    def warning(self, message):
        print(f'{bcolors.WARNING}[{self.context}] {message}{bcolors.ENDC}')
    
    def success(self, message):
        print(f'{bcolors.OKGREEN}[{self.context}] {message}{bcolors.ENDC}')