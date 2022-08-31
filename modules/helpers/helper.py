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
