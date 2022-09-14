#!/usr/bin/python
import json
import logging
import os
import re
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import TextIOBase
from threading import Lock
from typing import Union
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.models import Response

from modules.helpers.helper import get_requests_header, traceback_name

warnings.filterwarnings("ignore", category=UserWarning, module="bs4")
requests.urllib3.disable_warnings()


class Crawler:
    """Crawl input link upto depth (c_depth) with a pause of c_pause seconds using multiple threads.

    :param str website: Website to crawl.
    :param dict[str, str] proxies: Dictionary mapping protocol or protocol and host to the URL of the proxy.
    :param dict[str, any] c_params: Dictionary mapping
                                    {
                                        int c_depth: Depth of the crawl,
                                        float c_pause: Pause after every iteration
                                    }
    :param str out_path: Output path to store extracted links.
    :param bool external: True if external links are to be crawled else False.
    :param re str exclusion: Paths that you don't want to include.
    :param int thread: Number pages to visit (Threads) at the same time.
    :param dict[str, bool] logging: Dictionary mapping
                                    {
                                        bool logs: True if logs are to be written else False,
                                        bool verbose: True if crawl details are to be printed else False
                                    }
    """

    network_file = "network_structure.json"
    __headers = get_requests_header()

    def __init__(
        self,
        website: str,
        proxies: dict[str, str],
        c_params: dict[str, Union[int, float]],
        out_path: str,
        external: bool,
        exclusion: str,
        thread: int,
        logging_: dict[str, bool],
    ):
        self.website = website
        self.proxies = proxies
        self.c_depth = c_params["c_depth"]
        self.c_pause = c_params["c_pause"]
        self.out_path = out_path
        self.external = external
        self.exclusion = rf"{exclusion}" if exclusion else None
        self.thread = thread
        self.logs = logging_["log"]
        self.log_path = os.path.join(self.out_path, "log.txt")
        self.verbose = logging_["verbose"]
        self.__executor = ThreadPoolExecutor(max_workers=min(32, self.thread))
        self.__lock = Lock()
        self.__files = {
            "extlinks": open(
                os.path.join(self.out_path, "extlinks.txt"), "w+", encoding="UTF-8"
            ),
            "telephones": open(
                os.path.join(self.out_path, "telephones.txt"), "w+", encoding="UTF-8"
            ),
            "mails": open(
                os.path.join(self.out_path, "mails.txt"), "w+", encoding="UTF-8"
            ),
            "log_file": open(self.log_path, "w+", encoding="UTF-8"),
            "network_structure": os.path.join(self.out_path, self.network_file),
            "links": os.path.join(self.out_path, "links.txt"),
        }

    def __get_tor_session(self):
        session = requests.Session()
        session.proxies = self.proxies
        session.headers.update(self.__headers)
        session.verify = False
        return session

    def excludes(self, link):
        """Excludes links that are not required.

        :param link: String
        :return: Boolean
        """
        # BUG: For NoneType Exceptions, got to find a solution here
        if link is None:
            return True
        # Excludes links that matches the regex path.
        if self.exclusion and re.search(self.exclusion, link, re.IGNORECASE):
            return True
        # Links
        if "#" in link:
            return True
        # External links
        if link.startswith("http") and not link.startswith(self.website):
            if self.external is True:
                return False
            self.__files["extlinks"].write(str(link) + "\n")
            return True
        # Telephone Number
        if link.startswith("tel:"):
            self.__files["telephones"].write(str(link) + "\n")
            return True
        # Mails
        if link.startswith("mailto:"):
            self.__files["mails"].write(str(link) + "\n")
            return True
        # Type of files
        if re.search("^.*\\.(pdf|jpg|jpeg|png|gif|doc)$", link, re.IGNORECASE):
            return True

    def canonical(self, base, href):
        """Canonization of the link.

        :param link: String
        :return: String 'final_link': parsed canonical url.
        """
        # Already formatted
        if href.startswith("http"):
            return href

        # For relative paths
        return urljoin(base, href)

    def __crawl_link(self, item, session) -> tuple[str, list[str]]:
        # Store the crawled link of an item
        item_data = set()
        html_page = Response

        try:
            if item is not None:
                html_page = session.get(item, allow_redirects=True, timeout=10)
        except Exception as error:
            print(
                f"## Request Error :: {item} :: {traceback_name(error)}{' :: ' + error if self.logs else ''}"
            )
            # Keeps logs for every webpage visited.
            if self.logs:
                with self.__lock:
                    self.__files["log_file"].write(f"{str(item)}\n")
            return item, item_data

        try:
            soup = BeautifulSoup(html_page.text, features="html.parser")
        except Exception as error:
            print(
                f"## Soup Parse Error :: {item} :: {traceback_name(error)}{' :: ' + error if self.logs else ''}"
            )
            # Keeps logs for every webpage visited.
            if self.logs:
                with self.__lock:
                    self.__files["log_file"].write(f"{str(item)}\n")
            return item, item_data

        # For each <a href=""> tag.
        for link in soup.findAll("a"):
            link = link.get("href")

            if self.excludes(link):
                continue

            ver_link = self.canonical(item, link)
            if ver_link is not None:
                item_data.add(ver_link)

        # For each <area> tag.
        for link in soup.findAll("area"):
            link = link.get("href")

            if self.excludes(link):
                continue

            ver_link = self.canonical(item, link)
            if ver_link is not None:
                item_data.add(ver_link)

        # For each <script> tag
        for link in soup.findAll("script"):
            link = link.get("src")

            if self.excludes(link):
                continue

            ver_link = self.canonical(item, link)
            if ver_link is not None:
                item_data.add(ver_link)

        # For each <link> tag
        for link in soup.findAll("link"):
            link = link.get("href")

            if self.excludes(link):
                continue

            ver_link = self.canonical(item, link)
            if ver_link is not None:
                item_data.add(ver_link)

        return item, item_data

    def crawl(self):
        """Core of the crawler.
        :return: Dict (json_data) - Dictionary of crawled links.
        """
        ord_lst = set([self.website])
        old_level = [self.website]
        cur_level = set()

        if self.logs is True and os.access(self.log_path, os.W_OK) is ~os.path.exists(
            self.log_path
        ):
            print(f"## Unable to write to {self.log_path} - Exiting")
            sys.exit(2)

        print(
            f"## Crawler started from {self.website} with {self.c_depth} depth, "
            f"{self.c_pause} second{'s'[:int(self.c_pause)^1]} delay and using {self.thread} "
            f"Thread{'s'[:self.thread^1]}. Excluding '{self.exclusion}' links."
        )

        # Json dictionary
        json_data = {}
        # Depth
        for index in range(0, int(self.c_depth)):
            session = self.__get_tor_session()

            futures = [
                self.__executor.submit(self.__crawl_link, item=item, session=session)
                for item in old_level
                if item.rstrip("/") not in json_data
            ]

            for future in as_completed(futures):
                item, item_data = future.result()

                # Add item_data to crawled links.
                cur_level = cur_level.union(item_data)

                if self.verbose:
                    sys.stdout.write(f"-- Results: {len(cur_level)}\r")
                    sys.stdout.flush()

                # Adding to json data
                json_data[item.rstrip("/")] = list(item_data)

            # Get the next level withouth duplicates.
            clean_cur_level = cur_level.difference(ord_lst)
            # Merge both ord_lst and cur_level into ord_lst
            ord_lst = ord_lst.union(cur_level)
            # Replace old_level with clean_cur_level
            old_level = list(clean_cur_level)
            # Reset cur_level
            cur_level = set()
            print(f"## Step {index + 1} completed \n\t with: {len(ord_lst)} result(s)")

            # Creating json
            with open(
                self.__files["network_structure"], "w", encoding="UTF-8"
            ) as lst_file:
                json.dump(json_data, lst_file, indent=2, sort_keys=False)

            with open(self.__files["links"], "w+", encoding="UTF-8") as file:
                for item in sorted(ord_lst):
                    file.write(f"{item}\n")

            # Pause time
            time.sleep(self.c_pause)

        for file in self.__files.values():
            if isinstance(file, TextIOBase):
                file.close()

        return json_data
