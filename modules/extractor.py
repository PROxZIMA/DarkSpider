#!/usr/bin/python
import os
import urllib.error
import urllib.parse
import urllib.request
from http.client import IncompleteRead, InvalidURL
from io import TextIOWrapper
from urllib.error import HTTPError, URLError

import requests
import yara as _yara
from bs4 import BeautifulSoup

from modules.helpers.helper import get_requests_header, traceback_name


class Extractor:
    """Extractor - scrapes the resulting website or discovered links.

    :param str website: URL of website to scrape.
    :param dict[str, str] proxies: Dictionary mapping protocol or protocol and host to the URL of the proxy.
    :param bool crawl: Cinex trigger. If used iteratively scrape the urls from input_file.
    :param str output_file: Filename of resulting output from scrape.
    :param str input_file: Filename of crawled/discovered URLs
    :param str out_path: Dir path for output files.
    :param int yara: keyword search option.
    """

    __headers = get_requests_header()

    def __init__(
        self,
        website: str,
        proxies: dict[str, str],
        crawl: bool,
        output_file: str,
        input_file: str,
        out_path: str,
        yara: int,
    ):
        self.website = website
        self.proxies = proxies
        self.crawl = crawl
        self.output_file = output_file
        self.input_file = input_file

        self.out_path = os.path.join(out_path, "extracted")
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

        self.yara = yara
        self.__session = self.__get_tor_session()

    def __get_tor_session(self):
        session = requests.Session()
        # session.proxies = self.proxies
        # session.headers.update(self.__headers)
        # session.verify = False
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

        :param raw: HTTP Response body.
        :param yara:  Integer: Keyword search argument.
        :return matches: List of yara rule matches.
        """

        file_path = os.path.join("res/keywords.yar")

        if raw is not None:
            if yara == 1:
                raw = self.__text(response=raw).lower()

            file = os.path.join(file_path)
            rules = _yara.compile(file)
            matches = rules.match(data=raw)
            if len(matches) != 0:
                print("found a match!")
            return matches
        return None

    def __cinex(self, input_file, out_path, yara=None):
        """Ingests the crawled links from the input_file,
        scrapes the contents of the resulting web pages and writes the contents to
        the into out_path/{url_address}.

        :param input_file: String: Filename of the crawled Urls.
        :param out_path: String: Pathname of results.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        file = TextIOWrapper
        try:
            file = open(input_file, "r", encoding="UTF-8")
        except IOError as err:
            print(f"Error: {err}\n## Can't open: {input_file}")

        for line in file.read().splitlines():

            # Generate the name for every file.
            try:
                page_name = line.rsplit("/", 1)
                cl_page_name = str(page_name[1])
                if len(cl_page_name) == 0:
                    output_file = "index.html"
                else:
                    output_file = cl_page_name
            except IndexError as error:
                print(f"Error: {error}")
                continue

            # Extract page to file.
            try:
                content = self.__session.get(
                    line, allow_redirects=True, timeout=10
                ).text

                if yara is not None:
                    full_match_keywords = self.__check_yara(content, yara)

                    if len(full_match_keywords) == 0:
                        print("No matches found.")
                        continue

                with open(
                    os.path.join(out_path, output_file), "w+", encoding="UTF-8"
                ) as results:
                    results.write(content)
                print(f"# File created on: {os.path.join(out_path, output_file)}")
            except HTTPError as err:
                print(f"Cinex Error: {err.code}, cannot access: {err.url}")
                continue
            except InvalidURL as _:
                print(f"Invalid URL: {line} \n Skipping...")
                continue
            except IncompleteRead as _:
                print(f"IncompleteRead on {line}")
                continue
            except IOError as err:
                print(f"Error: {err}\nCan't write on file: {output_file}")
        file.close()

    def __intermex(self, input_file, yara):
        """Input links from file and extract them into terminal.

        :param input_file: String: File name of links file.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        try:
            with open(input_file, "r", encoding="UTF-8") as file:
                for line in file.read().splitlines():
                    content = self.__session.get(
                        line, allow_redirects=True, timeout=10
                    ).text
                    if yara is not None:
                        full_match_keywords = self.__check_yara(raw=content, yara=yara)

                        if full_match_keywords is None or len(full_match_keywords) == 0:
                            print(f"No matches in: {line}")
                    print(content)
        except (HTTPError, URLError, InvalidURL) as err:
            print(f"Request Error: {err}")
        except IOError as err:
            print(f"Error: {err}\n## Not valid file")
        except Exception as err:
            print(f"Error: {err}")

    def __outex(self, website, output_file, out_path, yara):
        """Scrapes the contents of the provided web address and outputs the
        contents to file.

        :param website: String: Url of web address to scrape.
        :param output_file: String: Filename of the results.
        :param out_path: String: Folder name of the output findings.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        # Extract page to file
        try:
            output_file = os.path.join(out_path, output_file)
            content = self.__session.get(website, allow_redirects=True, timeout=10).text

            if yara is not None:
                full_match_keywords = self.__check_yara(raw=content, yara=yara)

                if len(full_match_keywords) == 0:
                    print(f"No matches in: {website}")

            with open(output_file, "w+", encoding="UTF-8") as file:
                file.write(content)
            print(f"## File created on: {output_file}")
        except (HTTPError, URLError, InvalidURL) as err:
            print(f"HTTPError: {err}")
        except IOError as err:
            print(f"Error: {err}\n Can't write on file: {output_file}")

    def __termex(self, website, yara):
        """Scrapes provided web address and prints the results to the terminal.

        :param website: String: URL of website to scrape.
        :param yara: Integer: Keyword search argument.
        :return: None
        """
        try:
            content = self.__session.get(website, allow_redirects=True, timeout=10).text
            if yara is not None:
                full_match_keywords = self.__check_yara(content, yara)

                if full_match_keywords is None or len(full_match_keywords) == 0:
                    # No match.
                    print(f"No matches in: {website}")
                    return

            print(content)
        except (HTTPError, URLError, InvalidURL) as err:
            print(f"Error: ({err}) {website}")
            return

    def extract(self):
        """Extracts the contents of the input file into the outputs folder/file"""
        # TODO: Return output to torcrawl.py
        if len(self.input_file) > 0:
            if self.crawl:
                self.__cinex(self.input_file, self.out_path, self.yara)
            # TODO: Extract from list into a folder
            # elif len(output_file) > 0:
            # 	inoutex(website, input_ile, output_file)
            else:
                self.__intermex(self.input_file, self.yara)
        else:
            if len(self.output_file) > 0:
                self.__outex(self.website, self.output_file, self.out_path, self.yara)
            else:
                self.__termex(self.website, self.yara)
