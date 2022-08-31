import os.path
import re
import shutil
import unittest

from modules.checker import check_ip, check_tor, extract_domain, folder, url_canon
from modules.helpers.helper import Capturing


class TestCheckerFunctions(unittest.TestCase):
    """Unit test for Checker module."""

    @classmethod
    def setUp(cls) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        """Test Suite Teardown."""
        # Remove test folder.
        shutil.rmtree("torcrawl", ignore_errors=True)

    def test_url_canon_001(self):
        """url_canon unit test.
        Returns true if the function successfully performs URL normalisation.
        """
        url = "torcrawl.com"
        expected = "http://www.torcrawl.com"
        result = url_canon(url, verbose=False)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    def test_url_canon_002(self):
        """url_canon unit test.
        Returns true if the function successfully performs URL normalisation.
        """
        url = "www.torcrawl.com"
        expected = "http://www.torcrawl.com"
        result = url_canon(url, verbose=False)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    def test_extract_domain_001(self):
        """extract_domain test.
        Returns true if correct domain is returned.
        """
        url = "http://www.torcrawl.com/test/domain-extract/api?id=001"
        expected = "www.torcrawl.com"
        result = extract_domain(url, remove_http=True)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    def test_extract_domain_002(self):
        """extract_domain test.
        Returns true if correct domain is returned.
        """
        url = "http://www.torcrawl.com/test/domain-extract/api?id=002"
        expected = "http://www.torcrawl.com"
        result = extract_domain(url, remove_http=False)
        self.assertEqual(
            expected, result, f"Test Fail:: expected = {expected}, got {result}"
        )

    def test_folder_creation(self):
        """folder creation test.
        Returns true if folder is successfully created.
        """
        _input = "torcrawl"
        result = folder(_input, False)
        self.assertTrue(
            os.path.exists(result), f"Test Fail:: could not find folder {_input}"
        )

    def test_check_tor(self):
        """folder creation test.
        Returns true if folder is successfully created.
        """
        expected_ip = r"^## Your IP: (?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        expected_error = [
            "Error: <class 'urllib.error.HTTPError'> ",
            "## IP cannot be obtained. ",
            "## Is https://api.ipify.org/?format=json up? ",
            "## HTTPError: HTTP Error 404: Not Found",
        ]

        with Capturing() as result:
            check_ip()

        if result[0].startswith("## Your IP:"):
            self.assertEqual(
                re.findall(expected_ip, result[0]),
                result,
                f"Test Fail:: expected = {expected_ip}, got {result}",
            )
        else:
            self.assertEqual(
                expected_error,
                result,
                f"Test Fail:: expected = {expected_ip}, got {result}",
            )

    # TODO: Implement check_tor tests.
