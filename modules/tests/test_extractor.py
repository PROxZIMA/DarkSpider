import os.path
import shutil
import unittest
import urllib.request
from collections import defaultdict
from unittest import mock

from modules.checker import folder
from modules.extractor import (
    check_yara,
    cinex,
    extractor,
    intermex,
    outex,
    termex,
    text,
)


def mocked_urllib_open(*args, **kwargs):
    """Custom sideeffect for mock testing network urls"""

    class MockResponse:
        """Custom mock response"""

        def __init__(self, response_data):
            self.response_data = response_data

        def read(self):
            """Read method for urllib.request.urlopen"""
            return self.response_data

    responses = defaultdict(None)

    responses[
        "http://info.cern.ch/"
    ] = b'<html><head></head><body><header>\n<title>http://info.cern.ch</title>\n</header>\n\n<h1>http://info.cern.ch - home of the first website</h1>\n<p>From here you can:</p>\n<ul>\n<li><a href="http://info.cern.ch/hypertext/WWW/TheProject.html">Browse the first website</a></li>\n<li><a href="http://line-mode.cern.ch/www/hypertext/WWW/TheProject.html">Browse the first website using the line-mode browser simulator</a></li>\n<li><a href="http://home.web.cern.ch/topics/birth-web">Learn about the birth of the web</a></li>\n<li><a href="http://home.web.cern.ch/about">Learn about CERN, the physics laboratory where the web was born</a></li>\n</ul>\n</body></html>\n'

    responses[
        "http://info.cern.ch/hypertext/WWW/TheProject.html"
    ] = b'<HEADER>\n<TITLE>The World Wide Web project</TITLE>\n<NEXTID N="55">\n</HEADER>\n<BODY>\n<H1>World Wide Web</H1>The WorldWideWeb (W3) is a wide-area<A\nNAME=0 HREF="WhatIs.html">\nhypermedia</A> information retrieval\ninitiative aiming to give universal\naccess to a large universe of documents.<P>\nEverything there is online about\nW3 is linked directly or indirectly\nto this document, including an <A\nNAME=24 HREF="Summary.html">executive\nsummary</A> of the project, <A\nNAME=29 HREF="Administration/Mailing/Overview.html">Mailing lists</A>\n, <A\nNAME=30 HREF="Policy.html">Policy</A> , November\'s  <A\nNAME=34 HREF="News/9211.html">W3  news</A> ,\n<A\nNAME=41 HREF="FAQ/List.html">Frequently Asked Questions</A> .\n<DL>\n<DT><A\nNAME=44 HREF="../DataSources/Top.html">What\'s out there?</A>\n<DD> Pointers to the\nworld\'s online information,<A\nNAME=45 HREF="../DataSources/bySubject/Overview.html"> subjects</A>\n, <A\nNAME=z54 HREF="../DataSources/WWW/Servers.html">W3 servers</A>, etc.\n<DT><A\nNAME=46 HREF="Help.html">Help</A>\n<DD> on the browser you are using\n<DT><A\nNAME=13 HREF="Status.html">Software Products</A>\n<DD> A list of W3 project\ncomponents and their current state.\n(e.g. <A\nNAME=27 HREF="LineMode/Browser.html">Line Mode</A> ,X11 <A\nNAME=35 HREF="Status.html#35">Viola</A> ,  <A\nNAME=26 HREF="NeXT/WorldWideWeb.html">NeXTStep</A>\n, <A\nNAME=25 HREF="Daemon/Overview.html">Servers</A> , <A\nNAME=51 HREF="Tools/Overview.html">Tools</A> ,<A\nNAME=53 HREF="MailRobot/Overview.html"> Mail robot</A> ,<A\nNAME=52 HREF="Status.html#57">\nLibrary</A> )\n<DT><A\nNAME=47 HREF="Technical.html">Technical</A>\n<DD> Details of protocols, formats,\nprogram internals etc\n<DT><A\nNAME=40 HREF="Bibliography.html">Bibliography</A>\n<DD> Paper documentation\non  W3 and references.\n<DT><A\nNAME=14 HREF="People.html">People</A>\n<DD> A list of some people involved\nin the project.\n<DT><A\nNAME=15 HREF="History.html">History</A>\n<DD> A summary of the history\nof the project.\n<DT><A\nNAME=37 HREF="Helping.html">How can I help</A> ?\n<DD> If you would like\nto support the web..\n<DT><A\nNAME=48 HREF="../README.html">Getting code</A>\n<DD> Getting the code by<A\nNAME=49 HREF="LineMode/Defaults/Distribution.html">\nanonymous FTP</A> , etc.</A>\n</DL>\n</BODY>\n'

    return MockResponse(responses[args[0]])


class TestCheckerFunctions(unittest.TestCase):
    """Unit test for Extractor module."""

    def setUp(self):

        # os.rmdir("torcrawl", ignore_errors=True)

        self.out_path = folder("torcrawl", False)
        self.inp_path = os.path.join(self.out_path, "links.txt")

        with open(self.inp_path, "w", encoding="utf-8") as f:
            f.write("http://info.cern.ch/\n")
            f.write("http://info.cern.ch/hypertext/WWW/TheProject.html")

        # with open(link_1, "wb") as f:
        #     f.write(mocked_urllib_open("http://info.cern.ch/").read())

        # with open(link_2, "wb") as f:
        #     f.write(
        #         mocked_urllib_open(
        #             "http://info.cern.ch/hypertext/WWW/TheProject.html"
        #         ).read()
        #     )

    def tearDown(self):
        """Test Suite Teardown."""
        # Remove test folder.
        shutil.rmtree(self.out_path)

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_text(self, _):
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

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_check_yara_001(self, _):
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

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_check_yara_002(self, _):
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

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_check_yara_003(self, _):
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

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_check_yara_004(self, _):
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

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_check_yara_005(self, _):
        """check_yara unit test.
        Validates Yara Rule to categorize the site and check for keywords.
        """
        expected = None
        result = check_yara(raw=None, yara=1)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    def test_cinex(self):
        """cinex unit test.
        Ingests the crawled links from the input_file,
        scrapes the contents of the resulting web pages and writes the contents to
        the into out_path/{url_address}.
        """
        cinex(self.inp_path, self.out_path)
        link_1 = os.path.join(self.out_path, "index.htm")
        link_2 = os.path.join(self.out_path, "TheProject.htm")

        with open(link_1, "rb") as f:
            expected = mocked_urllib_open("http://info.cern.ch/").read()
            result = f.read()
            self.assertEqual(
                expected, result, f"Test Fail:: expected = {expected}, got {result}"
            )

        with open(link_2, "rb") as f:
            expected = mocked_urllib_open(
                "http://info.cern.ch/hypertext/WWW/TheProject.html"
            ).read()
            result = f.read()
            self.assertEqual(
                expected, result, f"Test Fail:: expected = {expected}, got {result}"
            )

    # TODO: Implement intermex, outex, termex, extractor test cases
