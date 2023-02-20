---
layout: default
title: As Extractor
parent: How to Use
nav_order: 1
---

# As Extractor

{: .note }
> Extractor takes maximum file name length under consideration and creates sub-directories based on the url.
>
> `http://a.com/b.ext?x=&y=$%z2` -> `a.com/b.extxyz2_.html` (`a.com` folder with `b.extxyz2_.html` file in it)

- To just extract a single webpage to terminal:

```shell
$ python darkspider.py -u http://github.com/
## Termex :: Extracting http://github.com to terminal
## http://github.com ::
<!DOCTYPE html>
...
</html>
```

- Extract into a file (github.html) without the use of TOR:

```shell
$ python darkspider.py -w -u http://github.com -o github.html
## Outex :: Extracting http://github.com to github.com/github.html
```

- Extract to terminal and find only the line with google-site-verification:

```shell
$ python darkspider.py -u http://github.com/ | grep 'google-site-verification'
    <meta name="google-site-verification" content="xxxx">
```

- Extract to file and find only the line with google-site-verification using `yara`:

```shell
$ python darkspider.py -v -w -u https://github.com -e -y 0
...
```

{: .note }
> Update `res/keyword.yar` to search for other keywords.
> Use `-y 0` for raw html searching and `-y 1` for text search only.

- Extract a set of webpages (imported from file) to a folder:

```shell
$ python darkspider.py -i links.txt -f links_output
...
```
