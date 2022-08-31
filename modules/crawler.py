#!/usr/bin/python
import http.client
import json
import os
import re
import sys
import time
import urllib.request
from urllib.parse import urljoin

from bs4 import BeautifulSoup


class Crawler:
    """Crawl input link upto depth (c_depth) with a pause of c_pause seconds.

    :param website: String: Website to crawl.
    :param c_depth: Integer: Depth of the crawl.
    :param c_pause: Integer: Pause after every iteration.
    :param out_path: String: Output path to store extracted links.
    :param external: Boolean: True if external links are to be crawled else False.
    :param logs: Boolean: True if logs are to be written else False.
    :param verbose: Boolean: True if crawl details are to be printed else False.
    :param exclusion: re String: Paths that you don't want to include.
    """

    def __init__(
        self, website, c_depth, c_pause, out_path, external, logs, verbose, exclusion
    ):
        self.website = website
        self.c_depth = c_depth
        self.c_pause = c_pause
        self.out_path = out_path
        self.external = rf"{external}"
        self.logs = logs
        self.verbose = verbose
        self.exclusion = exclusion

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
            file_path = self.out_path + "/extlinks.txt"
            with open(file_path, "a+", encoding="UTF-8") as lst_file:
                lst_file.write(str(link) + "\n")
            return True
        # Telephone Number
        if link.startswith("tel:"):
            file_path = self.out_path + "/telephones.txt"
            with open(file_path, "a+", encoding="UTF-8") as lst_file:
                lst_file.write(str(link) + "\n")
            return True
        # Mails
        if link.startswith("mailto:"):
            file_path = self.out_path + "/mails.txt"
            with open(file_path, "a+", encoding="UTF-8") as lst_file:
                lst_file.write(str(link) + "\n")
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

    def crawl(self):
        """Core of the crawler.
        :return: Dict (json_data) - Dictionary of crawled links.
        """
        ord_lst = set([self.website])
        old_level = [self.website]
        cur_level = set()
        log_path = self.out_path + "/log.txt"
        if self.logs is True and os.access(log_path, os.W_OK) is ~os.path.exists(
            log_path
        ):
            print(f"## Unable to write to {self.out_path}/log.txt - Exiting")
            sys.exit(2)

        print(
            f"## Crawler started from {self.website} with "
            f"{str(self.c_depth)} depth crawl, {'' if self.exclusion else 'and '}{str(self.c_pause)} "
            f"second(s) delay. Excluding {self.exclusion if self.exclusion else 'no'} links."
        )

        # Json dictionary
        json_data = {}
        # Depth
        for index in range(0, int(self.c_depth)):
            # For every element of list.
            for item in old_level:
                # Don't crawl if already crawled
                if item.rstrip("/") in json_data:
                    continue

                # Store the crawled link of an item
                item_data = set()
                html_page = http.client.HTTPResponse
                try:
                    if item is not None:
                        html_page = urllib.request.urlopen(item, timeout=10)
                except Exception as error:
                    print(error)
                    continue
                # Keeps logs for every webpage visited.
                if self.logs:
                    with open(log_path, "a+", encoding="UTF-8") as log_file:
                        log_file.write(f"{str(item)}\n")

                try:
                    soup = BeautifulSoup(html_page, features="html.parser")
                except Exception as _:
                    print(f"## Soup Error Encountered:: to parse :: {item}")
                    continue

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

                # TODO: For images
                # TODO: For scripts

                if self.verbose:
                    sys.stdout.write("-- Results: " + str(len(ord_lst)) + "\r")
                    sys.stdout.flush()

                # Pause time
                time.sleep(float(self.c_pause))

                # Add item_data to crawled links.
                cur_level = cur_level.union(item_data)
                # Adding to json data
                json_data[item] = list(item_data)

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
            json_path = self.out_path + "/network_structure.json"
            with open(json_path, "w", encoding="UTF-8") as lst_file:
                json.dump(json_data, lst_file, indent=2, sort_keys=False)

            with open(self.out_path + "/links.txt", "w+", encoding="UTF-8") as file:
                for item in sorted(ord_lst):
                    file.write(f"{item}\n")

        return json_data
