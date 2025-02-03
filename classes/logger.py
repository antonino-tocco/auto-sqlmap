from datetime import datetime
from enum import Enum
from colorama import Fore

class LogLevel(Enum):
    ERROR = 1
    WARNING = 2
    DEBUG = 3
    INFO = 4


def cyan(text):
    print(Fore.CYAN + text + Fore.RESET)


def yellow(text):
    print(Fore.YELLOW + text + Fore.RESET)

def orange(text):
    print(Fore.LIGHTRED_EX + text + Fore.RESET)

def red(text):
    print(Fore.RED + text + Fore.RESET)

log_level = LogLevel.INFO

level_to_color = {
    LogLevel.ERROR: red,
    LogLevel.WARNING: orange,
    LogLevel.DEBUG: yellow,
    LogLevel.INFO: cyan
}


class Logger:
    @staticmethod
    def log(level, message):
        message = "{}: {}".format(datetime.now().strftime("%d-%m-%Y %H:%M"), message)
        if level in level_to_color:
            level_to_color[level](message)
        else:
            print(message)

    @staticmethod
    def error(message):
        if log_level.value >= LogLevel.ERROR.value:
            Logger.log(LogLevel.ERROR, message)

    @staticmethod
    def warning(message):
        if log_level.value >= LogLevel.WARNING.value:
            Logger.log(LogLevel.WARNING, message)

    @staticmethod
    def debug(message):
        if log_level.value >= LogLevel.DEBUG.value:
            Logger.log(LogLevel.DEBUG, message)

    @staticmethod
    def info(message):
        if log_level.value >= LogLevel.INFO.value:
            Logger.log(LogLevel.INFO, message)