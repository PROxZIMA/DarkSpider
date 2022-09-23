import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.client import IncompleteRead, InvalidURL
from io import TextIOWrapper
from logging import Logger
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

import requests
import yara as _yara
from bs4 import BeautifulSoup

from modules.checker import folder
from modules.helper import get_requests_header

# Type hinting aliases
ExcInfo = Exception | bool
LogMsg = tuple[str]
LogLevel = int
Log = tuple[LogLevel, LogMsg, ExcInfo]
SingleRes = list[Log]
Results = list[SingleRes]


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
        yara: keyword search option.
        logger: A logger object to log the output.
    """

    __headers = get_requests_header()
    __yara_rules = _yara.compile("res/keywords.yar")
    __extract_folder = "extracted"

    def __init__(
        self,
        website: str,
        proxies: dict[str, str],
        crawl: bool,
        output_file: str,
        input_file: str,
        out_path: str,
        thread: int,
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
        self.yara = yara
        self.logger = logger

        self.__executor = ThreadPoolExecutor(max_workers=min(32, self.thread))
        self.__session = self.__get_tor_session()

    def extract(self) -> Results:
        """Extracts the contents of the input file/single URL into the outputs folder/file/terminal.

        Note:
            `Log` represents either Yara or an Exception output.

            If Yara search is True then content is written to file/terminal.

            If Yara search is False then content is ignored.

        A `Log` is a tuple of `LogLevel`, `LogMsg` and `ExcInfo` with the following format:
            (`LogLevel`, (`msg`, `*args`), `Exception()` or `False`)

        `SingleRes` of an url is a list of `Log` with the following format:
            [
                (10, ("%s :: %s match found!", "`http://example.com/file.html`", "Yara"), False),

                (10, ("IOError Error :: %s", "`http://example.com/file.html`"), IOError()),
            ]

        Returns:
            `Results` of an input which is a List of `SingleRes` with the following format:

            [[
                (10, ("%s :: %s match found!", "`http://example.com`", "Yara"), False),

                (10, ("File created :: %s", "example.com/extracted/example.com/_.html"), False),
            ], [
                (10, ("%s :: %s match found!", "`http://example.com/main.html`", "No yara"), False)
            ], [
                (10, ("%s :: %s match found!", "`http://example.com/file.html`", "Yara"), False),

                (10, ("IOError Error :: %s", "`http://example.com/file.html`"), IOError()),
            ]]
        """
        results: Results = []
        if len(self.input_file) > 0:
            if self.crawl or self.out_path:
                # Crawl(output folder) | INput file | EXtract
                results = self.__cinex(self.input_file, self.out_path, self.yara)
            else:
                # TERMinal | INput file | EXtract
                results = self.__terminex(self.input_file, self.yara)
        else:
            if len(self.output_file) > 0:
                # OUTput file | EXtract
                self.output_file = os.path.join(self.out_path, self.output_file)
                single_res = self.__outex(self.website, self.output_file, self.yara)
            else:
                # TERMinal | EXtract
                single_res = self.__termex(self.website, self.yara)

            for level, args, exception in single_res:
                self.logger.log(level, *args, exc_info=exception)

            results.append(single_res)
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

    def __cinex(self, input_file: str, out_path: str, yara: Optional[int]) -> Results:
        """Ingests the crawled links from the input_file,
        scrapes the contents of the resulting web pages and writes the contents to
        the into out_path/{url_address}.

        Args:
            input_file: Filename of the crawled Urls.
            out_path: Dir path for results.
            yara: Keyword search argument.

        Returns:
            List of `SingleRes` for each url in input.
        """
        self.logger.info("Cinex :: Extracting from %s to %s", input_file, out_path)
        return self.__inex(input_file=input_file, yara=yara, out_path=out_path)

    def __terminex(self, input_file: str, yara: Optional[int]) -> Results:
        """Input links from file and extract them into terminal.

        Args:
            input_file: Filename of the crawled Urls.
            yara: Keyword search argument.

        Returns:
            List of `SingleRes` for each url in input.
        """
        self.logger.info("Terminex :: Extracting from %s to terminal", input_file)
        return self.__inex(input_file=input_file, yara=yara)

    def __outex(self, website: str, output_file: str, yara: Optional[int]) -> SingleRes:
        """Scrapes the contents of the provided web address and outputs the
        contents to file.

        Args:
            website: Url of web address to scrape.
            output_file: Filename to write the contents to.
            yara: Keyword search argument.

        Returns:
            List of `Log` for given website.
        """
        self.logger.info("Outex :: Extracting %s to %s", website, output_file)
        return self.__ex(website=website, yara=yara, output_file=output_file)

    def __termex(self, website: str, yara: Optional[int]) -> SingleRes:
        """Scrapes provided web address and prints the results to the terminal.

        Args:
            website: Url of web address to scrape.
            yara: Keyword search argument.

        Returns:
            List of `Log` for given website.
        """
        self.logger.info("Termex :: Extracting %s to terminal", website)
        return self.__ex(website=website, yara=yara)

    def __inex(self, input_file: str, out_path: Optional[str] = None, yara: Optional[int] = None) -> Results:
        """Ingests the crawled links from the input_file,
        scrapes the contents of the resulting web pages and writes the contents
        into the terminal if out_path is None else out_path/{url_address}.

        Args:
            input_file: Filename of the crawled Urls.
            out_path: Dir path for results.
            yara: Keyword search argument.

        Returns:
            List of `SingleRes` [`Results`] for each url in input.
        """
        file = TextIOWrapper
        try:
            file = open(input_file, "r", encoding="UTF-8")
        except IOError as _:
            self.logger.exception("Read Error :: %s", input_file)
            return

        # Sumbit all the links to the thread pool
        futures = [
            self.__executor.submit(self.__generate_file, url=url, yara=yara, out_path=out_path)
            for url in file.read().splitlines()
        ]

        results: Results = []

        # Get the results from list of futures and append them to results
        for future in as_completed(futures):
            single_res = future.result()
            results.append(single_res)

            for level, args, exception in single_res:
                self.logger.log(level, *args, exc_info=exception)

        # Close the executor, don't wait for all threads to finish
        self.__executor.shutdown(wait=False)
        file.close()

        return results

    def __generate_file(self, url: str, out_path: Optional[str], yara: Optional[int]) -> SingleRes:
        """Generate output file from url and send it to extractor.

        Args:
            url: Url of web address to scrape.
            output_file: Filename to write the contents to.
            yara: Keyword search argument.

        Returns:
            List of `Log` [`SingleRes`] for given url.
        """
        output_file = None
        if out_path is not None:
            try:
                # http://a.com/b.ext?x=&y=$%z2 -> a.com/b.extxyz2_.html
                uri = urlparse(url)
                output_file = os.path.join(
                    out_path,
                    os.path.join(uri.netloc, *uri.path.split("/")) + re.sub(r"[^\w_.)( -]", "", uri.query) + "_.html",
                )
                # Create the directory if it doesn't exist
                folder(output_file, is_file=True)
            except Exception as err:
                return [
                    (
                        logging.DEBUG,
                        ("Output File Error :: %s", url),
                        err,
                    )
                ]

        return self.__ex(website=url, yara=yara, output_file=output_file)

    def __ex(self, website: str, output_file: str = None, yara: Optional[int] = None) -> SingleRes:
        """Scrapes the contents of the provided web address and outputs the
        contents to file or terminal.

        Args:
            website: Url of web address to scrape.
            output_file: Filename to write the contents to.
            yara: Keyword search argument.

        Returns:
            List of `Log` [`SingleRes`] for given website.
        """
        result = []
        try:
            content = self.__session.get(website, allow_redirects=True, timeout=10).text
            if yara is not None:
                full_match_keywords = self.__check_yara(raw=content, yara=yara)

                result.append(
                    (
                        logging.DEBUG,
                        (
                            "%s :: %s match found!",
                            website,
                            "Yara" if len(full_match_keywords) else "No yara",
                        ),
                        False,
                    )
                )

                # Don't write to file/terminal if no matches found.
                if len(full_match_keywords) == 0:
                    return result

            if output_file is not None:
                with open(output_file, "w", encoding="UTF-8") as file:
                    file.write(content)
                result.append((logging.DEBUG, ("File created :: %s", output_file), False))
            else:
                result.append((logging.INFO, ("%s :: %s", website, content), False))
        except HTTPError as err:
            result.append((logging.DEBUG, ("Request Error :: %s", website), err))
        except (InvalidURL, URLError) as _:
            result.append((logging.DEBUG, ("Invalid URL Error :: %s :: Skipping...", website), False))
        except IncompleteRead as _:
            result.append((logging.DEBUG, ("Incomplete Read Error :: %s", website), False))
        except IOError as err:
            result.append((logging.DEBUG, ("IOError Error :: %s", website), err))
        except Exception as err:
            result.append((logging.DEBUG, ("Error :: %s", website), err))

        return result

    def __check_yara(self, raw: str, yara: int = 0) -> dict[str, list]:
        """Validates Yara Rule to categorize the site and check for keywords.

        Args:
            yara: Keyword search argument.
            raw: HTTP Response body.

        Returns:
            Dictionary of yara rule matches.

            {"namespace":[match1,match2,...]}
        """
        if raw is None:
            return None

        if yara == 1:
            raw = self.__text(response=raw).lower()

        matches = self.__yara_rules.match(data=raw)

        return matches

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
