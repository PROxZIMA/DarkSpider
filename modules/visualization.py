import json
import os
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx


def verbose(func):
    """Verbose decorator"""

    def wrapper(*args, **kwargs):
        if args[0].verbose:
            print(f"## {func.__doc__}...")
        plt.cla()
        plt.grid()
        return func(*args, **kwargs)

    return wrapper


class Visualization:
    """Visualize the graphs and insights from the crawled data

    :param json_file: The json file containing the crawled data
    :param out_path: The path to the output directory
    :param verbose: Whether to print the output or not
    """

    def __init__(self, json_file, out_path, verbose):
        self.json_file = json_file
        self.verbose = verbose

        self.out_path = os.path.join(out_path, "visualization")
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

        with open(self.json_file, "r", encoding="UTF-8") as f:
            self.data = json.load(f)

        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.data.keys())
        for key, value in self.data.items():
            self.G.add_edges_from([key, val] for val in value)

    @verbose
    def visualize(self):
        """Visualization of the graph."""
        nx.draw(
            self.G,
            with_labels=False,
            node_size=5,
            font_size=6,
            node_shape="o",
            node_color="blue",
            edge_color="red",
            alpha=0.4,
            width=0.5,
        )
        plt.savefig(os.path.join(self.out_path, "graph.png"))

    def indegree(self):
        """Indegree of the graph."""
        return dict(self.G.in_degree())

    def outdegree(self):
        """Outdegree of the graph."""
        return dict(self.G.out_degree())

    @verbose
    def plot_indegree(self):
        """Scatter Plot of the indegree vs nodes of the graph."""
        indegree = self.indegree()
        indegree_counter = Counter(indegree.values())
        indegree_counter.pop(0, None)
        indegree_values = indegree_counter.values()
        indegree_keys = indegree_counter.keys()
        plt.scatter(indegree_keys, indegree_values, color="red")
        plt.ylabel("No. of Nodes")
        plt.xlabel("Indegree")
        plt.title("Indegree of the graph")
        plt.savefig(os.path.join(self.out_path, "indegree_plot.png"))

    @verbose
    def bar_indegree(self):
        """Bar Graph of the indegree vs percentage of nodes of the graph."""
        indegree = self.indegree()
        indegree_counter = Counter(indegree.values())
        total = sum(indegree_counter.values())
        indegree_keys = indegree_counter.keys()
        indegree_percent = [
            (counter / total) * 100 for counter in indegree_counter.values()
        ]
        plt.bar(indegree_keys, indegree_percent, width=0.1, color="blue")
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("Indegree")
        plt.title("Indegree of the graph")
        plt.savefig(os.path.join(self.out_path, "indegree_bar.png"))

    @verbose
    def plot_outdegree(self):
        """Scatter Plot of the outdegree vs nodes of the graph."""
        outdegree = self.outdegree()
        outdegree_counter = Counter(outdegree.values())
        outdegree_counter.pop(0, None)
        outdegree_values = outdegree_counter.values()
        outdegree_keys = outdegree_counter.keys()
        plt.scatter(outdegree_keys, outdegree_values, color="red")
        plt.ylabel("No. of Nodes")
        plt.xlabel("Outdegree")
        plt.title("Outdegree of the graph")
        plt.savefig(os.path.join(self.out_path, "outdegree_plot.png"))

    @verbose
    def bar_outdegree(self):
        """Bar Graph of the outdegree vs percentage of nodes of the graph."""
        outdegree = self.outdegree()
        outdegree_counter = Counter(outdegree.values())
        total = sum(outdegree_counter.values())
        outdegree_keys = outdegree_counter.keys()
        outdegree_percent = [
            (counter / total) * 100 for counter in outdegree_counter.values()
        ]
        plt.bar(outdegree_keys, outdegree_percent, width=10, color="blue")
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("Outdegree")
        plt.title("Outdegree of the graph")
        plt.savefig(os.path.join(self.out_path, "outdegree_bar.png"))

    @verbose
    def bar_eigenvector_centrality(self):
        """Bar Graph of the eigenvector centrality vs percentage of nodes of the graph."""
        eigenvector_centrality = nx.eigenvector_centrality(self.G)
        eigenvector_centrality_counter = Counter(eigenvector_centrality.values())
        total = sum(eigenvector_centrality_counter.values())
        evc_keys = eigenvector_centrality_counter.keys()
        evc_percent = [
            (counter / total) * 100
            for counter in eigenvector_centrality_counter.values()
        ]
        plt.bar(evc_keys, evc_percent, width=0.01, color="blue")
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("Eigenvector Centrality")
        plt.title("Eigenvector Centrality of the graph")
        plt.savefig(os.path.join(self.out_path, "eigenvector_centrality_bar.png"))

    @verbose
    def bar_pagerank(self):
        """Bar Graph of the pagerank vs percentage of nodes of the graph."""
        pagerank = nx.pagerank(self.G)
        pagerank_counter = Counter(pagerank.values())
        total = sum(pagerank_counter.values())
        pagerank_keys = pagerank_counter.keys()
        pagerank_percent = [
            (counter / total) * 100 for counter in pagerank_counter.values()
        ]
        plt.bar(pagerank_keys, pagerank_percent, width=0.001, color="blue")
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("PageRank")
        plt.title("PageRank of the graph")
        plt.savefig(os.path.join(self.out_path, "pagerank_bar.png"))
