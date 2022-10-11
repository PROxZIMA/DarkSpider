---
layout: default
title: As Crawler
parent: How to Use
nav_order: 2
---

# As Crawler

- Crawl the links of the webpage without the use of TOR, also show verbose output (really helpful):

```shell
$ python darkspider.py -v -w -u http://github.com/ -c
[ DEBUG ] Your IP: XXX.XXX.XXX.XXX :: Tor Connection: False
[ DEBUG ] URL :: http://github.com/
[ DEBUG ] Folder created :: github.com
[ INFO  ] Crawler started from http://github.com with 1 depth, 0 seconds delay and using 16 Threads. Excluding 'None' links.
[ INFO  ] Step 1 completed :: 87 result(s)
[ INFO  ] Network Structure created :: github.com/network_structure.json
```

- Crawl the webpage with depth 2 (2 clicks) and 5 seconds waiting before crawl the next page:

```shell
$ python darkspider.py -v -u http://github.com/ -c -d 2 -p 5
[ DEBUG ] TOR is ready!
[ DEBUG ] Your IP: XXX.XXX.XXX.XXX :: Tor Connection: True
[ DEBUG ] URL :: http://github.com
[ DEBUG ] Folder created :: github.com
[ INFO  ] Crawler started from http://github.com with 2 depth, 5.0 seconds delay and using 16 Threads. Excluding 'None' links.
[ INFO  ] Step 1 completed :: 87 result(s)
[ INFO  ] Step 2 completed :: 4228 result(s)
[ INFO  ] Network Structure created :: github.com/network_structure.json
```

- Crawl the webpage with depth 1 (1 clicks), 1 seconds pause and exclude links that match `.*\.blog`:

```shell
$ python darkspider.py -v -u http://github.com/ -c -d 1 -p 1 -z ".*\.blog"
[ DEBUG ] TOR is ready!
[ DEBUG ] Your IP: XXX.XXX.XXX.XXX :: Tor Connection: True
[ DEBUG ] URL :: http://github.com/
[ DEBUG ] Folder created :: github.com
[ INFO  ] Crawler started from http://github.com with 1 depth, 1.0 second delay and using 16 Threads. Excluding '.*\.blog' links.
[ INFO  ] Step 1 completed :: 85 result(s)
[ INFO  ] Network Structure created :: github.com/network_structure.json
```
