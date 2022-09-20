import json
import os
import sys
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from matplotlib.ticker import MultipleLocator

from modules.checker import folder
from modules.helper import verbose


class Visualization:
    """Visualize the graphs and insights from the crawled data.

    Attributes:
        json_file: The json file containing the crawled data.
        out_path: The path to the output directory.
        logger: A logger object to log the output.
    """

    def __init__(self, json_file, out_path, logger):
        self.json_file = json_file
        self.logger = logger

        self.out_path = folder(os.path.join(out_path, "visualization"))

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

    def indegree(self):
        """Indegree of the graph."""
        return dict(self.G.in_degree())

    def outdegree(self):
        """Outdegree of the graph."""
        return dict(self.G.out_degree())

    @verbose
    def indegree_plot(self):
        """Scatter Plot of the indegree vs nodes of the graph."""
        indegree = self.indegree()
        indegree_counter = Counter(indegree.values())
        indegree_counter.pop(0, None)
        indegree_values = indegree_counter.values()
        indegree_keys = indegree_counter.keys()
        sns.scatterplot(x=indegree_keys, y=indegree_values, color="orangered")
        plt.ylabel("No. of Nodes")
        plt.xlabel("Indegree")
        plt.title("Indegree of the graph")

    @verbose
    def indegree_bar(self):
        """Bar Graph of the indegree vs percentage of nodes of the graph."""
        indegree = self.indegree()
        indegree_counter = Counter(indegree.values())
        total = sum(indegree_counter.values())

        indegree_keys, indegree_percent = [], []
        for k, v in sorted(indegree_counter.items()):
            indegree_keys.append(k)
            indegree_percent.append((v / total) * 100)

        ax = sns.barplot(x=indegree_keys, y=indegree_percent, color="cornflowerblue")
        ax.set_xlim(-1, min(50, len(indegree_keys)))
        ax.xaxis.set_major_locator(MultipleLocator(base=min(50, max(len(indegree_keys), 5)) // 5))
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("Indegree")
        plt.title("Indegree of the graph")

    @verbose
    def outdegree_plot(self):
        """Scatter Plot of the outdegree vs nodes of the graph."""
        outdegree = self.outdegree()
        outdegree_counter = Counter(outdegree.values())
        outdegree_counter.pop(0, None)
        outdegree_values = outdegree_counter.values()
        outdegree_keys = outdegree_counter.keys()
        sns.scatterplot(x=outdegree_keys, y=outdegree_values, color="limegreen")
        plt.ylabel("No. of Nodes")
        plt.xlabel("Outdegree")
        plt.title("Outdegree of the graph")

    @verbose
    def outdegree_bar(self):
        """Bar Graph of the outdegree vs percentage of nodes of the graph."""
        outdegree = self.outdegree()
        outdegree_counter = Counter(outdegree.values())
        total = sum(outdegree_counter.values())

        outdegree_keys, outdegree_percent = [], []
        for k, v in sorted(outdegree_counter.items()):
            outdegree_keys.append(k)
            outdegree_percent.append((v / total) * 100)

        ax = sns.barplot(x=outdegree_keys, y=outdegree_percent, color="cornflowerblue")
        ax.set_xlim(-1, min(50, len(outdegree_keys)) + 1)
        ax.xaxis.set_major_locator(MultipleLocator(base=min(50, max(len(outdegree_keys), 5)) // 5))
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("Outdegree")
        plt.title("Outdegree of the graph")

    @verbose
    def eigenvector_centrality_bar(self):
        """Bar Graph of the eigenvector centrality vs percentage of nodes of the graph."""
        eigenvector_centrality = nx.eigenvector_centrality(self.G, max_iter=sys.maxsize)
        eigenvector_centrality_counter = Counter(eigenvector_centrality.values())
        total = sum(eigenvector_centrality_counter.values())

        evc_keys, evc_percent = [], []
        for k, v in sorted(eigenvector_centrality_counter.items()):
            evc_keys.append(k)
            evc_percent.append((v / total) * 100)

        ax = sns.barplot(x=evc_keys, y=evc_percent, color="cornflowerblue")
        ax.set_xticklabels(map(lambda x: f"{x:.2E}", evc_keys))
        ax.xaxis.set_major_locator(MultipleLocator(base=max(len(evc_keys), 5) // 5))
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("Eigenvector Centrality")
        plt.title("Eigenvector Centrality of the graph")

    @verbose
    def pagerank_bar(self):
        """Bar Graph of the pagerank vs percentage of nodes of the graph."""
        pagerank = nx.pagerank(self.G)
        pagerank_counter = Counter(pagerank.values())
        total = sum(pagerank_counter.values())

        pagerank_keys, pagerank_percent = [], []
        for k, v in sorted(pagerank_counter.items()):
            pagerank_keys.append(k)
            pagerank_percent.append((v / total) * 100)

        ax = sns.barplot(x=pagerank_keys, y=pagerank_percent, color="cornflowerblue")
        ax.set_xticklabels(map(lambda x: f"{x:.2E}", pagerank_keys))
        ax.xaxis.set_major_locator(MultipleLocator(base=max(len(pagerank_keys), 5) // 5))
        plt.ylabel("Percentage of Nodes")
        plt.xlabel("PageRank")
        plt.title("PageRank of the graph")
