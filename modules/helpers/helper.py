import logging
import os
import sys
from io import StringIO
from logging.handlers import RotatingFileHandler

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

    def __init__(self, filename, mode="w", maxBytes=0, backupCount=0, encoding=None, delay=False):
        self.last_backup_cnt = 0
        super(RollingFileHandler, self).__init__(
            filename=filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay
        )

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.last_backup_cnt += 1
        next_name = "{0}.{2}{1}".format(*os.path.splitext(self.baseFilename), self.last_backup_cnt)
        self.rotate(self.baseFilename, next_name)
        if not self.delay:
            self.stream = self._open()


def setup_custom_logger(name, verbose_, filelog, filename):
    """Setup custom logger with stream and file handlers"""
    formatter = logging.Formatter(
        fmt="{asctime} [{levelname:^7s}] [{filename}:{lineno}] {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    screen_handler.setLevel(logging.DEBUG)

    if verbose_ is False:
        screen_handler.setFormatter(
            logging.Formatter(
                fmt="## {message}",
                style="{",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        screen_handler.setLevel(logging.INFO)

    logger.addHandler(screen_handler)

    if filelog:
        file_handler = RollingFileHandler(filename=filename, mode="w", maxBytes=10 * 1024 * 1024)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    return logger


def get_requests_header():
    """Get requests header"""
    return {
        "Accept-Encoding": "identity",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    }


def get_tor_proxies(port):
    """Get Tor socks proxies"""
    return {
        "http": f"socks5h://127.0.0.1:{port}",
        "https": f"socks5h://127.0.0.1:{port}",
    }


def traceback_name(error):
    """Get traceback name"""
    module = error.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return error.__class__.__name__
    return module + "." + error.__class__.__name__


class TorProxyException(Exception):
    "Exception raised for errors in the Tor proxy. This might happen if the Tor is running but the application is using a different port."
    pass
