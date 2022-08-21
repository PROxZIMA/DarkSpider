import json
import os
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx


class Visualization:
    """Visualize the graphs and insights from the crawled data

    :param json_file: The json file containing the crawled data
    :param out_path: The path to the output directory
    """

    def __init__(self, json_file, out_path):
        self.json_file = json_file

        self.out_path = os.path.join(out_path, "visualization")
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

        with open(self.json_file, "r", encoding="UTF-8") as f:
            self.data = json.load(f)

        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.data.keys())
        for key, value in self.data.items():
            self.G.add_edges_from([key, value] for value in value)

    def visualize(self):
        """Visualization of the graph."""
        nx.draw(
            self.G,
            with_labels=True,
            node_size=150,
            font_size=6,
            node_shape="o",
            node_color="blue",
            edge_color="red",
            alpha=0.4,
            width=2,
        )
        plt.savefig(os.path.join(self.out_path, "graph.png"))

    def indegree(self):
        """Indegree of the graph."""
        indegree = dict(self.G.in_degree())
        return indegree

    def plot_indegree(self):
        """Plot the indegree of the graph."""
        indegree = dict(self.G.in_degree())
        indegree_counter = Counter(indegree.values())
        indegree_values = list(indegree_counter.values())
        indegree_keys = list(indegree_counter.keys())
        plt.scatter(indegree_keys, indegree_values)
        plt.ylabel("No. of Nodes")
        plt.xlabel("Indegree")
        plt.title("Indegree of the graph")
        plt.savefig(os.path.join(self.out_path, "indegree_plot.png"))

    def bar_indegree(self):
        """Bar Graph of the indegree vs percentage of nodes of the graph."""
        indegree = dict(self.G.in_degree())
        indegree_counter = Counter(indegree.values())
        sum1 = sum(indegree_counter.values())
        arr1 = indegree_counter.keys()
        arr2 = [(counter / sum1) * 100 for counter in indegree_counter.values()]
        plt.bar(arr1, arr2, width=0.1, color="blue")
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("Indegree")
        plt.title("Indegree of the graph")
        plt.savefig(os.path.join(self.out_path, "indegree_bar.png"))

    def outdegree(self):
        """Outdegree of the graph."""
        outdegree = dict(self.G.out_degree())
        return outdegree

    def plot_outdegree(self):
        """Plot the outdegree of the graph."""
        outdegree = dict(self.G.out_degree())
        outdegree_counter = Counter(outdegree.values())
        outdegree_values = list(outdegree.values())
        outdegree_keys = list(outdegree.keys())
        plt.scatter(outdegree_keys, outdegree_values)
        plt.ylabel("No. of Nodes")
        plt.xlabel("Outdegree")
        plt.title("Outdegree of the graph")
        plt.savefig(os.path.join(self.out_path, "outdegree_plot.png"))

    def bar_outdegree(self):
        """Bar Graph of the outdegree vs percentage of nodes of the graph."""
        outdegree = dict(self.G.out_degree())
        outdegree_counter = Counter(outdegree.values())
        sum1 = sum(outdegree_counter.values())
        arr1 = outdegree_counter.keys()
        arr2 = [(counter / sum1) * 100 for counter in outdegree_counter.values()]
        plt.bar(arr1, arr2, width=0.1, color="blue")
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("Outdegree")
        plt.title("Outdegree of the graph")
        plt.savefig(os.path.join(self.out_path, "outdegree_bar.png"))

    def bar_eigenvector_centrality(self):
        """Bar Graph of the eigenvector centrality vs percentage of nodes of the graph."""
        eigenvector_centrality = nx.eigenvector_centrality(self.G)
        eigenvector_centrality_counter = Counter(eigenvector_centrality.values())
        sum1 = sum(eigenvector_centrality_counter.values())
        arr1 = eigenvector_centrality_counter.keys()
        arr2 = [
            (counter / sum1) * 100
            for counter in eigenvector_centrality_counter.values()
        ]
        plt.bar(arr1, arr2, width=0.01, color="blue")
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("Eigenvector Centrality")
        plt.title("Eigenvector Centrality of the graph")
        plt.savefig(os.path.join(self.out_path, "eigenvector_centrality_bar.png"))

    def bar_pagerank(self):
        """Bar Graph of the pagerank vs percentage of nodes of the graph."""
        pagerank = nx.pagerank(self.G)
        pagerank_counter = Counter(pagerank.values())
        sum1 = sum(pagerank_counter.values())
        arr1 = pagerank_counter.keys()
        arr2 = [(counter / sum1) * 100 for counter in pagerank_counter.values()]
        plt.bar(arr1, arr2, width=0.001, color="blue")
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("PageRank")
        plt.title("PageRank of the graph")
        plt.savefig(os.path.join(self.out_path, "pagerank_bar.png"))
