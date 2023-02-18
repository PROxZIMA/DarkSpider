---
layout: default
title: As Crawler + Extractor
parent: How to Use
nav_order: 3
---

# As Crawler + Extractor

- You can crawl a page and also extract the webpages into a folder with a single command:

```shell
$ python darkspider.py -v -u http://github.com/ -c -d 1 -p 1 -e
[ DEBUG ] TOR is ready!
[ DEBUG ] Your IP: XXX.XXX.XXX.XXX :: Tor Connection: True
[ DEBUG ] URL :: http://github.com/
[ DEBUG ] Folder created :: github.com
[ INFO  ] Crawler started from http://github.com with 1 depth, 1.0 second delay and using 16 Threads. Excluding 'None' links.
[ INFO  ] Step 1 completed :: 87 result(s)
[ INFO  ] Network Structure created :: github.com/network_structure.json
[ INFO  ] Cinex :: Extracting from github.com/links.txt to github.com/extracted
[ DEBUG ] File created :: github.com/extracted/github.com/collections_.html
...
[ DEBUG ] File created :: github.com/extracted/github.community/_.html
```

{: .note }
> The default (and only for now) file for crawler's links is the `links.txt` document.
> To extract along with crawl `-e` argument is required.

- Following the same logic; you can parse all these pages to grep (for example) and search for specific text:

```shell
$ python darkspider.py -u http://github.com/ -c -e | grep '</html>'
</html>
</html>
...
```
