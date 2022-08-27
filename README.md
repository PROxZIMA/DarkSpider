<!--
  Title: DarkSpider
  Description: a python script to crawl and extract (regular or onion) webpages through TOR network.
  Author: MikeMeliz
  -->
# DarkSpider

[![Version](https://img.shields.io/badge/version-1.2-green.svg?style=plastic)]() [![Python](https://img.shields.io/badge/python-v3-blue.svg?style=plastic)]() [![license](https://img.shields.io/github/license/PROxZIMA/DarkSpider.svg?style=plastic)]()

## Basic Information:
DarkSpider is a python script to crawl and extract (regular or onion) webpages through TOR network.

- **Warning:** Crawling is not illegal, but violating copyright is. It’s always best to double check a website’s T&C before crawling them. Some websites set up what’s called robots.txt to tell crawlers not to visit those pages. This crawler will allow you to go around this, but we always recommend respecting robots.txt.
- **Keep in mind:** Extracting and crawling through TOR network take some time. That's normal behaviour; you can find more information [here](https://www.torproject.org/docs/faq.html.en#WhySlow).

### What makes it simple?

With a single argument you can read an .onion webpage or a regular one through TOR Network and using pipes you can pass the output at any other tool you prefer.

```shell
$ torcrawl -u http://www.github.com/ | grep 'google-analytics'
    <meta-name="google-analytics" content="UA-XXXXXX- ">
```

If you want to crawl the links of a webpage use the `-c` and you got on a file all the inside links. You can even use `-d` to crawl them and so on. As far, there is also the necessary argument `-p` to wait some seconds before the next crawl.

```shell
$ torcrawl -v -u http://www.github.com/ -c -d 2 -p 2
# TOR is ready!
# URL: http://www.github.com/
# Your IP: XXX.XXX.XXX.XXX
# Crawler started from http://www.github.com/ with 2 depth crawl and 2 second(s) delay:
# Step 1 completed with: 11 results
# Step 2 completed with: 112 results
# File created on /path/to/project/links.txt
```

## Installation:
To install this script, you need to clone that repository:

`git clone https://github.com/PROxZIMA/DarkSpider.git`

You'll also need to install dependecies:

`pip install -r requirements.txt`

Of course, the TOR Hidden Service is needed:

Debian/Ubuntu: `apt-get install tor`
[(for more distros and instructions)](https://www.torproject.org/docs/)

## Arguments:
arg | Long | Description
----|------|------------
**General**: | |
-h  |--help| Help
-g  |--gui| Open with GUI backend.
-v  |--verbose| Show more informations about the progress
-u  |--url *.onion| URL of Webpage to crawl or extract
-w  |--without| Without the use of Relay TOR
-f  |--folder| The directory which will contain the generated files ([@guyo13](https://www.github.com/guyo13))
-s  |--visualize| Visualize the graphs and insights from the crawled data
**Extract**: | |
-e  |--extract| Extract page's code to terminal or file. (Default: Terminal)
-i  |--input filename| Input file with URL(s) (seperated by line)
-o  |--output [filename]| Output page(s) to file(s) (for one page)
-y  |--yara | Perform yara keyword search (0 = search entire html object. 1 = search only text).
**Crawl**: | |
-c  |--crawl| Crawl website (Default output on /links.txt)
-d  |--cdepth| Set depth of crawl's travel (Default: 1)
-z  |--exclusion| Regex path that is ignored while crawling (Default: None)
-p  |--pause| The length of time the crawler will pause (Default: 0)
-l  |--log| Log file with visited URLs and their response code
-x  |--external| Exclude external links while crawling a webpage (Default: include all links)

## Usage:

### As Extractor:
To just extract a single webpage to terminal:

```shell
$ python torcrawl.py -u http://www.github.com
<!DOCTYPE html>
...
</html>
```

Extract into a file (github.htm) without the use of TOR:

```shell
$ python torcrawl.py -w -u http://www.github.com -o github.htm
## File created on /script/path/github.htm
```

Extract to terminal and find only the line with google-analytics:

```shell
$ python torcrawl.py -u http://www.github.com | grep 'google-analytics'
    <meta name="google-analytics" content="UA-*******-*">
```

Extract to file and find only the line with google-analytics using yara:
```shell
$ python torcrawl.py -v -w -u https://github.com -e -y 0
...
```
**_Note:_** update res/keyword.yar to search for other keywords.
Use ```-y 0``` for raw html searching and ```-y 1``` for text search only.

Extract a set of webpages (imported from file) to terminal:

```shell
$ python torcrawl.py -i links.txt
...
```


### As Crawler:
Crawl the links of the webpage without the use of TOR,
also show verbose output (really helpfull):

```shell
$ python torcrawl.py -v -w -u http://www.github.com/ -c
## URL: http://www.github.com/
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com/ with step 1 and wait 0
## Step 1 completed with: 11 results
## File created on /script/path/links.txt
```

Crawl the webpage with depth 2 (2 clicks) and 5 seconds waiting before crawl the next page:

```shell
$ python torcrawl.py -v -u http://www.github.com/ -c -d 2 -p 5
## TOR is ready!
## URL: http://www.github.com/
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com with step 2 and wait 5
## Step 1 completed with: 11 results
## Step 2 completed with: 112 results
## File created on /script/path/links.txt
```

Crawl the webpage with depth 1 (1 clicks), 1 seconds pause and exclude links that match `.*\.blog`:

```shell
$ python torcrawl.py -v -u http://www.github.com/ -c -d 1 -p 1 -z ".*\.blog"
## TOR is ready!
## URL: http://www.github.com/
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com with step 1 and wait 1. Excluding .*\.blog links.
## Step 1 completed with: 9 results
## File created on /script/path/links.txt
```
### As Both:
You can crawl a page and also extract the webpages into a folder with a single command:

```shell
$ python torcrawl.py -v -u http://www.github.com/ -c -d 2 -p 5 -e
## TOR is ready!
## URL: http://www.github.com/
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com with step 1 and wait 5
## Step 1 completed with: 11 results
## File created on /script/path/FolderName/index.htm
## File created on /script/path/FolderName/projects.html
## ...
```
***Note:*** *The default (and only for now) file for crawler's links is the `links.txt` document. Also, to extract right after the crawl you have to give `-e` argument*

Following the same logic; you can parse all these pages to grep (for example) and search for specific text:

```shell
$ python torcrawl.py -u http://www.github.com/ -c -e | grep '</html>'
</html>
</html>
...
```

### As Both + Keyword Search:
You can crawl a page, perform a keyword search and extract the webpages that match the findings into a folder with a single command:

```shell
$ python torcrawl.py -v -u http://www.github.com/ -c -d 2 -p 5 -e -y 0
## TOR is ready!
## URL: http://www.github.com/
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com with step 1 and wait 5
## Step 1 completed with: 11 results
## File created on /script/path/FolderName/index.htm
## File created on /script/path/FolderName/projects.html
## ...
```

***Note:*** *Update res/keyword.yar to search for other keywords.
Use ```-y 0``` for raw html searching and ```-y 1``` for text search only.*

## Demo:
![peek 2018-12-08 16-11](https://user-images.githubusercontent.com/9204902/49687660-f72f8280-fb0e-11e8-981e-1bbeeac398cc.gif)

## TODO:
- [x] Store links relation in one-to-may json dictionary format
- [ ] Plot the graphical network of the generated json using [`NetworkX`](https://networkx.org/) package.
- [ ] Crawl images and scripts
- [ ] -z, --exclusions  : Paths that you don't want to include
- [ ] -m, --simultaneous: How many pages to visit at the same time

## Credits
- [**@MikeMeliz**](https://github.com/MikeMeliz) for intial [`TorCrawl`](https://github.com/MikeMeliz/TorCrawl.py) codebase
- A. Alharbi et al., "[Exploring the Topological Properties of the Tor Dark Web](https://ieeexplore.ieee.org/document/9340182)", IEEE Access, vol. 9, pp. 21746-21758, 2021.

## Contributors:
Feel free to contribute on this project! Just fork it, make any change on your fork and add a pull request on current branch! Any advice, help or questions would be appreciated :shipit:

## License:
“GPL” stands for “General Public License”. Using the GNU GPL will require that all the released improved versions be free software. [source & more](https://www.gnu.org/licenses/gpl-faq.html)

## Changelog:
```
v1:
    * Initial project setup
```
