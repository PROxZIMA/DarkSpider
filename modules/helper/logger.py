import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler
from typing import List, Optional

from modules.helper.header import Colors


class RollingFileHandler(RotatingFileHandler):
    """Custom RotatingFileHandler for incremental infinite logging"""

    def __init__(self, filename, mode="a", maxBytes=0, backupCount=0, encoding=None, delay=False, errors=None):
        self.last_backup_cnt = int(time.time())
        self.filename = filename
        super(RollingFileHandler, self).__init__(
            filename="{0}.{2}.init{1}".format(*os.path.splitext(self.filename), self.last_backup_cnt),
            mode=mode,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
            errors=errors,
        )

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.last_backup_cnt += 1
        next_name = "{0}.{2}{1}".format(*os.path.splitext(self.filename), self.last_backup_cnt)
        self.baseFilename = next_name
        # self.rotate(self.baseFilename, next_name)
        if not self.delay:
            self.stream = self._open()


class CustomFormatter(logging.Formatter):
    """Custom colored logging formatter"""

    def __init__(self, **params):
        super().__init__(**params)
        self.FORMAT = self._style._fmt
        self.FORMATS = {
            logging.DEBUG: self._fmt.format(color=Colors.WHITE, reset=Colors.RESET),
            logging.INFO: self._fmt.format(color=Colors.BLUE, reset=Colors.RESET),
            logging.WARNING: self._fmt.format(color=Colors.YELLOW, reset=Colors.RESET),
            logging.ERROR: self._fmt.format(color=Colors.RED, reset=Colors.RESET),
            logging.CRITICAL: self._fmt.format(color=Colors.BOLD_RED, reset=Colors.RESET),
        }

    def format(self, record):
        self._style._fmt = self.FORMATS.get(record.levelno)
        result = logging.Formatter.format(self, record)
        self._style._fmt = self.FORMAT
        return result


def setup_custom_logger(
    name: str,
    filename: str = "log.log",
    verbose_: bool = False,
    filelog: bool = True,
    screenlog: bool = True,
    argv: Optional[List[str]] = None,
) -> logging.Logger:
    """Setup custom logger with stream and file handlers

    Args:
        name: Name of the logger.
        filename: Name of the log file.
        verbose_: Simple formatter for stream if False.
        filelog: Add FileHandler to logger if True.

    Returns:
        Logger object with custom handlers and formatters.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # Clear all handlers

    # Create file handler if filelog is True
    if filelog:
        file_handler = RollingFileHandler(filename=filename, mode="w", maxBytes=1024 * 1024 * 10)
        file_handler.setFormatter(None)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        # Add a single non-formatted terminal command to the log file only
        if argv:
            logger.info("$ python %s \n", " ".join(argv))

        # Update the formatter for the file handler
        logger.handlers[0].setFormatter(
            logging.Formatter(
                fmt="{asctime} |{levelname:^7s}| {filename}:{lineno} | {message}",
                style="{",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    # Return logger if screen log is disabled
    if not screenlog:
        return logger

    formatter, fmt, level = (
        (CustomFormatter, "[{color}{{levelname:^7s}}{reset}] {{message}}", logging.DEBUG)
        if verbose_
        else (logging.Formatter, "## {message}", logging.INFO)
    )

    # Add screen handler with custom formatter
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(
        formatter(
            fmt=fmt,
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    screen_handler.setLevel(level)
    logger.addHandler(screen_handler)

    return logger
