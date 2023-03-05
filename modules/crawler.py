import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import TextIOBase
from logging import Logger
from shutil import get_terminal_size
from typing import Dict, List, Set, Tuple, Union
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.models import Response

from modules.checker import url_canon
from modules.helper import DatabaseManager, get_requests_header


class Crawler:
    """Crawl input link upto depth (depth) with a pause of pause seconds using multiple threads.

    Attributes:
        website: Website to crawl.
        proxies: Dictionary mapping protocol or protocol and host to the URL of the proxy.
        depth: Depth of the crawl.
        pause: Pause after every depth iteration.
        out_path: Output path to store extracted links.
        external: True if external links are to be crawled else False.
        exclusion: Paths that you don't want to include.
        thread: Number pages to visit (Threads) at the same time.
        db: Neo4j :class:`DatabaseManager` object
        logger: A logger object to log the output.
    """

    network_file = "network_structure.json"
    __headers = get_requests_header()

    def __init__(
        self,
        website: str,
        proxies: Dict[str, str],
        depth: int,
        pause: float,
        out_path: str,
        external: bool,
        exclusion: str,
        thread: int,
        db: DatabaseManager,
        logger: Logger,
    ):
        self.website = website
        self.proxies = proxies
        self.depth = depth
        self.pause = pause
        self.out_path = out_path
        self.external = external
        self.exclusion = rf"{exclusion}" if exclusion else None
        self.thread = thread
        self.db = db
        self.logger = logger

        self.__executor = ThreadPoolExecutor(max_workers=min(32, self.thread))
        self.__files = {
            "Extlink": open(os.path.join(self.out_path, "extlinks.txt"), "w+", encoding="UTF-8"),
            "Telephone": open(os.path.join(self.out_path, "telephones.txt"), "w+", encoding="UTF-8"),
            "Mail": open(os.path.join(self.out_path, "mails.txt"), "w+", encoding="UTF-8"),
            "network_structure": os.path.join(self.out_path, self.network_file),
            "links": os.path.join(self.out_path, "links.txt"),
        }

    def __get_tor_session(self) -> requests.Session:
        """Get a new session with Tor proxies.

        Returns:
            Session object to make requests.
        """
        session = requests.Session()
        session.proxies = self.proxies
        session.headers.update(self.__headers)
        session.verify = False
        return session

    def excludes(self, link: str, parent_url: str) -> bool:
        """Excludes links that are not required.

        Args:
            link: Link to check for exclusion.

        Returns:
            True if link is to be excluded else False.
        """
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
            if self.external:
                return False
            self.__files["Extlink"].write(f"{parent_url}\n{link}\n")
            return True
        # Telephone Number
        if link.startswith("tel:"):
            self.__files["Telephone"].write(f"{parent_url}\n{link}\n")
            return True
        # Mails
        if link.startswith("mailto:"):
            self.__files["Mail"].write(f"{parent_url}\n{link}\n")
            return True
        # Type of files
        if re.search("^.*\\.(pdf|jpg|jpeg|png|gif|doc|js|css)$", link, re.IGNORECASE):
            return True

    def canonical(self, base: str, href: str) -> str:
        """Canonization of the link.

        Args:
            base: Base URL.
            href: Hyperlink present in the base URL page.

        Returns:
            parsed canonical url.
        """
        # Already formatted
        if href.startswith("http"):
            return href

        # For relative paths
        return urljoin(base, href)

    def __crawl_link(
        self, url: str, session: requests.Session
    ) -> Tuple[str, set[str], Union[int, Tuple[str, Exception]]]:
        """
        Extracts all the hyperlinks from the given url and returns a tuple of
        the url, set of hyperlinks and either status code or raised Exception.

        Args:
            url: URL to crawl.
            session: Session object to make requests.

        Returns:
            A tuple of the url, set of hyperlinks and either status code or raised Exception.

            (`https://example.com`, {`https://example.com/1`, `https://example.com/2`}, `200`)
            (`https://error.com`, {}, `Exception()`)
        """
        url_data = set()
        html_page = Response
        response_code = 0

        try:
            if url is not None:
                html_page = session.get(url, allow_redirects=True, timeout=10)
                response_code = html_page.status_code
        except Exception as err:
            return url, url_data, ("Request", err)

        try:
            soup = BeautifulSoup(html_page.text, features="html.parser")
        except Exception as err:
            return url, url_data, ("Soup Parse", err)

        # For each <a href=""> tag.
        for link in soup.findAll("a"):
            link = link.get("href")

            if self.excludes(link, url):
                continue

            ver_link = self.canonical(url, link)
            if ver_link is not None:
                url_data.add(url_canon(ver_link)[1])

        # For each <area href=""> tag.
        for link in soup.findAll("area"):
            link = link.get("href")

            if self.excludes(link, url):
                continue

            ver_link = self.canonical(url, link)
            if ver_link is not None:
                url_data.add(url_canon(ver_link)[1])

        return url, url_data, response_code

    def crawl(self) -> Dict[str, List[str]]:
        """Core of the crawler.

        Returns:
            Dictionary of crawled links.

            {
                "link1": [ "link2", "link3", "link4" ],
                "link2": [ "link5", "link6", "link4" ],
                "link3": [ "link7", "link2", "link9" ],
                "link4": [ "link1" ]
            }
        """
        ord_lst = set([self.website])
        old_level = [self.website]
        cur_level: Set[str] = set()

        self.logger.info(
            f"Crawler started from {self.website} with {self.depth} depth, "
            f"{self.pause} second{'s'[:int(self.pause)^1]} delay and using {self.thread} "
            f"Thread{'s'[:self.thread^1]}. Excluding '{self.exclusion}' links."
        )

        # Json dictionary
        json_data = {}
        # Depth
        for index in range(0, int(self.depth)):
            session = self.__get_tor_session()

            # Sumbit all the links to the thread pool
            futures = [
                self.__executor.submit(self.__crawl_link, url=url, session=session)
                for url in old_level
                if url not in json_data
            ]
            _flength = len(futures)
            _i = 0

            # Get the results from list of futures and update the json_data
            for future in as_completed(futures):
                _i += 1
                _percent = int((_i / _flength) * 100)
                _width = (_percent + 1) // 4
                print(" " * get_terminal_size().columns, end="\r", flush=True)

                url, url_data, response_code = future.result()
                if isinstance(response_code, int):
                    self.logger.debug("%s :: %d", url, response_code)
                else:
                    error, exception = response_code
                    self.logger.debug("%s Error :: %s", error, url, exc_info=exception)

                # Add url_data to crawled links.
                cur_level = cur_level.union(url_data)

                print(
                    f"[{'#'*_width}{' '*(25-_width)}]{_percent: >3}% -- Results: {len(cur_level)}",
                    end="\r",
                    flush=True,
                )

                # Adding to json data
                json_data[url] = list(url_data)

                self.db.create_linkage(url, list(url_data))

            print(" " * get_terminal_size().columns, end="\r", flush=True)
            # Get the next level withouth duplicates.
            clean_cur_level = cur_level.difference(ord_lst)
            # Merge both ord_lst and cur_level into ord_lst
            ord_lst = ord_lst.union(cur_level)
            # Replace old_level with clean_cur_level
            old_level = list(clean_cur_level)
            # Reset cur_level
            cur_level = set()
            self.logger.info("Step %d completed :: %d result(s)", index + 1, len(ord_lst))

            # Creating json
            with open(self.__files["network_structure"], "w", encoding="UTF-8") as lst_file:
                json.dump(json_data, lst_file, indent=2, sort_keys=False)

            with open(self.__files["links"], "w+", encoding="UTF-8") as file:
                for url in sorted(ord_lst):
                    file.write(f"{url}\n")

            session.close()
            # Pause time
            time.sleep(self.pause)

        # Close the executor, don't wait for all threads to finish
        self.__executor.shutdown(wait=False)

        # Close the output files and return the json_data
        for label, file in self.__files.items():
            if isinstance(file, TextIOBase):
                file.seek(0)
                data = file.read().splitlines()
                pairs = [data[i : i + 2] for i in range(0, len(data), 2)]
                self.db.create_labeled_link(label, pairs)
                file.close()

        return json_data
