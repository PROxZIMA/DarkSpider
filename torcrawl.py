#!/usr/bin/python
"""
DarkSpider is a python script to crawl and extract (regular or onion)
webpages through TOR network.

usage: python torcrawl.py [options]
python torcrawl.py -u l0r3m1p5umD0lorS1t4m3t.onion
python torcrawl.py -v -w -u http://www.github.com -o github.htm
python torcrawl.py -v -u l0r3m1p5umD0lorS1t4m3t.onion -c -d 2 -p 5
python torcrawl.py -v -w -u http://www.github.com -c -d 2 -p 5 -e -f GitHub

General:
-h, --help         : Help
-g, --gui          : Open with GUI backend.
-v, --verbose      : Show more informations about the progress
-u, --url *.onion  : URL of Webpage to crawl or extract
-w, --without      : Without the use of Relay TOR
-s, --visualize    : Visualize the graphs and insights from the crawled data

Extract:
-e, --extract           : Extract page's code to terminal or file.
                          (Defualt: terminal)
-i, --input filename    : Input file with URL(s) (seperated by line)
-o, --output [filename] : Output page(s) to file(s) (for one page)
-y, --yara              : Yara keyword search page categorisation
                          read in from /res folder. 0 search whole html object.
                          1 search only the text.

Crawl:
-c, --crawl               : Crawl website (Default output on /links.txt)
-d, --cdepth              : Set depth of crawl's travel (Default: 1)
-z, --exclusions "regexp" : Paths that you don't want to include
-t, --thread number       : How many pages to visit (Threads) at the same time
                            (Default: 16)
-p, --pause               : The length of time the crawler will pause
                            (Default: 0)
-f, --folder	          : The root directory which will contain the
                            generated files
-l, --log                 : Log file with visited URLs and their response code.
-x, --external            : Exclude external links while crawling a webpage
                            (Default: include all links)

GitHub: github.com/MikeMeliz/TorCrawl.py
License: GNU General Public License v3.0

"""

import argparse
import os
import sys

from modules.helpers.helper import get_tor_proxies

try:
    from gooey import Gooey, GooeyParser

    GOOEY_AVAILABLE = True
except ModuleNotFoundError:
    GOOEY_AVAILABLE = False

from modules.checker import check_ip, check_tor, extract_domain, folder, url_canon

# DarkSpider Modules
from modules.crawler import Crawler
from modules.extractor import extractor
from modules.visualization import Visualization

IGNORE_COMMAND = "--ignore-gooey"

# Remove IGNORE_COMMAND if present in arguments.
# We don't want to pass it to the argpaarse.
try:
    sys.argv.remove(IGNORE_COMMAND)
except ValueError:
    pass

# If GUI parameters are passed in arguments then handel Gooey unavailable error
if "-g" not in sys.argv and "--gui" not in sys.argv:
    if GOOEY_AVAILABLE:
        sys.argv.append(IGNORE_COMMAND)
elif not GOOEY_AVAILABLE:
    print("## Gooey is not available!")
    print("## Install Gooey with 'pip install Gooey' or remove '-g/--gui' argument")
    sys.exit(2)


def GooeyConditional(flag, **kwargs):
    """Conditional decorator if GUI backend is available or not"""

    def decorate(function):
        return Gooey(function, **kwargs) if flag else function

    return decorate


@GooeyConditional(GOOEY_AVAILABLE, program_name="DarkSpider")
def main():
    """Main method of DarkSpider application. Collects and parses arguments and
    instructs the rest of the application on how to run.

    :return: None
    """

    # Get arguments with GooeyParser if available else argparse.
    description = (
        "DarkSpider.py is a python script to crawl and extract "
        + "(regular or onion) webpages through TOR network."
    )
    if GOOEY_AVAILABLE:
        parser = GooeyParser(description=description)
    else:
        parser = argparse.ArgumentParser(description=description)

    # GUI
    gui_kwargs = {
        "action": "store_true",
        "help": "Open with GUI backend.",
    }
    if GOOEY_AVAILABLE:
        gui_kwargs["gooey_options"] = {"visible": False}

    parser.add_argument(
        "-g",
        "--gui",
        **gui_kwargs,
    )

    # General
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show more information about the progress",
    )
    parser.add_argument(
        "-s",
        "--visualize",
        action="store_true",
        help="Visualize the graphs and insights from the crawled data",
    )
    parser.add_argument(
        "-u", "--url", type=str, help="URL of webpage to crawl or extract"
    )
    parser.add_argument(
        "-w", "--without", action="store_true", help="Without the use of Relay TOR"
    )

    # Extract
    parser.add_argument(
        "-e",
        "--extract",
        action="store_true",
        help="Extract page's code to terminal or file.",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="Input file with URL(s) (seperated by line)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="",
        help="Output page(s) to file(s) (for one page)",
    )

    # Crawl
    parser.add_argument(
        "-c",
        "--crawl",
        action="store_true",
        help="Crawl website (Default output on /links.txt)",
    )
    parser.add_argument(
        "-d",
        "--cdepth",
        type=int,
        default=1,
        help="Set depth of crawl's travel. (Default: 1)",
    )
    parser.add_argument(
        "-p",
        "--cpause",
        type=float,
        default=0,
        help="The length of time the crawler will pause. (Default: 1 second)",
    )
    parser.add_argument(
        "-z",
        "--exclusion",
        type=str,
        help="Regex path that is ignored while crawling",
    )
    parser.add_argument(
        "-t",
        "--thread",
        type=int,
        default=16,
        help="How many pages to visit (Threads) at the same time (Default: 16)",
    )
    parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        help="A save log will let you see which URLs were visited and their "
        "response code",
    )
    parser.add_argument(
        "-f",
        "--folder",
        type=str,
        help="The root directory which will contain the generated files",
    )
    parser.add_argument(
        "-x",
        "--external",
        action="store_false",
        default=True,
        help="Exclude external links while crawling a webpage (Default: include all links)",
    )
    parser.add_argument(
        "-y",
        "--yara",
        type=int,
        default=0,
        help="Check for keywords and only scrape documents that contain a "
        "match. 0 search whole html object. 1 search only the text. (Default: 0)",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return

    args = parser.parse_args()

    if args.url is None and args.input is None:
        parser.error("either argument -u/--url or -i/--input is required to proceed.")

    if args.yara not in [0, 1]:
        parser.error("argument -y/--yara: expected argument 0 or 1.")

    if args.cdepth < 1:
        parser.error("argument -d/--cdepth: expected argument greater than 1.")

    if args.cpause < 0:
        parser.error("argument -p/--cpause: expected argument greater than 0.")

    if args.thread < 1:
        parser.error("argument -t/--thread: expected argument greater than 1.")

    # Connect to TOR
    if args.without is False:
        check_tor(args.verbose)

    proxies = get_tor_proxies(without=args.without)

    if args.verbose:
        check_ip(proxies=proxies)
        print(("## URL: " + args.url))

    website = ""
    out_path = ""

    # Canonicalization of web url and create path for output.
    if args.url:
        website = url_canon(args.url, args.verbose)
        if args.folder is not None:
            out_path = folder(args.folder, args.verbose)
        else:
            out_path = folder(extract_domain(website), args.verbose)

    if args.crawl:
        crawler = Crawler(
            website=website,
            proxies=proxies,
            c_params={"c_depth": args.cdepth, "c_pause": args.cpause},
            out_path=out_path,
            external=args.external,
            exclusion=args.exclusion,
            thread=args.thread,
            logging_={"log": args.log, "verbose": args.verbose},
        )
        json_data = crawler.crawl()
        print(f"## File created on {os.path.join(out_path, crawler.network_file)}")

        if args.visualize:
            obj = Visualization(
                os.path.join(out_path, crawler.network_file), out_path, args.verbose
            )
            obj.indegree_plot()
            obj.indegree_bar()
            obj.outdegree_plot()
            obj.outdegree_bar()
            obj.eigenvector_centrality_bar()
            obj.pagerank_bar()
            # obj.visualize()

        if args.extract:
            input_file = os.path.join(out_path, "links.txt")
            extractor(
                website,
                proxies,
                args.crawl,
                args.output,
                input_file,
                out_path,
                args.yara,
            )
    else:
        extractor(
            website,
            proxies,
            args.crawl,
            args.output,
            args.input or "",
            out_path,
            args.yara,
        )


# Stub to call main method.
if __name__ == "__main__":
    main()
