---
layout: default
title: As Crawler + Extractor + Keyword Search
parent: How to Use
nav_order: 4
---

# As Crawler + Extractor + Keyword Search

- You can crawl a page, perform a keyword search and extract the webpages that match the findings into a folder with a single command:

```shell
$ python darkspider.py -v -u http://github.com/ -o github.html -y 0
[ DEBUG ] TOR is ready!
[ DEBUG ] Your IP: XXX.XXX.XXX.XXX :: Tor Connection: True
[ DEBUG ] URL :: http://github.com/
[ DEBUG ] Folder created :: github.com
[ INFO  ] Outex :: Extracting http://github.com to github.com/github.html
[ DEBUG ] http://github.com :: Yara match found!
```
