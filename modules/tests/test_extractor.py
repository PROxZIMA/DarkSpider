import os.path
import unittest
import urllib.request

from modules.extractor import (
    check_yara,
    cinex,
    extractor,
    intermex,
    outex,
    termex,
    text,
)


class TestCheckerFunctions(unittest.TestCase):
    """Unit test for Extractor module."""

    @classmethod
    def setUp(cls) -> None:
        pass

    def test_text(self):
        """text unit test.
        Removes all the garbage from the HTML and takes only text elements from the page.
        """
        url = "http://info.cern.ch/"
        expected = """http://info.cern.ch http://info.cern.ch - home of the first website From here you can: Browse the first website Browse the first website using the line-mode browser simulator Learn about the birth of the web Learn about CERN, the physics laboratory where the web was born"""

        content = urllib.request.urlopen(url, timeout=10).read()
        result = text(response=content)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    def test_check_yara_001(self):
        """check_yara unit test.
        Validates Yara Rule to categorize the site and check for keywords.
        """
        url = "http://info.cern.ch/"
        expected = {
            "main": [
                {
                    "matches": True,
                    "meta": {"author": "@the-siegfried", "score": 90},
                    "rule": "keyword_search",
                    "strings": [
                        {
                            "data": "info.cern.ch",
                            "flags": 27,
                            "identifier": "$e",
                            "offset": 48,
                        },
                        {
                            "data": "info.cern.ch",
                            "flags": 27,
                            "identifier": "$e",
                            "offset": 91,
                        },
                        {
                            "data": "info.cern.ch",
                            "flags": 27,
                            "identifier": "$e",
                            "offset": 188,
                        },
                        {
                            "data": "about CERN",
                            "flags": 27,
                            "identifier": "$d",
                            "offset": 558,
                        },
                        {
                            "data": "<h1>http://",
                            "flags": 19,
                            "identifier": "$c",
                            "offset": 80,
                        },
                        {
                            "data": "physics laboratory",
                            "flags": 59,
                            "identifier": "$b",
                            "offset": 574,
                        },
                        {
                            "data": "website",
                            "flags": 187,
                            "identifier": "$a",
                            "offset": 124,
                        },
                        {
                            "data": "website",
                            "flags": 187,
                            "identifier": "$a",
                            "offset": 249,
                        },
                        {
                            "data": "website",
                            "flags": 187,
                            "identifier": "$a",
                            "offset": 356,
                        },
                    ],
                    "tags": [],
                }
            ]
        }

        content = urllib.request.urlopen(url, timeout=10).read()
        result = check_yara(raw=content, yara=0)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    def test_check_yara_002(self):
        """check_yara unit test.
        Validates Yara Rule to categorize the site and check for keywords.
        """
        url = "http://info.cern.ch/"
        expected = {
            "main": [
                {
                    "matches": True,
                    "meta": {"author": "@the-siegfried", "score": 90},
                    "rule": "keyword_search",
                    "strings": [
                        {
                            "data": "info.cern.ch",
                            "flags": 27,
                            "identifier": "$e",
                            "offset": 7,
                        },
                        {
                            "data": "info.cern.ch",
                            "flags": 27,
                            "identifier": "$e",
                            "offset": 27,
                        },
                        {
                            "data": "about cern",
                            "flags": 27,
                            "identifier": "$d",
                            "offset": 214,
                        },
                        {
                            "data": "physics laboratory",
                            "flags": 59,
                            "identifier": "$b",
                            "offset": 230,
                        },
                        {
                            "data": "website",
                            "flags": 187,
                            "identifier": "$a",
                            "offset": 60,
                        },
                        {
                            "data": "website",
                            "flags": 187,
                            "identifier": "$a",
                            "offset": 104,
                        },
                        {
                            "data": "website",
                            "flags": 187,
                            "identifier": "$a",
                            "offset": 129,
                        },
                    ],
                    "tags": [],
                }
            ]
        }

        content = urllib.request.urlopen(url, timeout=10).read()
        result = check_yara(raw=content, yara=1)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    def test_check_yara_003(self):
        """check_yara unit test.
        Validates Yara Rule to categorize the site and check for keywords.
        """
        url = "http://info.cern.ch/hypertext/WWW/TheProject.html"
        expected = {}

        content = urllib.request.urlopen(url, timeout=10).read()
        result = check_yara(raw=content, yara=0)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    def test_check_yara_004(self):
        """check_yara unit test.
        Validates Yara Rule to categorize the site and check for keywords.
        """
        url = "http://info.cern.ch/hypertext/WWW/TheProject.html"
        expected = {}

        content = urllib.request.urlopen(url, timeout=10).read()
        result = check_yara(raw=content, yara=1)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    def test_check_yara_005(self):
        """check_yara unit test.
        Validates Yara Rule to categorize the site and check for keywords.
        """
        expected = None
        result = check_yara(raw=None, yara=1)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    # TODO: Implement cinex, intermex, outex, termex, extractor test cases
