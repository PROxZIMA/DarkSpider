import os.path
import shutil
import unittest
from collections import defaultdict
from copy import copy
from unittest import mock

from modules.checker import folder
from modules.extractor import Extractor
from modules.helper import assert_msg, setup_custom_logger

URL_1 = "http://info.cern.ch/"
URL_2 = "http://info.cern.ch/hypertext/WWW/TheProject.html"
URL_3 = "unknown_path"


def mocked_requests_Session_get(*args, **kwargs):
    """Custom sideeffect for mock testing network urls"""

    class MockResponse:
        """Custom mock response"""

        def __init__(self, response_data):
            self.text = response_data

    responses = defaultdict(lambda: "")

    responses[
        URL_1
    ] = '<html><head></head><body><header>\n<title>http://info.cern.ch</title>\n</header>\n\n<h1>http://info.cern.ch - home of the first website</h1>\n<p>From here you can:</p>\n<ul>\n<li><a href="http://info.cern.ch/hypertext/WWW/TheProject.html">Browse the first website</a></li>\n<li><a href="http://line-mode.cern.ch/www/hypertext/WWW/TheProject.html">Browse the first website using the line-mode browser simulator</a></li>\n<li><a href="http://home.web.cern.ch/topics/birth-web">Learn about the birth of the web</a></li>\n<li><a href="http://home.web.cern.ch/about">Learn about CERN, the physics laboratory where the web was born</a></li>\n</ul>\n</body></html>\n'

    responses[
        URL_2
    ] = '<HEADER>\n<TITLE>The World Wide Web project</TITLE>\n<NEXTID N="55">\n</HEADER>\n<BODY>\n<H1>World Wide Web</H1>The WorldWideWeb (W3) is a wide-area<A\nNAME=0 HREF="WhatIs.html">\nhypermedia</A> information retrieval\ninitiative aiming to give universal\naccess to a large universe of documents.<P>\nEverything there is online about\nW3 is linked directly or indirectly\nto this document, including an <A\nNAME=24 HREF="Summary.html">executive\nsummary</A> of the project, <A\nNAME=29 HREF="Administration/Mailing/Overview.html">Mailing lists</A>\n, <A\nNAME=30 HREF="Policy.html">Policy</A> , November\'s  <A\nNAME=34 HREF="News/9211.html">W3  news</A> ,\n<A\nNAME=41 HREF="FAQ/List.html">Frequently Asked Questions</A> .\n<DL>\n<DT><A\nNAME=44 HREF="../DataSources/Top.html">What\'s out there?</A>\n<DD> Pointers to the\nworld\'s online information,<A\nNAME=45 HREF="../DataSources/bySubject/Overview.html"> subjects</A>\n, <A\nNAME=z54 HREF="../DataSources/WWW/Servers.html">W3 servers</A>, etc.\n<DT><A\nNAME=46 HREF="Help.html">Help</A>\n<DD> on the browser you are using\n<DT><A\nNAME=13 HREF="Status.html">Software Products</A>\n<DD> A list of W3 project\ncomponents and their current state.\n(e.g. <A\nNAME=27 HREF="LineMode/Browser.html">Line Mode</A> ,X11 <A\nNAME=35 HREF="Status.html#35">Viola</A> ,  <A\nNAME=26 HREF="NeXT/WorldWideWeb.html">NeXTStep</A>\n, <A\nNAME=25 HREF="Daemon/Overview.html">Servers</A> , <A\nNAME=51 HREF="Tools/Overview.html">Tools</A> ,<A\nNAME=53 HREF="MailRobot/Overview.html"> Mail robot</A> ,<A\nNAME=52 HREF="Status.html#57">\nLibrary</A> )\n<DT><A\nNAME=47 HREF="Technical.html">Technical</A>\n<DD> Details of protocols, formats,\nprogram internals etc\n<DT><A\nNAME=40 HREF="Bibliography.html">Bibliography</A>\n<DD> Paper documentation\non  W3 and references.\n<DT><A\nNAME=14 HREF="People.html">People</A>\n<DD> A list of some people involved\nin the project.\n<DT><A\nNAME=15 HREF="History.html">History</A>\n<DD> A summary of the history\nof the project.\n<DT><A\nNAME=37 HREF="Helping.html">How can I help</A> ?\n<DD> If you would like\nto support the web..\n<DT><A\nNAME=48 HREF="../README.html">Getting code</A>\n<DD> Getting the code by<A\nNAME=49 HREF="LineMode/Defaults/Distribution.html">\nanonymous FTP</A> , etc.</A>\n</DL>\n</BODY>\n'

    return MockResponse(responses[args[0]])


@mock.patch("requests.Session.get", side_effect=mocked_requests_Session_get)
class TestCheckerFunctions(unittest.TestCase):
    """Unit test for Extractor module."""

    @classmethod
    def setUpClass(cls) -> None:
        """Test Suite Setup."""
        cls.out_path = os.path.join("test_run", "darkspider")
        cls.out_file = os.path.join(cls.out_path, "index.html")
        cls.inp_file = os.path.join(cls.out_path, "links.txt")
        cls.logger = setup_custom_logger(
            name="testlog",
            filename=None,
            verbose_=False,
            filelog=False,
            argv=None,
        )
        cls.extractor_1 = Extractor(
            website=URL_1,
            proxies=None,
            crawl=False,
            output_file=cls.out_file,
            input_file=cls.inp_file,
            out_path=cls.out_path,
            thread=1,
            yara=True,
            logger=cls.logger,
        )

    def setUp(self):
        """Test Case Setup."""
        folder(self.out_path, False)

        with open(self.inp_file, "w", encoding="utf-8") as f:
            f.write(f"{URL_1}\n")
            f.write(f"{URL_2}\n")
            f.write(URL_3)

    def tearDown(self):
        """Test Case Teardown."""
        # Remove test folder.
        shutil.rmtree(os.path.dirname(self.out_path), ignore_errors=True)

    def get_response_text(self, url: str) -> str:
        """Get patched response text.

        Args:
            url: URL to get response text.

        Returns:
            Response text.
        """
        return self.extractor_1._Extractor__session.get(url, allow_redirects=True, timeout=10).text

    def test_text(self, _):
        """text unit test."""
        expected = """http://info.cern.ch http://info.cern.ch - home of the first website From here you can: Browse the first website Browse the first website using the line-mode browser simulator Learn about the birth of the web Learn about CERN, the physics laboratory where the web was born"""
        content = self.get_response_text(URL_1)
        result = self.extractor_1._Extractor__text(response=content)
        self.assertEqual(expected, result, assert_msg(expected, result))

    def test_check_yara_001(self, _):
        """check_yara unit test."""
        expected = {
            "matches": True,
            "rule": "keyword_search",
            "namespace": "default",
            "tags": [],
            "meta": {"author": "@the-siegfried", "score": 90},
            "strings": [
                (124, "$a", b"website"),
                (249, "$a", b"website"),
                (356, "$a", b"website"),
                (574, "$b", b"physics laboratory"),
                (80, "$c", b"<h1>http://"),
                (558, "$d", b"about CERN"),
                (48, "$e", b"info.cern.ch"),
                (91, "$e", b"info.cern.ch"),
                (188, "$e", b"info.cern.ch"),
            ],
        }

        content = self.get_response_text(URL_1)
        result = self.extractor_1._Extractor__check_yara(raw=content, yara=0)
        self.assertEqual(expected, result, assert_msg(expected, result))

    def test_check_yara_002(self, _):
        """check_yara unit test.
        Validates Yara Rule to categorize the site and check for keywords.
        """
        expected = {
            "matches": True,
            "rule": "keyword_search",
            "namespace": "default",
            "tags": [],
            "meta": {"author": "@the-siegfried", "score": 90},
            "strings": [
                (60, "$a", b"website"),
                (104, "$a", b"website"),
                (129, "$a", b"website"),
                (230, "$b", b"physics laboratory"),
                (214, "$d", b"about cern"),
                (7, "$e", b"info.cern.ch"),
                (27, "$e", b"info.cern.ch"),
            ],
        }

        content = self.get_response_text(URL_1)
        result = self.extractor_1._Extractor__check_yara(raw=content, yara=1)
        self.assertEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_cinex_001(self, _, __):
        """cinex unit test."""
        expected = [
            [
                (10, ("%s :: %s match found!", URL_1, "Yara"), False),
                (10, ("File created :: %s", f"{self.out_path}/info.cern.ch/_.html"), False),
            ],
            [
                (10, ("%s :: %s match found!", URL_2, "No yara"), False),
                (
                    10,
                    ("File created :: %s", f"{self.out_path}/info.cern.ch/hypertext/WWW/TheProject.html_.html"),
                    False,
                ),
            ],
            [
                (10, ("%s :: %s match found!", URL_3, "No yara"), False),
                (10, ("File created :: %s", f"{self.out_path}/unknown_path_.html"), False),
            ],
        ]

        result = self.extractor_1._Extractor__cinex(self.inp_file, self.out_path, 0)

        self.assertCountEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_cinex_002(self, _, __):
        """cinex unit test."""
        expected = [
            [(10, ("File created :: %s", f"{self.out_path}/info.cern.ch/_.html"), False)],
            [
                (
                    10,
                    ("File created :: %s", f"{self.out_path}/info.cern.ch/hypertext/WWW/TheProject.html_.html"),
                    False,
                )
            ],
            [(10, ("File created :: %s", f"{self.out_path}/unknown_path_.html"), False)],
        ]

        result = self.extractor_1._Extractor__cinex(self.inp_file, self.out_path, None)

        self.assertCountEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_terminex_001(self, _, __):
        """intermex unit test."""
        expected = [
            [
                (10, ("%s :: %s match found!", URL_1, "Yara"), False),
                (20, ("%s :: %s", URL_1, mocked_requests_Session_get(URL_1).text), False),
            ],
            [
                (10, ("%s :: %s match found!", URL_2, "No yara"), False),
                (
                    20,
                    (
                        "%s :: %s",
                        URL_2,
                        mocked_requests_Session_get(URL_2).text,
                    ),
                    False,
                ),
            ],
            [
                (10, ("%s :: %s match found!", URL_3, "No yara"), False),
                (20, ("%s :: %s", URL_3, mocked_requests_Session_get(URL_3).text), False),
            ],
        ]

        result = self.extractor_1._Extractor__terminex(self.inp_file, 1)

        self.assertCountEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_terminex_002(self, _, __):
        """intermex unit test."""
        expected = [
            [
                (20, ("%s :: %s", URL_1, mocked_requests_Session_get(URL_1).text), False),
            ],
            [
                (
                    20,
                    (
                        "%s :: %s",
                        URL_2,
                        mocked_requests_Session_get(URL_2).text,
                    ),
                    False,
                ),
            ],
            [
                (20, ("%s :: %s", URL_3, mocked_requests_Session_get(URL_3).text), False),
            ],
        ]

        result = self.extractor_1._Extractor__terminex(self.inp_file, None)

        self.assertCountEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_outex_001(self, _, __):
        """outex unit test."""
        expected = [
            (10, ("%s :: %s match found!", URL_1, "Yara"), False),
            (10, ("File created :: %s", f"{self.out_path}/index.html"), False),
        ]

        result = self.extractor_1._Extractor__outex(URL_1, self.out_file, 0)

        self.assertEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_outex_002(self, _, __):
        """outex unit test."""
        expected = [
            (10, ("File created :: %s", f"{self.out_path}/index.html"), False),
        ]

        result = self.extractor_1._Extractor__outex(URL_1, self.out_file, None)

        self.assertEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_termex_001(self, _, __):
        """termex unit test."""
        expected = [
            (10, ("%s :: %s match found!", URL_1, "Yara"), False),
            (20, ("%s :: %s", URL_1, mocked_requests_Session_get(URL_1).text), False),
        ]

        result = self.extractor_1._Extractor__termex(URL_1, 1)

        self.assertEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_termex_002(self, _, __):
        """termex unit test."""
        expected = [
            (20, ("%s :: %s", URL_1, mocked_requests_Session_get(URL_1).text), False),
        ]

        result = self.extractor_1._Extractor__termex(URL_1, None)

        self.assertEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_extractor_001(self, _, __):
        """extractor unit test."""
        expected = [
            [
                (10, ("%s :: %s match found!", URL_1, "Yara"), False),
                (10, ("File created :: %s", f"{self.out_path}/info.cern.ch/_.html"), False),
            ],
            [
                (10, ("%s :: %s match found!", URL_2, "No yara"), False),
                (
                    10,
                    ("File created :: %s", f"{self.out_path}/info.cern.ch/hypertext/WWW/TheProject.html_.html"),
                    False,
                ),
            ],
            [
                (10, ("%s :: %s match found!", URL_3, "No yara"), False),
                (10, ("File created :: %s", f"{self.out_path}/unknown_path_.html"), False),
            ],
        ]

        result = self.extractor_1.extract()

        self.assertEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_extractor_002(self, _, __):
        """extractor unit test."""
        expected = [
            [
                (10, ("%s :: %s match found!", URL_1, "Yara"), False),
                (20, ("%s :: %s", URL_1, mocked_requests_Session_get(URL_1).text), False),
            ],
            [
                (10, ("%s :: %s match found!", "http://info.cern.ch/hypertext/WWW/TheProject.html", "No yara"), False),
                (
                    20,
                    (
                        "%s :: %s",
                        "http://info.cern.ch/hypertext/WWW/TheProject.html",
                        mocked_requests_Session_get(URL_2).text,
                    ),
                    False,
                ),
            ],
            [
                (10, ("%s :: %s match found!", URL_3, "No yara"), False),
                (20, ("%s :: %s", URL_3, mocked_requests_Session_get(URL_3).text), False),
            ],
        ]

        extractor_2 = copy(self.extractor_1)
        extractor_2.out_path = None

        result = extractor_2.extract()

        self.assertEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_extractor_003(self, _, __):
        """extractor unit test."""
        expected = [
            [
                (10, ("%s :: %s match found!", "http://info.cern.ch/hypertext/WWW/TheProject.html", "No yara"), False),
                (10, ("File created :: %s", f"{self.out_path}/index.html"), False),
            ]
        ]

        extractor_3 = copy(self.extractor_1)
        extractor_3.website = URL_2
        extractor_3.input_file = ""
        extractor_3.output_file = "index.html"

        result = extractor_3.extract()

        self.assertEqual(expected, result, assert_msg(expected, result))

    @mock.patch("concurrent.futures.ThreadPoolExecutor.shutdown", side_effect=[lambda wait: None])
    def test_extractor_004(self, _, __):
        """extractor unit test."""
        expected = [
            [
                (10, ("%s :: %s match found!", URL_3, "No yara"), False),
                (20, ("%s :: %s", URL_3, mocked_requests_Session_get(URL_3).text), False),
            ]
        ]

        extractor_4 = copy(self.extractor_1)
        extractor_4.website = URL_3
        extractor_4.input_file = ""
        extractor_4.output_file = ""

        result = extractor_4.extract()

        self.assertEqual(expected, result, assert_msg(expected, result))
