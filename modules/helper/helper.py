import logging
import os
import sys
import time
from io import StringIO
from logging.handlers import RotatingFileHandler
from typing import Dict, List

import matplotlib.pyplot as plt


class Capturing(list):
    """Capture stdout into a single buffer list.

    >>> def func():
            print('Hello')
            print('World')
    >>> with Capturing() as result:
            func()
    >>> result
    ['Hello', 'World']"""

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def verbose(func):
    """Verbose decorator"""

    def wrapper(*args, **kwargs):
        args[0].logger.info("Generating :: %s..", func.__doc__)
        plt.cla()
        plt.figure(figsize=(12, 6))
        plt.grid()
        ret = func(*args, **kwargs)
        plt.savefig(os.path.join(args[0].out_path, f"{func.__name__}.png"), bbox_inches="tight")
        return ret

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


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


def setup_custom_logger(
    name: str, filename: str = "log.log", verbose_: bool = False, filelog: bool = True, argv: List[str] = None
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

    # Simple formatter for non-verbose logging
    fmt, level = ("[{levelname:^7s}] {message}", logging.DEBUG) if verbose_ else ("## {message}", logging.INFO)

    # Add screen handler with custom formatter
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(
        logging.Formatter(
            fmt=fmt,
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    screen_handler.setLevel(level)
    logger.addHandler(screen_handler)

    return logger


def get_requests_header() -> Dict[str, str]:
    """Get requests header

    Returns:
        Header dictioanry with Accept-Encoding and User-Agent.

        {"Accept-Encoding": "identity",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
    """
    return {
        "Accept-Encoding": "identity",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    }


def get_tor_proxies(port: int = 9050) -> Dict[str, str]:
    """Get Tor socks proxies

    Args:
        port: Port number of the Tor socks proxy.

    Returns:
        Dictioanry with socks5h based http and https proxies.

        {"http": f"socks5h://127.0.0.1:9050",
        "https": f"socks5h://127.0.0.1:9050"}
    """
    return {
        "http": f"socks5h://127.0.0.1:{port}",
        "https": f"socks5h://127.0.0.1:{port}",
    }


def traceback_name(error: Exception) -> str:
    """Get traceback class names from an exception

    Args:
        error: Exception object.

    Returns:
        Exception traceback class names.
    """
    module = error.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return error.__class__.__name__
    return module + "." + error.__class__.__name__


class TorProxyException(Exception):
    "Exception raised for errors in the Tor proxy. This might happen if the Tor Service is running but the application is using a different port."
    error_code = 69


class TorServiceException(Exception):
    "Exception raised for errors in the Tor Service. This error is raised if the Tor Service is not running."
    error_code = 96
