#!/usr/bin/python
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.client import IncompleteRead, InvalidURL
from io import TextIOWrapper
from logging import Logger
from typing import Union
from unittest import result
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

import requests
import yara as _yara
from bs4 import BeautifulSoup

from modules.checker import folder
from modules.helpers.helper import get_requests_header


class Extractor:
    """Extractor - scrapes the resulting website or discovered links.

    :param str website: URL of website to scrape.
    :param dict[str, str] proxies: Dictionary mapping protocol or protocol and host to the URL of the proxy.
    :param bool crawl: Cinex trigger. If used iteratively scrape the urls from input_file.
    :param str output_file: Filename of resulting output from scrape.
    :param str input_file: Filename of crawled/discovered URLs
    :param str out_path: Dir path for output files.
    :param int thread: Number pages to extract (Threads) at the same time.
    :param int yara: keyword search option.
    :param Logger logger: A logger object to log the output.
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
        yara: int,
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
        self.__executor = ThreadPoolExecutor(max_workers=min(32, self.thread))
        self.yara = yara
        self.logger = logger
        self.__session = self.__get_tor_session()

    def extract(self):
        """Extracts the contents of the input file/single URL into the outputs folder/file/terminal."""
        # TODO: Return output to torcrawl.py
        if len(self.input_file) > 0:
            if self.crawl or self.out_path:
                self.__cinex(self.input_file, self.yara, self.out_path)
            else:
                self.__terminex(self.input_file, self.yara)
        else:
            results = []
            if len(self.output_file) > 0:
                self.output_file = os.path.join(self.out_path, self.output_file)
                results = self.__outex(self.website, self.yara, self.output_file)
            else:
                results = self.__termex(self.website, self.yara)

            for level, args, exception in results:
                self.logger.log(level, *args, exc_info=exception)

    def __get_tor_session(self):
        session = requests.Session()
        session.proxies = self.proxies
        session.headers.update(self.__headers)
        session.verify = False
        return session

    def __text(self, response=None):
        """Removes all the garbage from the HTML and takes only text elements
        from the page.

        :param response: HTTP Response.
        :return: String: Text only stripped response.
        """
        soup = BeautifulSoup(response, features="lxml")
        for s in soup(["script", "style"]):
            s.decompose()

        return " ".join(soup.stripped_strings)

    def __check_yara(self, raw=None, yara=0):
        """Validates Yara Rule to categorize the site and check for keywords.

        :param yara:  Integer: Keyword search argument.
        :param raw:   HTTP Response body.
        :return matches: List of yara rule matches.
        """
        if raw is None:
            return None

        if yara == 1:
            raw = self.__text(response=raw).lower()

        matches = self.__yara_rules.match(data=raw)

        return matches

    def __generate_file_extract(self, url, yara, out_path) -> list[tuple[int, tuple[str], Union[Exception, bool]]]:
        output_file = None
        if out_path is not None:
            try:
                uri = urlparse(url)
                output_file = os.path.join(
                    out_path,
                    os.path.join(uri.netloc, *uri.path.split("/")) + re.sub(r"[^\w_.)( -]", "", uri.query) + "_.html",
                )
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

    def __inex(self, input_file, yara, out_path=None):
        """Ingests the crawled links from the input_file,
        scrapes the contents of the resulting web pages and writes the contents
        into the terminal if out_path is None else out_path/{url_address}.

        :param input_file: String: Filename of the crawled Urls.
        :param out_path: String|None : Pathname of results.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        file = TextIOWrapper
        try:
            file = open(input_file, "r", encoding="UTF-8")
        except IOError as _:
            self.logger.exception("Read Error :: %s", input_file)
            return

        futures = [
            self.__executor.submit(self.__generate_file_extract, url=url, yara=yara, out_path=out_path)
            for url in file.read().splitlines()
        ]

        for future in as_completed(futures):
            for level, args, exception in future.result():
                self.logger.log(level, *args, exc_info=exception)

        file.close()

    def __cinex(self, input_file, yara, out_path):
        """Ingests the crawled links from the input_file,
        scrapes the contents of the resulting web pages and writes the contents to
        the into out_path/{url_address}.

        :param input_file: String: Filename of the crawled Urls.
        :param yara: Integer: Keyword search argument.
        :param out_path: String: Pathname of results.
        :return: None
        """
        self.logger.info("Cinex :: Extracting from %s to %s", input_file, out_path)
        self.__inex(input_file=input_file, yara=yara, out_path=out_path)

    def __terminex(self, input_file, yara):
        """Input links from file and extract them into terminal.

        :param input_file: String: File name of links file.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        self.logger.info("Terminex :: Extracting from %s to terminal", input_file)
        self.__inex(input_file=input_file, yara=yara)

    def __ex(self, website, yara, output_file=None) -> list[tuple[int, tuple[str], Union[Exception, bool]]]:
        """Scrapes the contents of the provided web address and outputs the
        contents to file or terminal.

        :param type: String: Either "Outex" or "Termex".
        :param website: String: Url of web address to scrape.
        :param yara: Integer: Keyword search argument.
        :param output_file: String|None: Filename of the results.
        :return: None
        """
        result = []
        try:
            content = self.__session.get(website, allow_redirects=True, timeout=10).text

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

            # if len(full_match_keywords) == 0:
            #     # Don't write to file if no matches found.
            #     if output_file is not None:
            #         return result

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

    def __outex(self, website, yara, output_file):
        """Scrapes the contents of the provided web address and outputs the
        contents to file.

        :param website: String: Url of web address to scrape.
        :param yara: Integer: Keyword search argument.
        :param output_file: String: Filename of the results.
        :return: None
        """
        self.logger.info("Outex :: Extracting %s to %s", website, output_file)
        return self.__ex(website=website, yara=yara, output_file=output_file)

    def __termex(self, website, yara):
        """Scrapes provided web address and prints the results to the terminal.

        :param website: String: URL of website to scrape.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        self.logger.info("Termex :: Extracting %s to terminal", website)
        return self.__ex(website=website, yara=yara)
