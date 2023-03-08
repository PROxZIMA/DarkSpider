import re
import time
from collections import defaultdict
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
        self.extras = defaultdict(lambda: defaultdict(list))

        self.__executor = ThreadPoolExecutor(max_workers=min(32, self.thread))

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
            self.extras["Extlink"][parent_url].append(link)
            return True
        # Telephone Number
        if link.startswith("tel:"):
            self.extras["Telephone"][parent_url].append(link)
            return True
        # Mails
        if link.startswith("mailto:"):
            self.extras["Mail"][parent_url].append(link)
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

        # Depth
        for index in range(0, int(self.depth)):
            session = self.__get_tor_session()

            # Sumbit all the links to the thread pool
            futures = [self.__executor.submit(self.__crawl_link, url=url, session=session) for url in old_level]
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

            for label, data in self.extras.items():
                self.db.create_labeled_link(label, data)

            self.extras = defaultdict(lambda: defaultdict(list))

            session.close()
            # Pause time
            time.sleep(self.pause)

        # Close the executor, don't wait for all threads to finish
        self.__executor.shutdown(wait=False)

        return self.db.get_network_structure()
