<!--
  Title: DarkSpider
  Description: a python script to crawl and extract (regular or onion) webpages through TOR network.
  Author: PROxZIMA
  -->
# DarkSpider

[![Version](https://img.shields.io/badge/version-2.0.0-green.svg?style=plastic)]() [![Python](https://img.shields.io/badge/python-v3-blue.svg?style=plastic)]() [![license](https://img.shields.io/github/license/PROxZIMA/DarkSpider.svg?style=plastic)]()

## Basic Information:
DarkSpider is a python script to crawl and extract (regular or onion) webpages through TOR network.

> **Warning**
>
> Crawling is not illegal, but violating copyright is. It’s always best to double check a website’s T&C before crawling them. Some websites set up what’s called `robots.txt` to tell crawlers not to visit those pages. This crawler will allow you to go around this, but we always recommend respecting `robots.txt`.

> **Keep in mind**
>
> Extracting and crawling through TOR network take some time. That's normal behaviour; you can find more information [here](https://support.torproject.org/relay-operators/why-is-my-relay-slow/).

### What makes it simple?

With a single argument you can read an .onion webpage or a regular one through TOR Network and using pipes you can pass the output at any other tool you prefer.

```shell
$ python darkspider.py -u http://github.com/ | grep 'google-site-verification'
    <meta name="google-site-verification" content="xxxx">
```

If you want to crawl the links of a webpage use the `-c` and you will get a folder all the extracted links. You can even use `-d` to crawl them and so on. As far, there is also the necessary argument `-p` to wait some seconds before the next crawl.

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

## Installation:
To install this script, you need to clone that repository:

`git clone https://github.com/PROxZIMA/DarkSpider.git`

You'll also need to install dependencies:

`pip install -r requirements.txt`

Of course, the TOR Hidden Service is needed:

Debian/Ubuntu: `apt-get install tor`
[(for more distros and instructions)](https://www.torproject.org/docs/)

## Arguments:
Args | Long | Description
----|------|------------
**General**: | |
`-h` |`--help`| Help
`-g` |`--gui`| Open with GUI backend.
`-v` |`--verbose`| Show more information about the progress
`-u` |`--url *.onion`| URL of Webpage to crawl or extract
`-w` |`--without`| Without the use of Relay TOR
`-n` |`--port number`| Port number of TOR Socks Proxy (default: 9050)
`-f` |`--folder`| The directory which will contain the generated files
`-s` |`--visualize`| Visualize the graphs and insights from the crawled data
**Extract**: | |
`-e` |`--extract`| Extract page's code to terminal or file. (Default: Terminal)
`-i` |`--input filename`| Input file with URL(s) (separated by line)
`-o` |`--output filename`| Output page(s) to file(s) (for one page)
`-y` |`--yara 0\|1`| Perform yara keyword search (0 = search entire html object. 1 = search only text).
**Crawl**: | |
`-c` |`--crawl`| Crawl website (Default output on /links.txt)
`-d` |`--cdepth`| Set depth of crawl's travel (Default: 1)
`-z` |`--exclusion regexp`| Regex path that is ignored while crawling (Default: None)
`-t` |`--thread number`| How many pages to visit (Threads) at the same time (Default: 16)
`-p` |`--pause`| The length of time the crawler will pause (Default: 0)
`-l` |`--log`| Log file with visited URLs and their response code
`-x` |`--external`| Exclude external links while crawling a webpage (Default: include all links)

## Usage:

### As Extractor:

> **Note**
>
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

> **Note**
>
> Update `res/keyword.yar` to search for other keywords.
> Use `-y 0` for raw html searching and `-y 1` for text search only.

- Extract a set of webpages (imported from file) to a folder:

```shell
$ python darkspider.py -i links.txt -f links_output
...
```

### As Crawler:
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

### As Crawler + Extractor:
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

> **Note**
>
> The default (and only for now) file for crawler's links is the `links.txt` document.
> To extract along with crawl `-e` argument is required.

- Following the same logic; you can parse all these pages to grep (for example) and search for specific text:

```shell
$ python darkspider.py -u http://github.com/ -c -e | grep '</html>'
</html>
</html>
...
```

### As Crawler + Extractor + Keyword Search:
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

### Visualization of the Network Structure:
- Provide `-s` argument to create graphs to gain [insights](https://github.com/PROxZIMA/DarkSpider/pull/13) from the generated data,

```shell
$ python darkspider.py -u "http://github.com/" -c -d 2 -p 1 -t 32 -s
## Crawler started from http://github.com with 2 depth, 1.0 second delay and using 32 Threads. Excluding 'None' links.
## Step 1 completed :: 87 result(s)
## Step 2 completed :: 4508 result(s)
## Network Structure created :: github.com/network_structure.json
## Generating :: Scatter Plot of the indegree vs nodes of the graph...
## Generating :: Bar Graph of the indegree vs percentage of nodes of the graph...
## Generating :: Scatter Plot of the outdegree vs nodes of the graph...
## Generating :: Bar Graph of the outdegree vs percentage of nodes of the graph...
## Generating :: Bar Graph of the eigenvector centrality vs percentage of nodes of the graph...
## Generating :: Bar Graph of the pagerank vs percentage of nodes of the graph...
## Generating :: Visualization of the graph...
```

## Testing:
- Test cases must be updated as we don't want any unexpected exception to pop-up in-between long runs.
- Before creating a PR make sure to run all the test cases.

```bash
$ python3 -m unittest -b
```
- Or a module specific test cases using

```bash
$ python3 -m unittest modules.tests.test_crawler -b
```
---
> **Note**
>
> Output in Readme is trimmed for better readability. General [verbose output](./assets/logging.png) is much detailed.

## Credits:
- [**@MikeMeliz**](https://github.com/MikeMeliz) for initial [`TorCrawl`](https://github.com/MikeMeliz/TorCrawl.py) codebase
- A. Alharbi et al., "[Exploring the Topological Properties of the Tor Dark Web](https://ieeexplore.ieee.org/document/9340182)", IEEE Access, vol. 9, pp. 21746-21758, 2021.

## Contributing:
- Feel free to contribute on this project! Just fork it, make any change on your fork and add a pull request on current branch! Any advice, help or questions would be appreciated :shipit:

[![Contributors](https://contrib.rocks/image?repo=PROxZIMA/DarkSpider "Contributors")](https://github.com/PROxZIMA/DarkSpider/graphs/contributors)

[![Stats](https://repobeats.axiom.co/api/embed/6bcd62cf68bef8f509296f236f21b39f6af128a6.svg "Repobeats analytics image")](https://github.com/PROxZIMA/DarkSpider/pulse)

## License:
“GPL” stands for “General Public License”. Using the GNU GPL will require that all the released improved versions be free software. [source & more](https://www.gnu.org/licenses/gpl-faq.html)


## Changelog:

    v2.0.0:
#### What's Changed
* Add: Project IEEE citation by @PROxZIMA in https://github.com/PROxZIMA/DarkSpider/pull/8
* Fix: Ignore Gooey installation by default by @PROxZIMA in https://github.com/PROxZIMA/DarkSpider/pull/9
* Add: CLI command to include/exclude external links by @PROxZIMA in https://github.com/PROxZIMA/DarkSpider/pull/11
* Fixed Issue related to Graphical Analysis by @knightster0804 in https://github.com/PROxZIMA/DarkSpider/pull/10
* Revert "Fixed Issue related to Graphical Analysis" by @PROxZIMA in https://github.com/PROxZIMA/DarkSpider/pull/12
* Creating json by @r0nl in https://github.com/PROxZIMA/DarkSpider/pull/14
* Added 'exclusion' Argument by @r0nl in https://github.com/PROxZIMA/DarkSpider/pull/16
* Added required functionalities and Images by @knightster0804 in https://github.com/PROxZIMA/DarkSpider/pull/13
* White box unit test cases for modules by @PROxZIMA in https://github.com/PROxZIMA/DarkSpider/pull/7
* New graphical visualization using `seaborn` library by @PROxZIMA in https://github.com/PROxZIMA/DarkSpider/pull/17
* Added image and script crawler by @ytatiya3 in https://github.com/PROxZIMA/DarkSpider/pull/15
* Crawler multi-threaded implementation by @PROxZIMA in https://github.com/PROxZIMA/DarkSpider/pull/18

#### New Contributors
* @PROxZIMA made their first contribution in https://github.com/PROxZIMA/DarkSpider/pull/8
* @knightster0804 made their first contribution in https://github.com/PROxZIMA/DarkSpider/pull/10
* @r0nl made their first contribution in https://github.com/PROxZIMA/DarkSpider/pull/14
* @ytatiya3 made their first contribution in https://github.com/PROxZIMA/DarkSpider/pull/15

**Full Changelog**: https://github.com/PROxZIMA/DarkSpider/compare/1.0.0...2.0.1

    v1.0.0:
* Initial project setup

**Full Changelog**: https://github.com/PROxZIMA/DarkSpider/commits/1.0.0
