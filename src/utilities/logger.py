import logging 
from datetime import datetime
import os
from typing import Callable, Optional

from constants import CLIENT_NAME
from utils import Err

def get_proper_logger(logger: logging.Logger, debugConsole: bool):
    logger.setLevel(logging.DEBUG)
    logger.propagate = False #avoid having multiple outputs

    ch = logging.StreamHandler()
    if debugConsole:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    ch.setFormatter(CustomFormatter(True))
    logger.addHandler(ch)

    if not os.path.exists("logs/"): os.mkdir("logs/")

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H.%M.%S")

    ch = logging.FileHandler(f"logs/{dt_string}.log")
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter(False))
    logger.addHandler(ch)

    return logger

class COLORS:
    pink = "\033[95m"
    blue = "\033[94m"
    cyan = "\033[96m"
    green = "\033[92m"
    grey = "\x1b[38;21m"
    yellow = "\033[93m"
    red = "\033[91m"
    bold = "\033[1m"
    underline = "\033[4m"
    reset = "\033[0m"

class CustomFormatter(logging.Formatter):
    LOG_COLORS = {
        logging.DEBUG: COLORS.grey,
        logging.INFO: COLORS.cyan,
        logging.WARNING: COLORS.yellow,
        logging.ERROR: COLORS.red,
        logging.CRITICAL: COLORS.pink,
    }
    
    is_console: bool
    reset_color: str
    underline_color: str
    
    def __init__(self, is_console_formatter: bool, fmt: str ="%(asctime)s %(levelname)s %(filename)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"):
        self.is_console = is_console_formatter
        if is_console_formatter:
            self.reset_color = COLORS.reset
            self.underline_color = COLORS.underline
        else:
            self.reset_color = ""
            self.underline_color = ""
        super().__init__(fmt, datefmt)
    
    def get_log_color(self, level: int):
        if self.is_console:
            return CustomFormatter.LOG_COLORS.get(level, COLORS.reset)
        return ""

    def format(self, record):
        log_color = self.get_log_color(record.levelno)

        # Format the message with the chosen color
        record.msg = f"{log_color}{record.msg}{self.reset_color}"

        # Format the filename and line number with underline
        record.filename = f"{self.underline_color}{record.filename.replace(".py", "")}:{record.lineno}{self.reset_color}"
        record.levelname = f"{log_color}[{record.levelname}]"

        return super().format(record)

#thanks https://stackoverflow.com/a/56944275 & https://stackoverflow.com/a/287944


# webhook_queue_func and empty here are to avoid circular imports.
def empty(*kargs):
    print("/!\\Webhook Manager not set yet./!\\")
    pass

# TODO: use logger extend to not overwrite filename/lineno
# TODO: only log additional in file.

# Actually filename not even used.
class CustomLogger:
    webhook_queue_func: Callable
    logger: logging.Logger
    def __init__(self, webhook_queue_func: Callable, filename: str) -> None:
        self.webhook_queue_func = webhook_queue_func
        self.logger = get_proper_logger(logging.getLogger(filename), True)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)
    
    def warn(self, message: str, additional: Optional[list[Err]] = None, send_webhook: bool = True):
        if send_webhook:
            self.webhook_queue_func(logging.WARN, "An warning was triggered.", message, additional=additional, footer=f"On {CLIENT_NAME}")
        self.logger.warning(message)
        if additional:
            for thing in additional:
                self.logger.warning(f"{thing.name}: {thing.content}")
    
    def error(self, message: str,  additional: Optional[list[Err]] = None, send_webhook: bool = True):
        if send_webhook:
            self.webhook_queue_func(logging.ERROR, "An error has occured.", message, additional=additional, footer=f"On {CLIENT_NAME}")
        self.logger.error(message)
        if additional:
            for thing in additional:
                self.logger.error(f"{thing.name}: {thing.content}")
    
    def critical(self, message: str,  additional: Optional[list[Err]] = None, send_webhook: bool = True):
        if send_webhook:
            self.webhook_queue_func(logging.CRITICAL, "A critical error has occured.", message, additional=additional, footer=f"On {CLIENT_NAME}")
        self.logger.critical(message)
        if additional:
            for thing in additional:
                self.logger.critical(f"{thing.name}: {thing.content}")


LOGGER = CustomLogger(empty, "logger")
