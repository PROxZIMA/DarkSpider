---
layout: default
title: What is DarkSpider?
nav_order: 1
permalink: /
---

# What is DarkSpider?

DarkSpider is a multithreaded crawler and extractor for regular or onion webpages through the TOR network, written in Python.
{: .fs-6 .fw-300 }

[Get started now](getting-started){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 } [View it on GitHub](https://github.com/PROxZIMA/DarkSpider/){: .btn .fs-5 .mb-4 .mb-md-0 }

{: .warning }
> Crawling is not illegal, but violating copyright is. It’s always best to double check a website’s T&C before crawling them. Some websites set up what’s called `robots.txt` to tell crawlers not to visit those pages. This crawler will allow you to go around this, but we always recommend respecting `robots.txt`.

{: .note-title }
> **Keep in mind**
>
> Extracting and crawling through TOR network take some time. That's normal behaviour; you can find more information [here](https://support.torproject.org/relay-operators/why-is-my-relay-slow/).

## What makes it simple?

With a single argument you can read a .onion webpage or a regular one through TOR Network and using pipes you can pass the output to any other tool you prefer.

```shell
$ python darkspider.py -u http://github.com/ | grep 'google-site-verification'
    <meta name="google-site-verification" content="xxxx">
```

If you want to crawl the links of a webpage use the `-c` and you will get a folder with all the extracted links. You can even use `-d` to crawl them and so on. As far, there is also the necessary argument `-p` to wait some seconds before the next crawl.

```shell
$ python darkspider.py -v -u http://github.com/ -c -d 2 -p 2
[ DEBUG ] TOR is ready!
[ DEBUG ] Your IP: XXX.XXX.XXX.XXX :: Tor Connection: True
[ DEBUG ] URL :: http://github.com
[ DEBUG ] Folder created :: github.com
[ INFO  ] Crawler started from http://github.com with 2 depth, 2.0 seconds delay and using 16 Threads. Excluding 'None' links.
[ INFO  ] Step 1 completed :: 87 result(s)
[ INFO  ] Step 2 completed :: 4228 result(s)
[ INFO  ] Network Structure created :: github.com/network_structure.json
```

{: .note }
> Output in Readme is trimmed for better readability. General verbose output in log file is much detailed.
```sh
$ python darkspider.py -v -u https://thehiddenwiki.org/ -c -d 1 -p 1 -y 0 -t 32
>
2022-10-12 01:37:50 | DEBUG | checker.py:88 | TOR is ready!
2022-10-12 01:37:54 | DEBUG | checker.py:129 | Your IP: 185.246.188.60 :: Tor Connection: True
2022-10-12 01:37:54 | DEBUG | checker.py:134 | URL :: https://thehiddenwiki.org/
2022-10-12 01:37:54 | DEBUG | darkspider.py:296 | Folder created :: thehiddenwiki.org
2022-10-12 01:37:54 | INFO  | crawler.py:204 | Crawler started from https://thehiddenwiki.org with 1 depth, 1.0 second delay and using 32 Threads. Excluding 'None' links.
2022-10-12 01:37:56 | DEBUG | crawler.py:227 | https://thehiddenwiki.org :: 200
2022-10-12 01:37:56 | INFO  | crawler.py:248 | Step 1 completed :: 106 result(s)
2022-10-12 01:37:57 | INFO  | darkspider.py:311 | Network Structure created :: thehiddenwiki.org/network_structure.json
```
>
