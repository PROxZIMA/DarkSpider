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

- [`Neo4j`](https://neo4j.com/) :: For desktop app, see the [official installation](https://neo4j.com/download-center/#desktop) docs
    - Open Neo4j desktop application.
    - New > Create project > Add > Local DBMS > Enter password `<<password>>` > Create > Start
    - Wait for the database to start then open the Neo4j Browser.
    - Run `:server status` and note down `<<user>>` and `<<server_uri>>`.
    - Create a new `.env` file in the root the project directory with the following content.

    ```
    NEO4J_SERVER=server_uri
    NEO4J_USER=user
    NEO4J_PASSWORD=password
    ```

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
$ sudo apt install tor
```

# Arguments

Args | Long | Description
|:---|:-----|:-----------|
**General** | | Configuration options for the crawler
`-h` |`--help`| Show this help message and exit
`-g` |`--gui`| Open with GUI backend.
`-v` |`--verbose`| Show more information about the progress
`-w` |`--without`| Without the use of Relay TOR
`-n Port number` |`--port Port number`| Port number of TOR Socks Proxy (default: 9050)
`-f Folder` |`--folder Folder`| The root directory which will contain the generated files
`-t Threads` |`--thread Threads`| How many pages to visit (Threads) at the same time (Default: 16)
`-l` |`--log`| A log will let you see which URLs were visited and their response code (Default: True)
**Extract** | | Arguments for the Extractor module
`-i Input file` |`--input Input file`| Input file with URL(s) (separated by line)
`-e` |`--extract`| Extract page's code to terminal or file. (Default: Terminal)
`-o Output` |`--output Output`| Output page(s) to file(s) (for one page)
`-y 0|1` |`--yara 0|1`| Check for keywords and only scrape documents that contain a match. 0 search whole html object. 1 search only the text. (Default: None).
**Crawl** | | Arguments for the Crawler module
`-u Seed URL` |`--url Seed URL`| URL of Webpage to crawl or extract
`-c` |`--crawl`| Crawl website (Default output on /links.txt)
`-d Depth` |`--depth Depth`| Set depth of crawl's travel (Default: 1)
`-p Pause` |`--pause Pause`| The length of time the crawler will pause (Default: 1 second)
`-z Exclusion regex` |`--exclusion Exclusion regex`| Regex path that is ignored while crawling (Default: None)
`-x` |`--external`| Exclude external links while crawling a webpage (Default: include all links)
**Visualize** | | Arguments for the Visualize module
`-s` |`--visualize`| Visualize the graphs and insights from the crawled data
