import os.path
import shutil
import sys
import unittest
import urllib.request
from ast import literal_eval
from collections import defaultdict
from io import StringIO
from pathlib import Path
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

URL_1 = "http://info.cern.ch/"
URL_2 = "http://info.cern.ch/hypertext/WWW/TheProject.html"
URL_3 = "unknown_path"


class Capturing(list):
    """Capture stdout into a single buffer."""

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def mocked_urllib_open(*args, **kwargs):
    """Custom sideeffect for mock testing network urls"""

    class MockResponse:
        """Custom mock response"""

        def __init__(self, response_data):
            self.response_data = response_data

        def read(self):
            """Read method for urllib.request.urlopen"""
            return self.response_data

    responses = defaultdict(lambda: None)

    responses[
        URL_1
    ] = b'<html><head></head><body><header>\n<title>http://info.cern.ch</title>\n</header>\n\n<h1>http://info.cern.ch - home of the first website</h1>\n<p>From here you can:</p>\n<ul>\n<li><a href="http://info.cern.ch/hypertext/WWW/TheProject.html">Browse the first website</a></li>\n<li><a href="http://line-mode.cern.ch/www/hypertext/WWW/TheProject.html">Browse the first website using the line-mode browser simulator</a></li>\n<li><a href="http://home.web.cern.ch/topics/birth-web">Learn about the birth of the web</a></li>\n<li><a href="http://home.web.cern.ch/about">Learn about CERN, the physics laboratory where the web was born</a></li>\n</ul>\n</body></html>\n'

    responses[
        URL_2
    ] = b'<HEADER>\n<TITLE>The World Wide Web project</TITLE>\n<NEXTID N="55">\n</HEADER>\n<BODY>\n<H1>World Wide Web</H1>The WorldWideWeb (W3) is a wide-area<A\nNAME=0 HREF="WhatIs.html">\nhypermedia</A> information retrieval\ninitiative aiming to give universal\naccess to a large universe of documents.<P>\nEverything there is online about\nW3 is linked directly or indirectly\nto this document, including an <A\nNAME=24 HREF="Summary.html">executive\nsummary</A> of the project, <A\nNAME=29 HREF="Administration/Mailing/Overview.html">Mailing lists</A>\n, <A\nNAME=30 HREF="Policy.html">Policy</A> , November\'s  <A\nNAME=34 HREF="News/9211.html">W3  news</A> ,\n<A\nNAME=41 HREF="FAQ/List.html">Frequently Asked Questions</A> .\n<DL>\n<DT><A\nNAME=44 HREF="../DataSources/Top.html">What\'s out there?</A>\n<DD> Pointers to the\nworld\'s online information,<A\nNAME=45 HREF="../DataSources/bySubject/Overview.html"> subjects</A>\n, <A\nNAME=z54 HREF="../DataSources/WWW/Servers.html">W3 servers</A>, etc.\n<DT><A\nNAME=46 HREF="Help.html">Help</A>\n<DD> on the browser you are using\n<DT><A\nNAME=13 HREF="Status.html">Software Products</A>\n<DD> A list of W3 project\ncomponents and their current state.\n(e.g. <A\nNAME=27 HREF="LineMode/Browser.html">Line Mode</A> ,X11 <A\nNAME=35 HREF="Status.html#35">Viola</A> ,  <A\nNAME=26 HREF="NeXT/WorldWideWeb.html">NeXTStep</A>\n, <A\nNAME=25 HREF="Daemon/Overview.html">Servers</A> , <A\nNAME=51 HREF="Tools/Overview.html">Tools</A> ,<A\nNAME=53 HREF="MailRobot/Overview.html"> Mail robot</A> ,<A\nNAME=52 HREF="Status.html#57">\nLibrary</A> )\n<DT><A\nNAME=47 HREF="Technical.html">Technical</A>\n<DD> Details of protocols, formats,\nprogram internals etc\n<DT><A\nNAME=40 HREF="Bibliography.html">Bibliography</A>\n<DD> Paper documentation\non  W3 and references.\n<DT><A\nNAME=14 HREF="People.html">People</A>\n<DD> A list of some people involved\nin the project.\n<DT><A\nNAME=15 HREF="History.html">History</A>\n<DD> A summary of the history\nof the project.\n<DT><A\nNAME=37 HREF="Helping.html">How can I help</A> ?\n<DD> If you would like\nto support the web..\n<DT><A\nNAME=48 HREF="../README.html">Getting code</A>\n<DD> Getting the code by<A\nNAME=49 HREF="LineMode/Defaults/Distribution.html">\nanonymous FTP</A> , etc.</A>\n</DL>\n</BODY>\n'

    return MockResponse(responses[args[0]])


class TestCheckerFunctions(unittest.TestCase):
    """Unit test for Extractor module."""

    def setUp(self):
        self.out_path = folder("torcrawl", False)
        self.inp_path = "links.txt"

        with open(self.inp_path, "w", encoding="utf-8") as f:
            f.write(f"{URL_1}\n")
            f.write(f"{URL_2}\n")
            f.write(URL_3)

    def tearDown(self):
        """Test Suite Teardown."""
        # Remove input file.
        os.remove(self.inp_path)
        # Remove test folder.
        shutil.rmtree(self.out_path, ignore_errors=True)

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_text(self, _):
        """text unit test.
        Removes all the garbage from the HTML and takes only text elements from the page.
        """
        expected = """http://info.cern.ch http://info.cern.ch - home of the first website From here you can: Browse the first website Browse the first website using the line-mode browser simulator Learn about the birth of the web Learn about CERN, the physics laboratory where the web was born"""

        content = urllib.request.urlopen(URL_1, timeout=10).read()
        result = text(response=content)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_check_yara_001(self, _):
        """check_yara unit test.
        Validates Yara Rule to categorize the site and check for keywords.
        """
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

        content = urllib.request.urlopen(URL_1, timeout=10).read()
        result = check_yara(raw=content, yara=0)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_check_yara_002(self, _):
        """check_yara unit test.
        Validates Yara Rule to categorize the site and check for keywords.
        """
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

        content = urllib.request.urlopen(URL_1, timeout=10).read()
        result = check_yara(raw=content, yara=1)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_check_yara_003(self, _):
        """check_yara unit test.
        Validates Yara Rule to categorize the site and check for keywords.
        """
        expected = {}

        content = urllib.request.urlopen(URL_2, timeout=10).read()
        result = check_yara(raw=content, yara=0)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_check_yara_004(self, _):
        """check_yara unit test.
        Validates Yara Rule to categorize the site and check for keywords.
        """
        expected = {}

        content = urllib.request.urlopen(URL_2, timeout=10).read()
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

        content = urllib.request.urlopen(URL_3, timeout=10).read()
        result = check_yara(raw=content, yara=1)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_cinex_001(self, _):
        """cinex unit test.
        Ingests the crawled links from the input_file,
        scrapes the contents of the resulting web pages and writes the contents to
        the into out_path/{url_address}.
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            f"# File created on: {Path(__file__).parent.parent.parent}/{self.out_path}/index.htm",
            f"# File created on: {Path(__file__).parent.parent.parent}/{self.out_path}/TheProject.htm",
            "Error: list index out of range",
        ]

        with Capturing() as result:
            cinex(self.inp_path, self.out_path)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

        # We can't simply compare the contents of the files in `self.out_path`
        # because the order of the files is not guaranteed.
        link_1 = os.path.join(self.out_path, "index.htm")
        link_2 = os.path.join(self.out_path, "TheProject.htm")

        with open(link_1, "rb") as f:
            expected = mocked_urllib_open(URL_1).read()
            result = f.read()
            self.assertEqual(
                expected, result, f"Test Fail:: expected = {expected}, got {result}"
            )

        with open(link_2, "rb") as f:
            expected = mocked_urllib_open(URL_2).read()
            result = f.read()
            self.assertEqual(
                expected, result, f"Test Fail:: expected = {expected}, got {result}"
            )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_cinex_002(self, _):
        """cinex unit test.
        Ingests the crawled links from the input_file,
        scrapes the contents of the resulting web pages and writes the contents to
        the into out_path/{url_address}.
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            "found a match!",
            f"# File created on: {Path(__file__).parent.parent.parent}/{self.out_path}/index.htm",
            "No matches found.",
            "Error: list index out of range",
        ]

        with Capturing() as result:
            cinex(self.inp_path, self.out_path, yara=1)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

        link = os.path.join(self.out_path, "index.htm")

        with open(link, "rb") as f:
            expected = mocked_urllib_open(URL_1).read()
            result = f.read()
            self.assertEqual(
                expected, result, f"Test Fail:: expected = {expected}, got {result}"
            )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_intermex_001(self, _):
        """intermex unit test.
        Input links from file and extract them into terminal.
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            mocked_urllib_open(URL_1).read(),
            mocked_urllib_open(URL_2).read(),
            "None",
        ]

        with Capturing() as result:
            intermex(self.inp_path, None)

        result = [
            literal_eval(x) if x.startswith("b'") and x.endswith("'") else x
            for x in result
        ]
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_intermex_002(self, _):
        """intermex unit test.
        Input links from file and extract them into terminal.
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            "found a match!",
            mocked_urllib_open(URL_1).read(),
            f"No matches in: {URL_2}",
            mocked_urllib_open(URL_2).read(),
            f"No matches in: {URL_3}",
            "None",
        ]

        with Capturing() as result:
            intermex(self.inp_path, 1)

        result = [
            literal_eval(x) if x.startswith("b'") and x.endswith("'") else x
            for x in result
        ]
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_intermex_003(self, _):
        """intermex unit test.
        Input links from file and extract them into terminal.
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            "Error: [Errno 2] No such file or directory: 'unknown_path'",
            "## Not valid file",
        ]

        with Capturing() as result:
            intermex("unknown_path", None)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_outex_001(self, _):
        """outex unit test.
        Scrapes the contents of the provided web address and outputs the
        contents to file.
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            f"## File created on: {Path(__file__).parent.parent.parent}/{self.out_path}/index.htm"
        ]

        with Capturing() as result:
            outex(URL_1, "index.htm", self.out_path, None)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

        link = os.path.join(self.out_path, "index.htm")

        with open(link, "rb") as f:
            expected = mocked_urllib_open(URL_1).read()
            result = f.read()
            self.assertEqual(
                expected, result, f"Test Fail:: expected = {expected}, got {result}"
            )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_outex_002(self, _):
        """outex unit test.
        Scrapes the contents of the provided web address and outputs the
        contents to file.
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            "found a match!",
            f"## File created on: {Path(__file__).parent.parent.parent}/{self.out_path}/index.htm",
        ]

        with Capturing() as result:
            outex(URL_1, "index.htm", self.out_path, 1)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

        link = os.path.join(self.out_path, "index.htm")

        with open(link, "rb") as f:
            expected = mocked_urllib_open(URL_1).read()
            result = f.read()
            self.assertEqual(
                expected, result, f"Test Fail:: expected = {expected}, got {result}"
            )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_outex_003(self, _):
        """outex unit test.
        Scrapes the contents of the provided web address and outputs the
        contents to file.
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            "found a match!",
            f"Error: [Errno 21] Is a directory: '{self.out_path}/'",
            f" Can't write on file: {self.out_path}/",
        ]

        with Capturing() as result:
            outex(URL_1, "", self.out_path, 1)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_outex_004(self, _):
        """outex unit test.
        Scrapes the contents of the provided web address and outputs the
        contents to file.
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            f"Error: [Errno 21] Is a directory: '{self.out_path}/'",
            f" Can't write on file: {self.out_path}/",
        ]

        with Capturing() as result:
            outex(URL_1, "", self.out_path, None)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_termex_001(self, _):
        """termex unit test.
        Scrapes provided web address and prints the results to the terminal
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            mocked_urllib_open(URL_1).read(),
        ]

        with Capturing() as result:
            termex(URL_1, None)

        result = [literal_eval(*result)]
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_termex_002(self, _):
        """termex unit test.
        Scrapes provided web address and prints the results to the terminal
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [f"No matches in: {URL_2}"]

        with Capturing() as result:
            termex(URL_2, 1)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_termex_003(self, _):
        """termex unit test.
        Scrapes provided web address and prints the results to the terminal
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = ["None"]

        with Capturing() as result:
            termex("unknown_path", None)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_termex_004(self, _):
        """termex unit test.
        Scrapes provided web address and prints the results to the terminal
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [f"No matches in: {URL_3}"]

        with Capturing() as result:
            termex("unknown_path", 1)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_extractor_001(self, _):
        """extractor unit test.
        Extractor - scrapes the resulting website or discovered links
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            f"# File created on: {Path(__file__).parent.parent.parent}/{self.out_path}/index.htm",
            f"# File created on: {Path(__file__).parent.parent.parent}/{self.out_path}/TheProject.htm",
            "Error: list index out of range",
        ]

        with Capturing() as result:
            # Cinex
            extractor(URL_1, True, "index.htm", self.inp_path, self.out_path, None)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_extractor_002(self, _):
        """extractor unit test.
        Extractor - scrapes the resulting website or discovered links
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            mocked_urllib_open(URL_1).read(),
            mocked_urllib_open(URL_2).read(),
            "None",
        ]

        with Capturing() as result:
            # Intermex
            extractor(URL_1, False, "index.htm", self.inp_path, self.out_path, None)

        result = [
            literal_eval(x) if x.startswith("b'") and x.endswith("'") else x
            for x in result
        ]
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_extractor_003(self, _):
        """extractor unit test.
        Extractor - scrapes the resulting website or discovered links
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            f"## File created on: {Path(__file__).parent.parent.parent}/{self.out_path}/index.htm"
        ]

        with Capturing() as result:
            # Outex
            extractor(URL_1, True, "index.htm", "", self.out_path, None)

        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    @mock.patch("urllib.request.urlopen", side_effect=mocked_urllib_open)
    def test_extractor_004(self, _):
        """extractor unit test.
        Extractor - scrapes the resulting website or discovered links
        """

        shutil.rmtree(self.out_path, ignore_errors=True)
        folder(self.out_path, False)
        expected = [
            mocked_urllib_open(URL_1).read(),
        ]

        with Capturing() as result:
            # Termex
            extractor(URL_1, True, "", "", self.out_path, None)

        result = [literal_eval(*result)]
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )
