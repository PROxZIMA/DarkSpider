import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.client import IncompleteRead, InvalidURL
from io import TextIOWrapper
from logging import Logger
from shutil import get_terminal_size
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError

import requests
import yara as _yara
from bs4 import BeautifulSoup
from neo4j.time import DateTime

from modules.checker import folder
from modules.helper import DatabaseManager, Result, get_requests_header


class Extractor:
    """Extractor - scrapes the resulting website or discovered links.

    Attributes:
        website: URL of website to scrape.
        proxies: Dictionary mapping protocol or protocol and host to the URL of the proxy.
        crawl: Cinex trigger. If used, iteratively scrape the urls from input_file.
        output_file: Filename of resulting output from scrape.
        input_file: Filename of crawled/discovered URLs.
        out_path: Dir path for output files.
        thread: Number pages to extract (Threads) at the same time.
        db: Neo4j :class:`DatabaseManager` object
        yara: keyword search option.
        logger: A logger object to log the output.
    """

    __headers = get_requests_header()
    __yara_rules = _yara.compile("res/keywords.yar")
    __extract_folder = "extracted"

    def __init__(
        self,
        website: str,
        proxies: Dict[str, str],
        crawl: bool,
        output_file: str,
        input_file: str,
        out_path: str,
        thread: int,
        db: DatabaseManager,
        yara: Optional[int],
        logger: Logger,
    ):
        self.website = website
        self.proxies = proxies
        self.crawl = crawl
        self.output_file = output_file
        self.input_file = input_file

        self.out_path = out_path
        if self.crawl:
            self.out_path = folder(os.path.join(out_path, self.__extract_folder))

        self.thread = thread
        self.db = db
        self.yara = yara
        self.logger = logger

        self.__executor = ThreadPoolExecutor(max_workers=min(32, self.thread))
        self.__session = self.__get_tor_session()

    def extract(self) -> List[Result]:
        """Extracts the contents of the input file/single URL into the outputs folder/file/terminal.

        Returns:
            List[Result] with any of the following formats:

            Result(
                yara: (10, ("%s :: %s match found!", "`http://example.com`", "Yara"), False),
                extract: (10, ("File created :: %s", "output/input_file_name.html"), False),
                error: None
            )

            Result(
                yara: None,
                extract: (20, ("%s :: %s", "http://example.com", "<html>...</html>"), False),
                error: None
            )

            Result(
                yara: (10, ("%s :: %s match found!", "`http://example.com/file.html`", "No yara"), False),
                extract: None
                error: (10, ("IOError Error :: %s", "`http://example.com/file.html`"), IOError())
            )
        """
        results: List[Result] = []
        if len(self.input_file) > 0:
            if self.crawl:
                # Crawl | INput db | EXtract
                results = self.__cinex(self.yara, self.db)
            else:
                # TERMinal | INput file | EXtract
                results = self.__terminex(self.input_file, self.yara)
        else:
            if len(self.output_file) > 0:
                # OUTput file | EXtract
                self.output_file = os.path.join(self.out_path, self.output_file)
                result = self.__outex(self.website, self.output_file, self.yara)
            else:
                # TERMinal | EXtract
                result = self.__termex(self.website, self.yara)

            for log_type in (result.yara, result.extract, result.error):
                if log_type is not None:
                    level, args, exception = log_type
                    self.logger.log(level, *args, exc_info=exception)

            results.append(result)
        return results

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

    # Depricate input file extraction to an output folder after crawling
    # Use database to get all nodes, extract them and save ouput to the database.
    def __cinex(self, yara: Optional[int], db: DatabaseManager) -> List[Result]:
        """Ingests the crawled links from the database,
        scrapes the contents of the resulting web pages and writes the contents to
        the Database.

        Args:
            yara: Keyword search argument.
            db: Neo4j :class:`DatabaseManager` object

        Returns:
            List of :class:`Result` for each url in input.
        """
        self.logger.info("Cinex :: Extracting contents of all nodes to Database")
        results = self.__inex(yara=yara, db=db)
        for i, result in enumerate(results):
            results[i] = result.dict()
        self.db.add_web_content(results)
        return results

    def __terminex(self, input_file: str, yara: Optional[int]) -> List[Result]:
        """Input links from file and extract them into terminal.

        Args:
            input_file: Filename of the crawled Urls.
            yara: Keyword search argument.

        Returns:
            List of :class:`Result` for each url in input.
        """
        self.logger.info("Terminex :: Extracting from %s to terminal", input_file)
        return self.__inex(input_file=input_file, yara=yara)

    def __outex(self, website: str, output_file: str, yara: Optional[int]) -> Result:
        """Scrapes the contents of the provided web address and outputs the
        contents to file.

        Args:
            website: Url of web address to scrape.
            output_file: Filename to write the contents to.
            yara: Keyword search argument.

        Returns:
            :class:`Result` for given website.
        """
        self.logger.info("Outex :: Extracting %s to %s", website, output_file)
        return self.__ex(website=website, yara=yara, output_file=output_file)

    def __termex(self, website: str, yara: Optional[int]) -> Result:
        """Scrapes provided web address and prints the results to the terminal.

        Args:
            website: Url of web address to scrape.
            yara: Keyword search argument.

        Returns:
            :class:`Result` for given website.
        """
        self.logger.info("Termex :: Extracting %s to terminal", website)
        return self.__ex(website=website, yara=yara)

    def __inex(
        self,
        input_file: Optional[str] = None,
        yara: Optional[int] = None,
        db: Optional[DatabaseManager] = None,
    ) -> List[Result]:
        """Ingests the crawled links from the input_file,
        scrapes the contents of the resulting web pages and writes the contents
        into the terminal if db is None else to database.

        Args:
            input_file: Filename of the crawled Urls.
            yara: Keyword search argument.
            db: Neo4j :class:`DatabaseManager` object

        Returns:
            List of :class:`Result` for each url in input.
        """
        results: List[Result] = []
        urls: List[str] = []

        if db is not None:
            urls: List[str] = db.get_all_urls()
        elif input_file is not None:
            file = TextIOWrapper
            try:
                file = open(input_file, "r", encoding="UTF-8")
                urls: List[str] = file.read().splitlines()
                file.close()
            except IOError as _:
                self.logger.exception("Read Error :: %s", input_file)
                return results

        # Sumbit all the links to the thread pool
        futures = [self.__executor.submit(self.__ex, website=url, yara=yara) for url in urls]
        _flength = len(futures)
        _i = 0

        # Get the results from list of futures and append them to results
        for future in as_completed(futures):
            _i += 1
            _percent = int((_i / _flength) * 100)
            _width = (_percent + 1) // 4
            _stmt = f"[{'#'*_width}{' '*(25-_width)}]{_percent: >3}%"
            print(
                _stmt + " " * max(get_terminal_size().columns - len(_stmt), 0),
                end="\r",
                flush=True,
            )

            result = future.result()
            results.append(result)

            # db exists so don't log to terminal
            if db is not None:
                continue

            for log_type in (result.yara, result.extract, result.error):
                if log_type is not None:
                    level, args, exception = log_type
                    self.logger.log(level, *args, exc_info=exception)

        print(" " * get_terminal_size().columns, end="\r", flush=True)
        # Close the executor, don't wait for all threads to finish
        self.__executor.shutdown(wait=False)

        return results

    def __ex(self, website: str, output_file: Optional[str] = None, yara: Optional[int] = None) -> Result:
        """Scrapes the contents of the provided web address and outputs the
        contents to file or terminal.

        Args:
            website: Url of web address to scrape.
            output_file: Filename to write the contents to.
            yara: Keyword search argument.

        Returns:
            List of `Log` [`Result`] for given website.
        """
        result = Result(url=website, scrape_datetime=DateTime.now())
        try:
            content = self.__session.get(website, allow_redirects=True, timeout=10).text
            raw = self.__text(response=content).lower()
            result.scrape_html = content
            result.scrape_data = raw

            if yara is not None:

                if yara == 1:
                    content = raw

                full_match_keywords = self.__check_yara(data=content)
                result.yara_code = 1 if full_match_keywords["matches"] else 0

                result.yara = (
                    logging.DEBUG,
                    (
                        "%s :: %s match found!",
                        website,
                        "Yara" if full_match_keywords["matches"] else "No yara",
                    ),
                    False,
                )

                # Don't write to file/terminal if no matches found.
                if len(full_match_keywords) == 0:
                    return result

            if output_file is not None:
                with open(output_file, "w", encoding="UTF-8") as file:
                    file.write(content)
                result.extract = (logging.DEBUG, ("File created for %s :: %s", website, output_file), False)
            else:
                result.extract = (logging.INFO, ("%s :: %s", website, content), False)
        except HTTPError as err:
            result.error = (logging.DEBUG, ("Request Error :: %s", website), err)
        except (InvalidURL, URLError) as _:
            result.error = (logging.DEBUG, ("Invalid URL Error :: %s :: Skipping...", website), False)
        except IncompleteRead as _:
            result.error = (logging.DEBUG, ("Incomplete Read Error :: %s", website), False)
        except IOError as err:
            result.error = (logging.DEBUG, ("IOError Error :: %s", website), err)
        except Exception as err:
            result.error = (logging.DEBUG, ("Error :: %s", website), err)

        return result

    def __check_yara(self, data: str) -> Dict[str, list]:
        """Validates Yara Rule to categorize the site and check for keywords.

        Args:
            data: HTTP Response body.

        Returns:
            Dictionary of yara rule matches.

            {"namespace":[match1,match2,...]}
        """
        if data is None:
            return None

        rule_data = []

        def callback(data):
            rule_data.append(data)
            return 0  # yara.CALLBACK_CONTINUE

        _matches = self.__yara_rules.match(data=data, callback=callback)

        return rule_data[0]

    def __text(self, response: str) -> str:
        """Removes all the garbage from the HTML and takes only text elements
        from the page.

        Args:
            response: HTTP Response.

        Returns:
        Text only stripped response.
        """
        soup = BeautifulSoup(response, features="lxml")
        for s in soup(["script", "style"]):
            s.decompose()

        return " ".join(soup.stripped_strings)
