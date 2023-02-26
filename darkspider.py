#!/usr/bin/env python3

"""

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


DarkSpider is a multithreaded crawler and extractor for regular
or onion webpages through the TOR network, written in Python.

usage: python darkspider.py [options]

python darkspider.py --help
python darkspider.py -u l0r3m1p5umD0lorS1t4m3t.onion
python darkspider.py -v -w -u http://www.github.com -o github.htm
python darkspider.py -v -u l0r3m1p5umD0lorS1t4m3t.onion -c -d 2 -p 5
python darkspider.py -v -w -u http://www.github.com -c -d 2 -p 5 -e -f GitHub

GitHub: github.com/PROxZIMA/DarkSpider.py
License: GNU General Public License v3.0
"""

import argparse
import logging
import os
import sys
import warnings

import requests
from dotenv import load_dotenv

# DarkSpider Modules
from modules import Crawler
from modules.checker import check_ip, check_tor, extract_domain, folder, url_canon
from modules.extractor import Extractor
from modules.helper import HEADER, Colors, DatabaseManager, get_tor_proxies, gradient_print, setup_custom_logger
from modules.visualization import Visualization

warnings.filterwarnings("ignore", category=UserWarning, module=r"bs4|gooey")
logging.getLogger("urllib3").setLevel(logging.ERROR)
requests.urllib3.disable_warnings()


def main(gooey_available: bool, base_parser: argparse.ArgumentParser):
    """Main method of DarkSpider application. Collects and parses arguments and
    instructs the rest of the application on how to run.
    """

    # Get arguments with GooeyParser if available else argparse.
    description = "DarkSpider is a multithreaded crawler and extractor for regular or onion webpages through the TOR network, written in Python."
    parser: argparse.ArgumentParser = base_parser(description=description, add_help=False)

    # Required
    required_group = parser.add_argument_group("Required Options", "Either argument -u/--url or -i/--input is required")
    required_group.add_argument("-u", "--url", metavar="Seed URL", type=str, help="URL of webpage to crawl or extract")
    required_group.add_argument(
        "-i",
        "--input",
        metavar="Input file",
        type=str,
        help="Input file with URL(s) (seperated by line)",
    )

    # Extract
    extract_group = parser.add_argument_group("Extract Options", "Arguments for the Extractor module")
    extract_group.add_argument(
        "-e",
        "--extract",
        dest="Extract",
        action="store_true",
        help="Extract page's code to terminal or file. (Default: Terminal)",
    )
    extract_group.add_argument(
        "-o",
        "--output",
        metavar="Output",
        type=str,
        default="",
        help="Output page(s) to file(s) (for one page)",
    )
    extract_group.add_argument(
        "-y",
        "--yara",
        metavar="Yara",
        type=int,
        default=None,
        help="Check for keywords and only scrape documents that contain a "
        "match. 0 search whole html object. 1 search only the text. (Default: None)",
    )

    # Crawler
    crawler_group = parser.add_argument_group("Crawler Options", "Arguments for the Crawler module")
    crawler_group.add_argument(
        "-c",
        "--crawl",
        dest="Crawl",
        action="store_true",
        help="Crawl website (Default output on /links.txt)",
    )
    crawler_group.add_argument(
        "-d",
        "--depth",
        metavar="Depth",
        type=int,
        default=1,
        help="Set depth of crawl's travel. (Default: 1)",
    )
    crawler_group.add_argument(
        "-p",
        "--pause",
        metavar="Pause",
        type=float,
        default=1,
        help="The length of time the crawler will pause. (Default: 1 second)",
    )
    crawler_group.add_argument(
        "-z",
        "--exclusion",
        metavar="Exclusion regex",
        type=str,
        help="Regex path that is ignored while crawling (Default: None)",
    )
    crawler_group.add_argument(
        "-x",
        "--external",
        dest="External links",
        action="store_false",
        default=True,
        help="Exclude external links while crawling a webpage (Default: include all links)",
    )

    # Visualize
    visualize_group = parser.add_argument_group("Visualize Options", "Arguments for the Visualize module")
    visualize_group.add_argument(
        "-s",
        "--visualize",
        dest="Visualize",
        action="store_true",
        help="Visualize the graphs and insights from the crawled data",
    )

    # General
    general_group = parser.add_argument_group("General Options", "Configuration options for the crawler")
    gui_kwargs = {
        "action": "store_true",
        "help": "Open with GUI backend.",
    }
    if gooey_available:
        gui_kwargs["gooey_options"] = {"visible": False}

    general_group.add_argument(
        "-g",
        "--gui",
        dest="GUI",
        **gui_kwargs,
    )
    general_group.add_argument(
        "-h",
        "--help",
        dest="Help",
        action="help",
        help="Show this help message and exit",
    )
    general_group.add_argument(
        "-v",
        "--verbose",
        dest="Verbose",
        action="store_true",
        help="Show more information about the progress",
    )
    general_group.add_argument(
        "-w",
        "--without",
        dest="Without TOR",
        action="store_true",
        help="Without the use of Relay TOR",
    )
    general_group.add_argument(
        "-n",
        "--port",
        metavar="Port number",
        type=int,
        default=9050,
        help="Port number of TOR Proxy (default: 9050)",
    )
    general_group.add_argument(
        "-f",
        "--folder",
        metavar="Folder",
        type=str,
        help="The root directory which will contain the generated files",
    )
    general_group.add_argument(
        "-t",
        "--thread",
        metavar="Threads",
        type=int,
        default=16,
        help="How many pages to visit (Threads) at the same time (Default: 16)",
    )
    general_group.add_argument(
        "-l",
        "--log",
        dest="Log files",
        action="store_false",
        default=True,
        help="A log will let you see which URLs were visited and their response code (Default: True)",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return

    args = parser.parse_args()

    if args.url is None and args.input is None:
        parser.error("either argument -u/--url or -i/--input is required to proceed.")

    if args.port < 1 or 65535 < args.port:
        parser.error("argument -n/--port: expected argument in between 1 to 65535.")

    if args.yara and args.yara not in [0, 1]:
        parser.error("argument -y/--yara: expected argument 0 or 1.")

    if args.depth < 1:
        parser.error("argument -d/--depth: expected argument greater than 1.")

    if args.pause < 0:
        parser.error("argument -p/--pause: expected argument greater than 0.")

    if args.thread < 1:
        parser.error("argument -t/--thread: expected argument greater than 1.")

    proxies = None
    out_path = ""
    canon, website = False, ""

    # Canonicalization of web url and create path for output.
    if args.url:
        canon, website = url_canon(args.url)
        out_path = extract_domain(website)
    elif args.folder:
        out_path = args.folder

    out_path = folder(os.path.join("output", out_path))

    # Logger setup
    crawlog = setup_custom_logger(
        name="crawlog",
        filename=os.path.join(out_path, "crawl.log"),
        verbose_=args.Verbose,
        filelog=getattr(args, "Log files"),
        argv=sys.argv,
    )

    # Connect to TOR
    if not getattr(args, "Without TOR"):
        check_tor(logger=crawlog)
        proxies = get_tor_proxies(port=args.port)

    if args.Verbose:
        check_ip(proxies=proxies, url=args.url, logger=crawlog, without_tor=getattr(args, "Without TOR"))

    if canon:
        crawlog.debug("URL fixed :: %s", website)
    if out_path:
        crawlog.debug("Folder created :: %s", out_path)

    load_dotenv()
    db = DatabaseManager(
        out_path, os.environ.get("NEO4J_SERVER"), os.environ.get("NEO4J_USER"), os.environ.get("NEO4J_PASSWORD")
    )
    if args.Crawl and website:
        crawler = Crawler(
            website=website,
            proxies=proxies,
            depth=args.depth,
            pause=args.pause,
            out_path=out_path,
            external=getattr(args, "External links"),
            exclusion=args.exclusion,
            thread=args.thread,
            db=db,
            logger=crawlog,
        )
        json_data = crawler.crawl()
        crawlog.info(
            "Network Structure created :: %s",
            os.path.join(out_path, crawler.network_file),
        )

        if args.Visualize:
            obj = Visualization(
                json_file=os.path.join(out_path, crawler.network_file),
                out_path=out_path,
                logger=crawlog,
            )
            obj.indegree_plot()
            obj.indegree_bar()
            obj.outdegree_plot()
            obj.outdegree_bar()
            obj.eigenvector_centrality_bar()
            obj.pagerank_bar()
            # obj.visualize()

        if args.Extract:
            input_file = os.path.join(out_path, "links.txt")
            extractor = Extractor(
                website=website,
                proxies=proxies,
                crawl=args.Crawl,
                output_file=args.output,
                input_file=input_file,
                out_path=out_path,
                thread=args.thread,
                yara=args.yara,
                logger=crawlog,
            )
            extract = extractor.extract()
    elif args.input or website:
        extractor = Extractor(
            website=website,
            proxies=proxies,
            crawl=args.Crawl,
            output_file=args.output,
            input_file=args.input or "",
            out_path=out_path,
            thread=args.thread,
            yara=args.yara,
            logger=crawlog,
        )
        extract = extractor.extract()


GOOEY_AVAILABLE = False
PARSER = argparse.ArgumentParser

if not sys.stdout.isatty() or "-g" in sys.argv or "--gui" in sys.argv:
    # If we are not attached to a terminal or CLI includes -g/--gui, use Gooey
    try:
        from gooey import Gooey, GooeyParser

        GOOEY_AVAILABLE = True
        PARSER = GooeyParser
        gradient_print(HEADER, start_color=(252, 70, 107), end_color=(63, 94, 251), disable=True)

        main = Gooey(
            program_name="DarkSpider",
            image_dir="assets",
            monospace_display=True,
            tabbed_groups=False,
            menu=[
                {
                    "name": "File",
                    "items": [
                        {
                            "type": "AboutDialog",
                            "menuTitle": "About",
                            "name": "DarkSpider",
                            "description": "Multithreaded Crawler and Extractor for Dark Web",
                            "version": "2.1.0",
                            "copyright": "2023",
                            "website": "https://proxzima.dev/DarkSpider/",
                            "developer": "https://github.com/PROxZIMA, https://github.com/knightster0804, https://github.com/r0nl, https://github.com/ytatiya3",
                            "license": "GNU General Public License v3.0",
                        },
                        {
                            "type": "MessageDialog",
                            "menuTitle": "Information",
                            "caption": "Basic Idea about crawlers",
                            "message": "Crawling is not illegal, but violating copyright is. It's always best to double check a website's T&C before crawling them. Some websites set up what's called robots.txt to tell crawlers not to visit those pages. This crawler will allow you to go around this, but we always recommend respecting robots.txt.\n\nExtracting and crawling through TOR network take some time. That's normal behaviour; you can find more information here (https://support.torproject.org/relay-operators/why-is-my-relay-slow/).",
                        },
                    ],
                },
                {
                    "name": "Help",
                    "items": [{"type": "Link", "menuTitle": "Documentation", "url": "https://proxzima.dev/DarkSpider"}],
                },
            ],
        )(main)
    except ModuleNotFoundError:
        print(f"[ {Colors.RED}ERROR{Colors.RESET} ] Gooey is not available!")
        print(
            f"[ {Colors.BLUE}INFO {Colors.RESET} ] Install Gooey with 'pip install Gooey' or remove '-g/--gui' argument"
        )
        sys.exit(2)
else:
    os.system("cls" if os.name == "nt" else "clear")

    gradient_print(
        HEADER,
        start_color=(252, 70, 107),
        end_color=(63, 94, 251),
    )


# Stub to call main method.
if __name__ == "__main__":
    main(gooey_available=GOOEY_AVAILABLE, base_parser=PARSER)
