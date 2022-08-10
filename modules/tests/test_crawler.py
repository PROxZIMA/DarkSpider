import shutil
import unittest

from modules.checker import extract_domain, folder, url_canon
from modules.crawler import Crawler


class TestCrawlerFunctions(unittest.TestCase):
    """Unit test for Crawler module."""

    def setUp(self):
        _website = "http://info.cern.ch/"
        self.out_path = out_path = folder(extract_domain(_website), False)
        self.crawler = Crawler(_website, 1, 1, out_path, False, False)

    def tearDown(self):
        """Test Suite Teardown."""
        # Remove test folder.
        shutil.rmtree(self.out_path)

    def test_excludes(self):
        """Test crawler.excludes function.
        Return True if the function successfully excludes the the provided
        failing links.
        """
        _uri = "http://info.cern.ch/"
        failing_links = [
            "#",
            "tel:012-013-104-5",
            "mailto:test@torcrawl.com",
            f"{_uri}/res/test.pdf",
            f"{_uri}/res/test.doc",
            f"{_uri}/res/test.jpg",
            f"{_uri}/res/test.png",
            f"{_uri}/res/test.jpeg",
            f"{_uri}/res/test.gif",
        ]
        for link in failing_links:
            self.assertTrue(
                self.crawler.excludes(link), f"Test Fail:: Link: {link} - not excluded"
            )

    def test_canonical(self):
        """Test crawler.canonical function.
        Return True if the function successfully normalizes the provided
        failing links.
        """
        _uri = "http://info.cern.ch/"
        links = [
            [f"{_uri}sundance", f"{_uri}sundance"],
            ["/sundance", f"{_uri}sundance"],
            [f"{_uri}bob.html", f"{_uri}bob.html"],
            ["bob.html", f"{_uri}bob.html"],
        ]

        for link in links:
            result = self.crawler.canonical(link[0])
            self.assertEqual(
                link[1],
                result,
                f"Test Fail:: Canon returned = {result}, " f"expected {link[1]}",
            )

    def test_crawl(self):
        """Test Crawlwer.crawl functionality

        Return: List (ord_lst) - List of crawled links."""
        result = self.crawler.crawl()
        expected = [
            "http://info.cern.ch/",
            "http://info.cern.ch/hypertext/WWW/TheProject.html",
        ]

        self.assertEqual(
            expected,
            result,
            f"Test Fail:: Canon returned = {result}, " f"expected {expected}",
        )
