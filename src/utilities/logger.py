import logging 
from datetime import datetime
import os
import sys
from typing import Callable, Optional

from constants import CLIENT_NAME, DEBUG_CONSOLE
from utils import Err


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

LOG_COLORS = {
    logging.DEBUG: COLORS.grey,
    logging.INFO: COLORS.cyan,
    logging.WARNING: COLORS.yellow,
    logging.ERROR: COLORS.red,
    logging.CRITICAL: COLORS.pink,
}


class CustomFormatter(logging.Formatter):
    is_console: bool
    reset_color: str
    underline_color: str
    
    def __init__(self, is_console_formatter: bool, fmt: str ="%(asctime)s %(levelname)s %(filename)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"):
        self.is_console = is_console_formatter
        if self.is_console:
            self.reset_color = COLORS.reset
            self.underline_color = COLORS.underline
        else:
            self.reset_color = ""
            self.underline_color = ""
        super().__init__(fmt, datefmt)
    
    def get_log_color(self, level: int):
        if self.is_console:
            return LOG_COLORS.get(level, COLORS.reset)
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

class CustomLogger(logging.Logger):
    console_handler: logging.Handler
    file_handler: logging.Handler

    webhook_queue_func: Callable

    def __init__(self, name: str, webhook_queue_func: Callable, level: int | str = logging.DEBUG) -> None:
        self.webhook_queue_func = webhook_queue_func
        super().__init__(name, level)
        # Overwrite vars only AFTER the constructor is done.
        self.propagate = False
        self.console_handler = self._init_add_console_handler()
        self.file_handler = self._init_add_file_handler()

    def _init_add_console_handler(self):
        sh = logging.StreamHandler()
        if DEBUG_CONSOLE:
            sh.setLevel(logging.DEBUG)
        else:
            sh.setLevel(logging.INFO)
        sh.setFormatter(CustomFormatter(True))
        self.addHandler(sh)
        return sh
        
    def _init_add_file_handler(self):
        if not os.path.exists("logs/"): 
            os.mkdir("logs/")

        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y_%H.%M.%S")

        fh = logging.FileHandler(f"logs/{dt_string}.log", encoding="utf8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(CustomFormatter(False))
        self.addHandler(fh)
        return fh

    # Yoinked all from the logger's src
    def _make_record(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        sinfo = None
        if logging._srcfile:
            #IronPython doesn't track Python frames, so findCaller raises an
            #exception on some versions of IronPython. We trap it here so that
            #IronPython can use logging.
            try:
                fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel)
            except ValueError: # pragma: no cover
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        else: # pragma: no cover
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(self.name, level, fn, lno, msg, args,
                                 exc_info, func, extra, sinfo)

        return record
    

    def _emit(self, handler: logging.Handler, level, msg, args, exc_info = None, extra=None, stack_info=False, stacklevel=1):
        record = self._make_record(level, msg, args, exc_info, extra, stack_info, stacklevel)
        handler.emit(record)


    def _log(self, level: int, message: str, additional: Optional[list[Err]] = None, send_webhook: bool = True, webhook_message: str = "", *args):
        if send_webhook:
            self.webhook_queue_func(level, webhook_message, message, additional=additional, footer=f"On {CLIENT_NAME}")
        
        self._emit(self.console_handler, level, message, args, stacklevel=5)
        self._emit(self.file_handler, level, message, args, stacklevel=5)

        if additional:
            self._emit(self.console_handler, level, "Additional content has been logged to disk", args, stacklevel=5)
            for thing in additional:
                self._emit(self.file_handler, level, f"{thing.name}: {thing.content}", args, stacklevel=5)


    def debug(self, message: str):
        self._log(logging.DEBUG, message, send_webhook=False)

    def info(self, message: str):
        self._log(logging.INFO, message, send_webhook=False)

    def warn(self, message: str, additional: Optional[list[Err]] = None, send_webhook: bool = True):
        self._log(logging.WARNING, message, additional, send_webhook, webhook_message="A warning was triggered.")

    
    def error(self, message: str,  additional: Optional[list[Err]] = None, send_webhook: bool = True):
        self._log(logging.ERROR, message, additional, send_webhook, webhook_message="An error has occured.")

    
    def critical(self, message: str,  additional: Optional[list[Err]] = None, send_webhook: bool = True):  
        self._log(logging.CRITICAL, message, additional, send_webhook, webhook_message="A critical error has occured.")

    

LOGGER = CustomLogger("logger", empty)
