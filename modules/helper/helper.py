import difflib
import os
import sys
from functools import wraps
from io import StringIO
from typing import Dict

import matplotlib.pyplot as plt

from modules.helper.header import Colors


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

    @wraps(func)
    def wrapper(*args, **kwargs):
        args[0].logger.info("Generating :: %s..", func.__doc__)
        plt.cla()
        plt.figure(figsize=(12, 6))
        plt.grid()
        ret = func(*args, **kwargs)
        plt.savefig(os.path.join(args[0].out_path, f"{func.__name__}.png"), bbox_inches="tight")
        return ret

    return wrapper


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


def assert_msg(expected: object, result: object) -> str:
    """Compare and print difference between 2 objects. Objects must have string reprensentation.

    Args:
        expected: theoritical value
        result: observed value

    Returns:
        Colored text difference between the string representation of the objects.
    """
    old, new = str(expected), str(result)

    bold = lambda text: f"{Colors.BOLD}{text}{Colors.RESET}"
    red = lambda text: f"{Colors.RED}{text}{Colors.RESET}"
    green = lambda text: f"{Colors.GREEN}{text}{Colors.RESET}"
    blue = lambda text: f"{Colors.BLUE}{text}{Colors.RESET}"
    white = lambda text: f"{Colors.RESET}{text}{Colors.RESET}"

    result = ""
    opcodes = difflib.SequenceMatcher(a=old, b=new).get_opcodes()
    for opcode, a0, a1, b0, b1 in opcodes:
        if opcode == "equal":
            result += white(old[a0:a1])
        elif opcode == "delete":
            result += red(old[a0:a1])
        elif opcode == "insert":
            result += green(new[b0:b1])
        elif opcode == "replace":
            result += red(old[a0:a1]) + green(new[b0:b1])

    return bold(red("\nTest Fail :: ")) + result
