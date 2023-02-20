import os
import shutil
import unittest

from modules import Crawler
from modules.checker import extract_domain, folder
from modules.helper import setup_custom_logger
from modules.visualization import Visualization


class TestVisualizationFunctions(unittest.TestCase):
    """Unit test for Visualization module."""

    @classmethod
    def setUpClass(cls):
        """Test Suite Setup."""
        cls._website = "http://info.cern.ch/"
        cls.out_path = folder(os.path.join("test_run", extract_domain(cls._website)), False)
        cls.logger = setup_custom_logger(
            name="testlog",
            filename=None,
            verbose_=False,
            filelog=False,
            argv=None,
        )

        cls.crawler = Crawler(
            website=cls._website,
            proxies=None,
            c_depth=1,
            c_pause=1,
            out_path=cls.out_path,
            external=True,
            exclusion=None,
            thread=1,
            logger=cls.logger,
        )

        cls.crawler.crawl()

        cls.obj = Visualization(
            json_file=os.path.join(cls.out_path, cls.crawler.network_file),
            out_path=cls.out_path,
            logger=cls.logger,
        )

    @classmethod
    def tearDownClass(cls):
        """Test Suite Teardown."""
        # Remove test folder.
        shutil.rmtree(os.path.dirname(cls.out_path), ignore_errors=True)

    def plot(self, _func):
        """Base test function for all the plots."""
        _func()

        output = os.path.join(self.obj.out_path, f"{_func.__name__}.png")
        self.assertTrue(
            os.path.exists(output),
            f"Test Fail:: File: {output} - does not exist",
        )

    def test_indegree_plot(self):
        """Test visualization.indegree_plot function."""
        self.plot(self.obj.indegree_plot)

    def test_indegree_bar(self):
        """Test visualization.indegree_bar function."""
        self.plot(self.obj.indegree_bar)

    def test_outdegree_plot(self):
        """Test visualization.outdegree_plot function."""
        self.plot(self.obj.outdegree_plot)

    def test_outdegree_bar(self):
        """Test visualization.outdegree_bar function."""
        self.plot(self.obj.outdegree_bar)

    def test_eigenvector_centrality_bar(self):
        """Test visualization.eigenvector_centrality_bar function."""
        self.plot(self.obj.eigenvector_centrality_bar)

    def test_pagerank_bar(self):
        """Test visualization.pagerank_bar function."""
        self.plot(self.obj.pagerank_bar)

    def test_visualize(self):
        """Test visualization.visualize function."""
        self.plot(self.obj.visualize)
