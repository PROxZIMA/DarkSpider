import os
import sys
from logging import Logger
from typing import Optional
from urllib.parse import urlparse

import psutil
import requests

from modules.helper import TorProxyException, get_requests_header
from modules.helper.helper import TorServiceException


def url_canon(website: str, www: bool = False) -> tuple[bool, str]:
    """URL normalisation/canonicalization

    Args:
        website: URL of website.
        www: True if www is to be included else False.

    Returns:
        A tuple of a boolean indicating whether ``website`` is normalised, normalised ``website``.
    """
    canon = False
    if not website.startswith("http"):
        if www and not website.startswith("www."):
            website = "www." + website
        website = "http://" + website
        canon = True

    # Remove trailing slash if website is just a hostname
    uri = urlparse(website)
    if uri.path == "/":
        website = website.rstrip("/")

    return canon, website


def extract_domain(url: str, remove_http: bool = True) -> str:
    """Parses the provided 'url' to provide only the netloc or
    scheme + netloc parts of the provided url.

    Args:
        url: Url to parse.
        remove_http: True if http/https is to be removed else False.

    Returns:
        Resulting parsed Url.
    """
    uri = urlparse(url)
    if remove_http:
        domain_name = f"{uri.netloc}"
    else:
        domain_name = f"{uri.scheme}://{uri.netloc}"
    return domain_name


def folder(out_path: str, is_file: bool = False) -> str:
    """Creates an output path for the findings.

    Args:
        out_path: Output path in which all extracted data is stored.
        is_file: True if output path is a file else False.

    Returns:
        Path of the output folder.
    """
    os.makedirs(os.path.dirname(out_path) if is_file else out_path, exist_ok=True)
    return out_path


def check_tor(logger: Logger) -> Optional[bool]:
    """Checks to see if TOR service is running on device.
    Will exit if (-w) with argument is provided on application startup and TOR
    service is not found to be running on the device.

    Args:
        Logger: A logger object to log the output.

    Returns:
        True if TOR service is running.

    Raises:
        TorServiceException: If Tor Service is not working.
    """
    try:
        tor = "tor"
        for i in psutil.process_iter():
            if tor == i.name().lower().rstrip(".exe"):
                logger.debug("TOR is ready!")
                break
        else:
            raise TorServiceException("TOR is NOT running! Enable tor with 'service tor start' or add -w argument")
        return True
    except Exception as err:
        # We could've logged the TorServiceException where it was raised and could've avoided try/catch block
        # but we want to log unexpected errors too and raise all the exception
        logger.critical(err)
        raise


def check_ip(
    proxies: Optional[dict[str, str]], url: str, logger: Logger, without_tor: bool = False
) -> Optional[dict[str, str | bool]]:
    """Checks users IP and Tor proxy connection from external resource.

    Args:
        proxies: Dictionary mapping protocol or protocol and host to the URL of the proxy.
        url: Url to debug.
        logger: A logger object to log the output.
        without_tor: True if not using Tor for crawling/extraction else False.

    Returns:
        Dictionary containing the IP address and the Tor proxy flag.

        {"IsTor":True,
        "IP":"185.165.171.46"}

    Raises:
        TorProxyException: If Tor proxy is not working.
    """
    addr = "https://check.torproject.org/api/ip"
    headers = get_requests_header()
    try:
        # https://tor.stackexchange.com/a/13079
        # Double check to tackle false positives
        check1 = requests.get(addr, headers=headers, proxies=proxies, timeout=10, verify=False).json()

        check2 = requests.get(addr, headers=headers, proxies=proxies, timeout=10, verify=False).json()

        logger.debug(
            "Your IP: %s :: Tor Connection: %s",
            check2["IP"],
            check1["IsTor"] or check2["IsTor"],
        )
        logger.debug("URL :: %s", url)

        # If both checks are false, then Tor proxy is not working
        if not (check1["IsTor"] or check2["IsTor"] or without_tor):
            raise TorProxyException(
                "Tor proxy is NOT running! More info: https://support.torproject.org/connecting/#connecting-4"
            )

        return check2
    except Exception as err:
        # We could've logged the TorProxyException where it was raised and could've avoided try/catch block
        # but we want to log unexpected errors too and raise all the exception
        logger.critical(err)
        raise
