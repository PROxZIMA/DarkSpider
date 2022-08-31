import shutil
import unittest
from copy import copy

from modules.checker import extract_domain, folder
from modules.crawler import Crawler
from modules.helpers.helper import Capturing


class TestCrawlerFunctions(unittest.TestCase):
    """Unit test for Crawler module."""

    def setUp(self):
        self._website = "http://info.cern.ch/"
        self.out_path = out_path = folder(extract_domain(self._website), False)
        self.crawler = Crawler(
            website=self._website,
            c_depth=1,
            c_pause=1,
            out_path=out_path,
            external=False,
            logs=False,
            verbose=False,
            exclusion=None,
        )
        self.crawler_ex = copy(self.crawler)
        self.crawler_ex.external = True
        # Exclude links with subdomain='home.web'
        self.crawler_ex.exclusion = ".*//home\.web.*"

    def tearDown(self):
        """Test Suite Teardown."""
        # Remove test folder.
        shutil.rmtree(self.out_path)

    def test_excludes(self):
        """Test crawler.excludes function.
        Return True if the function successfully excludes the the provided
        failing links.
        """
        _uri = self._website
        failing_links = [
            None,
            "#",
            "http://home.web.cern.ch/topics",
            "tel:012-013-104-5",
            "mailto:test@torcrawl.com",
            f"{_uri}/res/test.pdf",
            f"{_uri}/res/test.jpg",
            f"{_uri}/res/test.jpeg",
            f"{_uri}/res/test.png",
            f"{_uri}/res/test.gif",
            f"{_uri}/res/test.doc",
        ]
        for link in failing_links:
            self.assertTrue(
                self.crawler.excludes(link),
                f"Test Fail:: Link: {link} - not excluded",
            )
            self.assertTrue(
                self.crawler_ex.excludes(link),
                f"Test Fail:: Link: {link} - not excluded",
            )
        # External links are allowed if it does not match the exclusion pattern
        link = "http://google.com/page.html"
        self.assertFalse(
            self.crawler_ex.excludes(link),
            f"Test Fail:: Link: {link} - excluded",
        )

    def test_canonical(self):
        """Test crawler.canonical function.
        Return True if the function successfully normalizes the provided
        failing links.
        """
        _uri = self._website
        links = [
            [f"{_uri}sundance", f"{_uri}sundance"],
            ["//sundance", "http://sundance"],
            ["/sundance", f"{_uri}sundance"],
            [f"{_uri}bob.html", f"{_uri}bob.html"],
            ["bob.html", f"{_uri}bob.html"],
        ]

        for link, expected in links:
            result = self.crawler.canonical(_uri, link)
            self.assertEqual(
                expected,
                result,
                f"Test Fail:: Canon returned = {result}, " f"expected {link[1]}",
            )

    def test_crawl(self):
        """Test Crawlwer.crawl functionality

        Return: List (ord_lst) - List of crawled links."""
        _uri = self._website

        with Capturing() as _:
            result = self.crawler.crawl()
            result_ex = self.crawler_ex.crawl()

        expected = {
            _uri: [
                f"{_uri}hypertext/WWW/TheProject.html",
            ]
        }

        # Following links are excluded as they match the exclusion pattern
        # http://home.web.cern.ch/topics/birth-web
        # http://home.web.cern.ch/about
        expected_ex = {
            _uri: [
                f"{_uri}hypertext/WWW/TheProject.html",
                "http://line-mode.cern.ch/www/hypertext/WWW/TheProject.html",
            ]
        }

        self.assertCountEqual(
            expected,
            result,
            f"Test Fail:: Crawler returned = {result}, " f"expected {expected}",
        )
        self.assertCountEqual(
            expected_ex,
            result_ex,
            f"Test Fail:: Crawler returned = {result_ex}, " f"expected {expected_ex}",
        )
