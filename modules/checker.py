#!/usr/bin/python

import os
import sys
from urllib.parse import urlparse

import psutil
import requests

from modules.helpers.helper import (
    TorProxyException,
    get_requests_header,
    traceback_name,
)


def url_canon(website, verbose):
    """URL normalisation/canonicalization

    :param website: String - URL of website.
    :param verbose: Boolean - Verbose logging switch.
    :return: String 'website' - normalised result.
    """
    if not website.startswith("http"):
        if not website.startswith("www."):
            website = "www." + website
            if verbose:
                print(("## URL fixed: " + website))
        website = "http://" + website
        if verbose:
            print(("## URL fixed: " + website))
    return website


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
def folder(website, verbose):
    """Creates an output path for the findings.

    :param website: String - URL of website to crawl.
    :param verbose: Boolean - Logging level.
    :return: String 'out_path' - Path of the output folder.
    """
    out_path = website
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    if verbose:
        print(f"## Folder created: {out_path}")
    return out_path


def check_tor(verbose):
    """Checks to see if TOR service is running on device.
    Will exit if (-w) with argument is provided on application startup and TOR
    service is not found to be running on the device.

    :param verbose: Boolean -'verbose' logging argument.
    :return: None
    """
    for i in psutil.process_iter():
        if "tor" == i.name().lower().rstrip(".exe"):
            if verbose:
                print("## TOR is ready!")
            break
    else:
        print("## TOR is NOT running!")
        print("## Enable tor with 'service tor start' or add -w argument")
        sys.exit(2)


def check_ip(proxies, url, verbose, without_tor):
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

        if verbose:
            print(
                f"## Your IP: {check2['IP']} :: Tor Connection: {check1['IsTor'] or check2['IsTor']}"
            )
            print(f"## URL: {url}")

        if (
            check1["IsTor"] is False
            and check2["IsTor"] is False
            and without_tor is False
        ):
            raise TorProxyException(
                "Tor proxy is NOT running! More info: https://support.torproject.org/connecting/#connecting-4"
            )
    except Exception as err:
        print(f"## Exception: {traceback_name(err)} \n## Error: {err}")
        sys.exit(2)
