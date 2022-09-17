#!/usr/bin/python
import os
from http.client import IncompleteRead, InvalidURL
from io import TextIOWrapper
from logging import Logger
from urllib.error import HTTPError, URLError

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

        self.yara = yara
        self.logger = logger
        self.__session = self.__get_tor_session()

    def extract(self):
        """Extracts the contents of the input file/single URL into the outputs folder/file/terminal."""
        # TODO: Return output to torcrawl.py
        if len(self.input_file) > 0:
            if self.crawl or self.out_path:
                self.__cinex(self.input_file, self.out_path, self.yara)
            else:
                self.__intermex(self.input_file, self.yara)
        else:
            if len(self.output_file) > 0:
                self.__outex(self.website, self.output_file, self.out_path, self.yara)
            else:
                self.__termex(self.website, self.yara)

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

    def __check_yara(self, type_, raw=None, yara=0):
        """Validates Yara Rule to categorize the site and check for keywords.

        :param type_: String: "Cinex" or "Intermex" or "Outex" or "Termex".
        :param yara:  Integer: Keyword search argument.
        :param raw:   HTTP Response body.
        :return matches: List of yara rule matches.
        """
        if raw is None:
            return None

        if yara == 1:
            raw = self.__text(response=raw).lower()

        matches = self.__yara_rules.match(data=raw)

        # if len(matches) != 0:
        #     self.logger.debug(f"{type_} :: Yara match found!")

        return matches

    def __inex(self, type_, input_file, yara, out_path=None):
        """Ingests the crawled links from the input_file,
        scrapes the contents of the resulting web pages and writes the contents
        into the terminal if out_path is None else out_path/{url_address}.

        :param type_: String: Either "Cinex" or "Intermex".
        :param input_file: String: Filename of the crawled Urls.
        :param out_path: String|None : Pathname of results.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        file = TextIOWrapper
        try:
            file = open(input_file, "r", encoding="UTF-8")
        except IOError as _:
            self.logger.exception(f"{type_} Read Error :: {input_file}")
            return

        for line in file.read().splitlines():

            # Generate the name for every file.
            if out_path is not None:
                try:
                    page_name = line.rsplit("/", 1)
                    cl_page_name = str(page_name[1])
                    if len(cl_page_name) == 0:
                        output_file = "index.html"
                    else:
                        output_file = cl_page_name
                except Exception as _:
                    self.logger.debug(
                        f"{type_} Output File Error :: {line}", exc_info=True
                    )
                    continue

            # Extract page to file.
            try:
                content = self.__session.get(
                    line, allow_redirects=True, timeout=10
                ).text

                full_match_keywords = self.__check_yara(
                    type_=type_, raw=content, yara=yara
                )

                self.logger.debug(
                    f"{type_} :: {line} :: {'Yara' if len(full_match_keywords) else 'No yara'} match found!"
                )

                # if len(full_match_keywords) == 0:
                #     self.logger.debug(f"{type_} :: No yara matches found.")
                #     Don't write to file if no matches found.
                #     if out_path is not None:
                #         continue

                if out_path is not None:
                    with open(
                        os.path.join(out_path, output_file), "w+", encoding="UTF-8"
                    ) as results:
                        results.write(content)
                    self.logger.debug(
                        f"{type_} File created :: {os.path.join(out_path, output_file)}"
                    )
                else:
                    self.logger.info(f"{line} :: {content}")
            except HTTPError as _:
                self.logger.debug(f"{type_} Request Error :: {line}", exc_info=True)
                continue
            except (InvalidURL, URLError) as _:
                self.logger.debug(f"{type_} Invalid URL Error :: {line} :: Skipping...")
                continue
            except IncompleteRead as _:
                self.logger.debug(f"{type_} Incomplete Read Error :: {line}")
                continue
            except IOError as _:
                self.logger.debug(f"{type_} IOError Error :: {line}", exc_info=True)
            except Exception as _:
                self.logger.debug(f"{type_} Error :: {line}", exc_info=True)
        file.close()

    def __cinex(self, input_file, out_path, yara):
        """Ingests the crawled links from the input_file,
        scrapes the contents of the resulting web pages and writes the contents to
        the into out_path/{url_address}.

        :param input_file: String: Filename of the crawled Urls.
        :param out_path: String: Pathname of results.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        self.__inex(type_="Cinex", input_file=input_file, yara=yara, out_path=out_path)

    def __intermex(self, input_file, yara):
        """Input links from file and extract them into terminal.

        :param input_file: String: File name of links file.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        self.__inex(type_="Intermex", input_file=input_file, yara=yara)

    def __ex(self, type_, website, yara, output_file=None, out_path=None):
        """Scrapes the contents of the provided web address and outputs the
        contents to file or terminal.

        :param type: String: Either "Outex" or "Termex".
        :param website: String: Url of web address to scrape.
        :param yara: Integer: Keyword search argument.
        :param output_file: String|None: Filename of the results.
        :param out_path: String|None: Folder name of the output findings.
        :return: None
        """
        # Extract page to file
        try:
            if out_path is not None:
                output_file = os.path.join(out_path, output_file)
            content = self.__session.get(website, allow_redirects=True, timeout=10).text

            full_match_keywords = self.__check_yara(type_=type_, raw=content, yara=yara)

            self.logger.debug(
                f"{type_} :: {website} :: {'Yara' if len(full_match_keywords) else 'No yara'} match found!"
            )

            if out_path is not None:
                with open(output_file, "w+", encoding="UTF-8") as file:
                    file.write(content)
                self.logger.debug(f"{type_} File created :: {output_file}")
            else:
                self.logger.info(f"{website} :: {content}")
        except HTTPError as _:
            self.logger.debug(f"{type_} Request Error :: {website}", exc_info=True)
        except (InvalidURL, URLError) as _:
            self.logger.debug(f"{type_} Invalid URL Error :: {website} :: Skipping...")
        except IncompleteRead as _:
            self.logger.debug(f"{type_} Incomplete Read Error :: {website}")
        except IOError as _:
            self.logger.debug(f"{type_} IOError Error :: {website}", exc_info=True)
        except Exception as _:
            self.logger.debug(f"{type_} Error :: {website}", exc_info=True)

    def __outex(self, website, output_file, out_path, yara):
        """Scrapes the contents of the provided web address and outputs the
        contents to file.

        :param website: String: Url of web address to scrape.
        :param output_file: String: Filename of the results.
        :param out_path: String: Folder name of the output findings.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        self.__ex(
            type_="Outex",
            website=website,
            yara=yara,
            output_file=output_file,
            out_path=out_path,
        )

    def __termex(self, website, yara):
        """Scrapes provided web address and prints the results to the terminal.

        :param website: String: URL of website to scrape.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        self.__ex(type_="Termex", website=website, yara=yara)
