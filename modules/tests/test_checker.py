import os.path
import re
import shutil
import unittest
from typing import Iterator, List
from unittest import mock

from modules.checker import check_ip, check_tor, extract_domain, folder, url_canon
from modules.helper import TorProxyException, TorServiceException, assert_msg, get_tor_proxies, setup_custom_logger


class MockedPsutilProcess:
    """Custom class for mock testing psutil process"""

    def __init__(self, _name: str):
        self._name = _name

    def name(self) -> str:
        """Returns the name of the process"""
        return self._name


def mocked_psutil_process_iter(has_tor: bool = True) -> List[Iterator[MockedPsutilProcess]]:
    """Custom sideeffect for mock testing psutil process

    Args:
        has_tor: True if tor is to be included else False.

    Returns:
        List of processes.
    """

    response = [MockedPsutilProcess("firefox"), MockedPsutilProcess("chrome")]

    if has_tor:
        response.append(MockedPsutilProcess("tor"))

    return [iter(response)]


class TestCheckerFunctions(unittest.TestCase):
    """Unit test for Checker module."""

    @classmethod
    def setUpClass(cls) -> None:
        """Test Suite Setup."""
        cls.path = os.path.join("test_run", "darkspider")
        cls.logger = setup_custom_logger(
            name="testlog",
            filename=None,
            verbose_=False,
            filelog=False,
            argv=None,
        )

    @classmethod
    def tearDownClass(cls):
        """Test Suite Teardown."""
        # Remove test folder.
        shutil.rmtree(os.path.dirname(cls.path), ignore_errors=True)

    def test_url_canon_001(self):
        """url_canon unit test."""
        url = "www.darkspider.com"
        expected = (True, "http://www.darkspider.com")
        result = url_canon(url, www=False)
        self.assertEqual(expected, result, assert_msg(expected, result))

    def test_url_canon_002(self):
        """url_canon unit test."""
        url = "www.darkspider.com"
        expected = (True, "http://www.darkspider.com")
        result = url_canon(url, www=True)
        self.assertEqual(expected, result, assert_msg(expected, result))

    def test_url_canon_003(self):
        """url_canon unit test."""
        url = "darkspider.com"
        expected = (True, "http://www.darkspider.com")
        result = url_canon(url, www=True)
        self.assertEqual(expected, result, assert_msg(expected, result))

    def test_url_canon_004(self):
        """url_canon unit test."""
        url = "http://darkspider.com/"
        expected = (False, "http://darkspider.com")
        result = url_canon(url, www=False)
        self.assertEqual(expected, result, assert_msg(expected, result))

    def test_extract_domain_001(self):
        """extract_domain test."""
        url = "http://darkspider.com/test/domain-extract/api?id=001"
        expected = "darkspider.com"
        result = extract_domain(url, remove_http=True)
        self.assertEqual(expected, result, assert_msg(expected, result))

    def test_extract_domain_002(self):
        """extract_domain test."""
        url = "http://darkspider.com/test/domain-extract/api?id=002"
        expected = "http://darkspider.com"
        result = extract_domain(url, remove_http=False)
        self.assertEqual(expected, result, assert_msg(expected, result))

    def test_folder_creation_001(self):
        """folder creation test."""
        _input = self.path
        result = folder(_input, False)
        self.assertTrue(os.path.exists(result), f"Test Fail:: could not find folder {_input}")

    def test_folder_creation_002(self):
        """folder creation test."""
        _input = os.path.join(self.path, "deep", "folder", "file.txt")
        result = folder(_input, True)
        expected = os.path.dirname(_input)
        self.assertTrue(os.path.exists(expected), f"Test Fail:: could not find directory of {_input}")
        self.assertEqual(expected, result, assert_msg(expected, result))

    def test_check_ip_001(self):
        """check_ip test."""

        with self.assertRaises(Exception) as error:
            # `None proxy` and `with tor` will raise exception.
            check_ip(proxies=None, url=None, logger=self.logger, without_tor=False)

        self.assertEqual(error.exception.error_code, TorProxyException.error_code)

    def test_check_ip_002(self):
        """check_ip test."""
        expected_ip = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"

        response = check_ip(proxies=None, url=None, logger=self.logger, without_tor=True)

        self.assertTrue(
            bool(re.match(expected_ip, response["IP"])),
            f"Test Fail:: expected = {expected_ip}, got {response['IP']}",
        )
        self.assertFalse(
            response["IsTor"],
            f"Test Fail:: Tor proxy flag must be False, got {response['IsTor']}",
        )

    def test_check_ip_003(self):
        """check_ip test."""
        expected_ip = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"

        response = check_ip(proxies=get_tor_proxies(), url=None, logger=self.logger, without_tor=True)

        self.assertTrue(
            bool(re.match(expected_ip, response["IP"])),
            f"Test Fail:: expected = {expected_ip}, got {response['IP']}",
        )
        self.assertTrue(
            response["IsTor"],
            f"Test Fail:: Tor proxy flag must be True, got {response['IsTor']}",
        )

    @mock.patch("psutil.process_iter", side_effect=mocked_psutil_process_iter(has_tor=True))
    def test_check_tor_001(self, _):
        """check_tor test."""
        self.assertTrue(
            check_tor(self.logger),
            "Test Fail:: Tor Service must be running",
        )

    @mock.patch("psutil.process_iter", side_effect=mocked_psutil_process_iter(has_tor=False))
    def test_check_tor_002(self, _):
        """check_tor test."""
        with self.assertRaises(Exception) as error:
            # `None proxy` and `with tor` will raise exception.
            check_tor(self.logger)

        self.assertEqual(error.exception.error_code, TorServiceException.error_code)
