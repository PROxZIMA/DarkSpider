import shutil
import sys
from typing import List, Tuple

HEADER = r"""
        ⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣶⣾⣿⣧⡀⠀⢀⣶⣶⣤⣤⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠤⠴⠶⠿⠿⠿⠿⠿⠿⠿⢿⣿⣿⣿⣰⣿⣿⣿⠛⠛⠛⠛⠛⠛⠓⠲⠶⠄⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⢀⣀⣠⣤⣴⣶⣾⣆⠀⢀⣾⣿⣿⠟⠀⠀⠀⣰⣷⣶⣦⣤⣄⣀⡀⠀⠀⠀⠀⠀⠀
        ⠀⠒⠒⠚⠛⠛⠛⠛⠛⠛⣿⣿⣿⣷⣿⣿⣿⠏⠀⠀⢀⣼⣿⣿⡿⠻⠿⠿⠿⠿⠿⠷⠶⠤⠤⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⡿⠃⠀⠀⢠⣾⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⣷⡄⠀⠀⠘⢿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠠⠤⢤⣤⣤⣤⣤⣴⣶⣿⣿⣿⡿⣿⣿⣿⣆⠀⠀⠈⢻⣿⣿⣷⣴⣶⣶⣶⣶⣶⠶⠶⠒⠒⠀
        ⠀⠀⠀⠀⠀⠈⠉⠙⠛⠿⠿⣿⠏⠀⠈⢿⣿⣿⣦⠀⠀⠀⠻⡿⠿⠟⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠒⠲⠶⣶⣶⣶⣶⣶⣶⣶⣾⣿⣿⣿⠹⣿⣿⣿⣤⣤⣤⣤⣤⣤⡴⠶⠶⠒⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠛⠿⢿⣿⡟⠁⠀⠘⠿⠿⠟⠛⠋⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

    ____             __   _____       _     __
   / __ \____ ______/ /__/ ___/____  (_)___/ /__  _____
  / / / / __ `/ ___/ //_/\__ \/ __ \/ / __  / _ \/ ___/
 / /_/ / /_/ / /  / ,<  ___/ / /_/ / / /_/ /  __/ /
/_____/\__,_/_/  /_/|_|/____/ .___/_/\__,_/\___/_/
                           /_/

    Multithreaded Crawler and Extractor for Dark Web

"""


class Colors:
    """ANSI color codes"""

    BLACK = "\033[0;90m"
    RED = "\033[0;91m"
    GREEN = "\033[0;92m"
    YELLOW = "\033[0;93m"
    BLUE = "\033[0;94m"
    PURPLE = "\033[0;95m"
    CYAN = "\033[0;96m"
    WHITE = "\033[0;97m"
    BOLD_BLACK = "\033[1;90m"
    BOLD_RED = "\033[1;91m"
    BOLD_GREEN = "\033[1;92m"
    BOLD_YELLOW = "\033[1;93m"
    BOLD_BLUE = "\033[1;94m"
    BOLD_PURPLE = "\033[1;95m"
    BOLD_CYAN = "\033[1;96m"
    BOLD_WHITE = "\033[1;97m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    RESET = "\033[0m"

    # cancel SGR codes if we don't write to a terminal
    if not __import__("sys").stdout.isatty():
        for _ in dir():
            if _[0] != "_" and isinstance(_, str):
                locals()[_] = ""
    else:
        # set Windows console in VT mode
        if __import__("platform").system() == "Windows":
            kernel32 = __import__("ctypes").windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            del kernel32


def gradient_print(
    texts: str, start_color: Tuple[int, int, int], end_color: Tuple[int, int, int], disable: bool = False
) -> None:
    """
    print gradients on your terminal

    Args:
        texts: Multiline text to print
        start_color: start_color R G B
        end_color: end_color R G B
        disable: Mono output
    """
    fmt = lambda r, g, b: f"\033[38;2;{r};{g};{b}m"
    texts = texts.split("\n")
    steps = max(len(x) for x in texts)
    padding = (shutil.get_terminal_size().columns - steps) // 2

    if disable:
        for text in texts:
            print(" " * padding + text)
        return

    rs: List[int] = [start_color[0]]
    gs: List[int] = [start_color[1]]
    bs: List[int] = [start_color[2]]

    for step in range(1, steps):
        rs.append(round(start_color[0] + (end_color[0] - start_color[0]) * step / steps))
        gs.append(round(start_color[1] + (end_color[1] - start_color[1]) * step / steps))
        bs.append(round(start_color[2] + (end_color[2] - start_color[2]) * step / steps))

    grad = list(
        zip(
            rs,  # [255, 127,   0]
            gs,  # [0,   127, 255]
            bs,  # [0,     0,   0]
        )
    )

    for text in texts:
        sys.stdout.write(" " * padding)

        try:
            for i, char in enumerate(text):
                color = grad[i]
                sys.stdout.write(fmt(*color) + char)
            sys.stdout.write("\n")
        finally:
            sys.stdout.write(Colors.RESET)
            sys.stdout.flush()


if __name__ == "__main__":
    for i in dir(Colors):
        if i[0:1] != "_" and i != "RESET":
            print(f"{i:>16} {getattr(Colors, i) + i + Colors.RESET}")
