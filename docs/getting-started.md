---
layout: default
title: Getting Started
nav_order: 2
---

# Installation

To install this script, you need to clone the repository:

```shell
$ git clone https://github.com/PROxZIMA/DarkSpider.git
```

### Dependencies
You'll also need to install dependencies:

- [`wxPython`](https://wxpython.org/) :: For Linux, see the [official installation](https://wxpython.org/pages/downloads/index.html) docs

```shell
$ pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04 wxPython
```

- [`yara`](https://virustotal.github.io/yara/) :: See the [official installation](https://yara.readthedocs.io/en/stable/gettingstarted.html) docs

- Project requirements

```shell
$ pip install -r requirements.txt
```

### TOR
The TOR Hidden Service is needed [(for more distros and instructions)](https://www.torproject.org/download/):

Debian/Ubuntu:

```shell
$ apt install tor
```

# Arguments

Args | Long | Description
|:---|:-----|:-----------|
**General** | |
`-h` |`--help`| Help
`-g` |`--gui`| Open with GUI backend.
`-v` |`--verbose`| Show more information about the progress
`-u` |`--url *.onion`| URL of Webpage to crawl or extract
`-w` |`--without`| Without the use of Relay TOR
`-n` |`--port number`| Port number of TOR Socks Proxy (default: 9050)
`-f` |`--folder`| The directory which will contain the generated files
`-s` |`--visualize`| Visualize the graphs and insights from the crawled data
**Extract** | |
`-e` |`--extract`| Extract page's code to terminal or file. (Default: Terminal)
`-i` |`--input filename`| Input file with URL(s) (separated by line)
`-o` |`--output filename`| Output page(s) to file(s) (for one page)
`-y` |`--yara 0\|1`| Perform yara keyword search (0 = search entire html object. 1 = search only text).
**Crawl** | |
`-c` |`--crawl`| Crawl website (Default output on /links.txt)
`-d` |`--cdepth`| Set depth of crawl's travel (Default: 1)
`-z` |`--exclusion regexp`| Regex path that is ignored while crawling (Default: None)
`-t` |`--thread number`| How many pages to visit (Threads) at the same time (Default: 16)
`-p` |`--pause`| The length of time the crawler will pause (Default: 0)
`-l` |`--log`| Log file with visited URLs and their response code
`-x` |`--external`| Exclude external links while crawling a webpage (Default: include all links)
