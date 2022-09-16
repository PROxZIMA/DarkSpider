import os
import sys
from io import StringIO

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
        if args[0].verbose:
            print(f"## {func.__doc__}...")
        plt.cla()
        plt.figure(figsize=(12, 6))
        plt.grid()
        ret = func(*args, **kwargs)
        plt.savefig(
            os.path.join(args[0].out_path, f"{func.__name__}.png"), bbox_inches="tight"
        )
        return ret

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


def get_requests_header():
    """Get requests header"""
    return {
        "Accept-Encoding": "identity",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    }


def get_tor_proxies(port=9050):
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
