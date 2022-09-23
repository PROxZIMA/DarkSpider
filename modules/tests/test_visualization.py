import os
import shutil
import unittest

from modules import Crawler
from modules.checker import extract_domain, folder
from modules.helper import setup_custom_logger
from modules.visualization import Visualization


def test_plots(self, _func):
    """Base test function for all the plots."""
    _func()

    output = os.path.join(self.obj.out_path, f"{_func.__name__}.png")
    self.assertTrue(
        os.path.exists(output),
        f"Test Fail:: File: {output} - does not exist",
    )


class TestVisualizationFunctions(unittest.TestCase):
    """Unit test for Visualization module."""

    @classmethod
    def setUpClass(cls):
        """Test Suite Setup."""
        cls._website = "http://info.cern.ch/"
        cls.out_path = out_path = folder(extract_domain(cls._website), False)
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
            out_path=out_path,
            external=True,
            exclusion=None,
            thread=1,
            logger=cls.logger,
        )

        cls.crawler.crawl()

        cls.obj = Visualization(
            json_file=os.path.join(out_path, cls.crawler.network_file),
            out_path=out_path,
            logger=cls.logger,
        )

    @classmethod
    def tearDownClass(cls):
        """Test Suite Teardown."""
        # Remove test folder.
        shutil.rmtree(cls.out_path)

    def test_indegree_plot(self):
        """Test visualization.indegree_plot function."""
        test_plots(self, self.obj.indegree_plot)

    def test_indegree_bar(self):
        """Test visualization.indegree_bar function."""
        test_plots(self, self.obj.indegree_bar)

    def test_outdegree_plot(self):
        """Test visualization.outdegree_plot function."""
        test_plots(self, self.obj.outdegree_plot)

    def test_outdegree_bar(self):
        """Test visualization.outdegree_bar function."""
        test_plots(self, self.obj.outdegree_bar)

    def test_eigenvector_centrality_bar(self):
        """Test visualization.eigenvector_centrality_bar function."""
        test_plots(self, self.obj.eigenvector_centrality_bar)

    def test_pagerank_bar(self):
        """Test visualization.pagerank_bar function."""
        test_plots(self, self.obj.pagerank_bar)

    def test_visualize(self):
        """Test visualization.visualize function."""
        test_plots(self, self.obj.visualize)
