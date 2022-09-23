import shutil
import unittest

from modules import Crawler
from modules.checker import extract_domain, folder
from modules.helper import setup_custom_logger

# Disable sorted test case loading
unittest.TestLoader.sortTestMethodsUsing = lambda *args: -1


class TestCrawlerFunctions(unittest.TestCase):
    """Unit test for Crawler module."""

    @classmethod
    def setUpClass(cls):
        """Test Suite Setup."""
        cls._website = "http://info.cern.ch/"
        cls.out_path = out_path = folder(extract_domain(cls._website), False)
        cls.logger = setup_custom_logger(
            name="testlog",
            filename=None,
            verbose_=False,
            filelog=False,
            argv=None,
        )
        cls.crawler = Crawler(
            website=cls._website,
            proxies=None,
            c_depth=1,
            c_pause=1,
            out_path=out_path,
            external=False,
            exclusion=None,
            thread=1,
            logger=cls.logger,
        )
        # Exclude links with subdomain='home.web'
        cls.crawler_ex = Crawler(
            website=cls._website,
            proxies=None,
            c_depth=1,
            c_pause=1,
            out_path=out_path,
            external=True,
            exclusion=".*//home\.web.*",
            thread=1,
            logger=cls.logger,
        )

    @classmethod
    def tearDownClass(cls):
        """Test Suite Teardown."""
        # Remove test folder.
        shutil.rmtree(cls.out_path)

    def test_excludes(self):
        """Test crawler.excludes function."""
        _uri = self._website
        failing_links = [
            None,
            "#",
            "http://home.web.cern.ch/topics",
            "tel:012-013-104-5",
            "mailto:test@darkspider.com",
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
        """Test crawler.canonical function."""
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
                f"Test Fail:: Canon returned = {result}, expected {link[1]}",
            )

    def test_crawl_001(self):
        """Test Crawler.crawl functionality"""
        _uri = self._website

        # with Capturing() as _:
        result = self.crawler.crawl()

        expected = {
            _uri: [
                f"{_uri}hypertext/WWW/TheProject.html",
            ]
        }

        self.assertCountEqual(
            expected,
            result,
            f"Test Fail:: Crawler returned = {result}, expected {expected}",
        )

    def test_crawl_002(self):
        """Test Crawler.crawl functionality"""
        _uri = self._website

        # with Capturing() as _:
        result_ex = self.crawler_ex.crawl()

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
            expected_ex,
            result_ex,
            f"Test Fail:: Crawler returned = {result_ex}, expected {expected_ex}",
        )
