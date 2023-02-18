---
layout: default
title: How to Contribute
nav_order: 4
---

# Contributing
- Feel free to contribute on this project! Just fork it, make any change on your fork and add a pull request on current branch! Any advice, help or questions would be appreciated <img src="https://github.githubassets.com/images/icons/emoji/shipit.png" alt=":shipit:" title=":shipit:" width="20px">

[![Contributors](https://contrib.rocks/image?repo=PROxZIMA/DarkSpider "Contributors")](https://github.com/PROxZIMA/DarkSpider/graphs/contributors)

[![Stats](https://repobeats.axiom.co/api/embed/6bcd62cf68bef8f509296f236f21b39f6af128a6.svg "Repobeats analytics image")](https://github.com/PROxZIMA/DarkSpider/pulse)

# Testing
- Test cases must be updated as we don't want any unexpected exception to pop-up in-between long runs.
- Before creating a PR make sure to run all the test cases.

```bash
$ python3 -m unittest -b
```
- Or a module specific test cases using

```bash
$ python3 -m unittest modules.tests.test_crawler -b
```
