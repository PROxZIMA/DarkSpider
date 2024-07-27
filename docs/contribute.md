---
layout: default
title: How to Contribute
nav_order: 4
---

# Contributing
- Feel free to contribute to this project! Just fork it, make any changes on your fork and add a pull request on the current branch! Any advice, help or questions would be appreciated <img src="https://github.githubassets.com/images/icons/emoji/shipit.png" alt=":shipit:" title=":shipit:" width="20px">

[![Contributors](https://contrib.rocks/image?repo=PROxZIMA/DarkSpider "Contributors")](https://github.com/PROxZIMA/DarkSpider/graphs/contributors)

[![Stats](https://repobeats.axiom.co/api/embed/6bcd62cf68bef8f509296f236f21b39f6af128a6.svg "Repobeats analytics image")](https://github.com/PROxZIMA/DarkSpider/pulse)

## Documentation
- This site uses [Just the Docs](https://github.com/just-the-docs/just-the-docs).
- Install dependencies using

```bash
$ cd docs
$ bundle install
```
- Test locally using

```bash
$ cd docs
$ bundle exec jekyll serve -c _config_dev.yml --livereload --open-url
```

## Testing
- Test cases must be updated as we don't want any unexpected exceptions to pop up in between long runs.
- Install `pytest` and `coverage`.

```bash
$ pip install -r requirements_dev.txt
```
- Module-specific test case using

```bash
$ pytest -q --tb=short modules/tests/test_extractor.py::TestCheckerFunctions::test_outex_002
```
- Before committing, make sure to run all the test cases.

```bash
$ coverage run -m pytest -q --tb=short modules/tests/
```
- Check code coverage

```bash
$ coverage report -m
$ coverage html
```
