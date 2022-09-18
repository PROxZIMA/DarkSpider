#!/usr/bin/python

import os
import sys
from urllib.parse import urlparse

import psutil
import requests

from modules.helpers.helper import TorProxyException, get_requests_header


def url_canon(website):
    """URL normalisation/canonicalization

    :param website: String - URL of website.
    :return: String 'website' - normalised result.
    """
    canon = False
    if not website.startswith("http"):
        if not website.startswith("www."):
            website = "www." + website
        website = "http://" + website
        canon = True
    return canon, website


def extract_domain(url, remove_http=True):
    """Parses the provided 'url' to provide only the netloc or
    scheme + netloc parts of the provided url.

    :param url: String - Url to parse.
    :param remove_http: Boolean
    :return: String 'domain_name' - Resulting parsed Url
    """
    uri = urlparse(url)
    if remove_http:
        domain_name = f"{uri.netloc}"
    else:
        domain_name = f"{uri.scheme}://{uri.netloc}"
    return domain_name


# Create output path
def folder(out_path):
    """Creates an output path for the findings.

    :param out_path: String - Output path in which all extracted data is stored.
    :return: String 'out_path' - Path of the output folder.
    """
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    return out_path


def check_tor(logger):
    """Checks to see if TOR service is running on device.
    Will exit if (-w) with argument is provided on application startup and TOR
    service is not found to be running on the device.

    :param Logger logger: A logger object to log the output.
    :return: None
    """
    for i in psutil.process_iter():
        if "tor" == i.name().lower().rstrip(".exe"):
            logger.debug("TOR is ready!")
            break
    else:
        logger.critical("TOR is NOT running!")
        logger.critical("Enable tor with 'service tor start' or add -w argument")
        sys.exit(2)


def check_ip(proxies, url, logger, without_tor):
    """Checks users IP from external resource.
    :return: None
    """
    addr = "https://check.torproject.org/api/ip"
    headers = get_requests_header()
    try:
        # https://tor.stackexchange.com/a/13079
        # Double check to tackle false positives
        check1 = requests.get(
            addr, headers=headers, proxies=proxies, timeout=10, verify=False
        ).json()

        check2 = requests.get(
            addr, headers=headers, proxies=proxies, timeout=10, verify=False
        ).json()

        logger.debug(
            "Your IP: %s :: Tor Connection: %s",
            check2["IP"],
            check1["IsTor"] or check2["IsTor"],
        )
        logger.debug("URL :: %s", url)

        if (
            check1["IsTor"] is False
            and check2["IsTor"] is False
            and without_tor is False
        ):
            raise TorProxyException(
                "Tor proxy is NOT running! More info: https://support.torproject.org/connecting/#connecting-4"
            )
    except Exception as err:
        logger.exception(err)
        sys.exit(2)
