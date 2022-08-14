from turtle import width
import extractor
import crawler
import json
import networkx as nx
from collections import Counter
import matplotlib.pyplot as plt

class visualize_json:
    def __init__(self, json_file):
        self.json_file = json_file
        self.data = json.load(open(self.json_file))
        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.data.keys())
        for key,value in self.data.items():
            self.G.add_edges_from([key,value]for value in value)

    
    def visualize(self):
        """Visualization of the graph."""
        
        nx.draw(self.G, with_labels=True,node_size=150,font_size=6,node_shape="o",node_color='blue',edge_color='red',alpha=0.4,width=2)
        plt.savefig('graph.png')
        plt.show()


    def indegree(self):
        """Indegree of the graph."""
        indegree =dict(self.G.in_degree())
        return indegree


    def plot_indegree(self):
        """Plot the indegree of the graph."""
        indegree = dict(self.G.in_degree())
        indegree_counter = Counter(indegree.values())
        indegree_values = list(indegree_counter.values())
        indegree_keys = list(indegree_counter.keys())
        plt.scatter(indegree_keys,indegree_values)
        plt.ylabel('No. of Nodes')
        plt.xlabel('Indegree')
        plt.title('Indegree of the graph')
        plt.savefig('indegree_plot.png')
        plt.show()


    def bar_indegree(self):
        """Bar Graph of the indegree vs percentage of nodes of the graph."""
        indegree = dict(self.G.in_degree())
        indegree_counter = Counter(indegree.values())
        sum1=0
        arr1=[]
        arr2=[]
        for i in indegree_counter.values():
            sum1=sum1+i
        for i in indegree_counter.keys():
            arr1.append(i)
            arr2.append((indegree_counter[i]/sum1)*100)
        plt.bar(arr1,arr2,width=0.1,color='blue')
        plt.ylabel('Percentage of Nodes')
        plt.xlabel('Indegree')
        plt.title('Indegree of the graph')
        plt.savefig('indegree_bar.png')
        plt.show()
        


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
        plt.scatter(outdegree_keys,outdegree_values)
        plt.ylabel('No. of Nodes')
        plt.xlabel('Outdegree')
        plt.title('Outdegree of the graph')
        plt.savefig('outdegree_plot.png')
        plt.show()
        

    def bar_outdegree(self):
        """Bar Graph of the outdegree vs percentage of nodes of the graph."""
        outdegree = dict(self.G.out_degree())
        outdegree_counter = Counter(outdegree.values())
        sum1=0
        arr1=[]
        arr2=[]
        for i in outdegree_counter.values():
            sum1=sum1+i
        for i in outdegree_counter.keys():
            arr1.append(i)
            arr2.append((outdegree_counter[i]/sum1)*100)
        plt.bar(arr1,arr2,width=0.1,color='blue')
        plt.ylabel('Percentage of Nodes')
        plt.xlabel('Outdegree')
        plt.title('Outdegree of the graph')
        plt.savefig('outdegree_bar.png')
        plt.show()

    def bar_eigenvector_centrality(self):
        """Bar Graph of the eigenvector centrality vs percentage of nodes of the graph."""
        eigenvector_centrality = nx.eigenvector_centrality(self.G)
        eigenvector_centrality_counter = Counter(eigenvector_centrality.values())
        sum1=0
        arr1=[]
        arr2=[]
        for i in eigenvector_centrality_counter.values():
            sum1=sum1+i
        for i in eigenvector_centrality_counter.keys():
            arr1.append(i)
            arr2.append((eigenvector_centrality_counter[i]/sum1)*100)
        plt.bar(arr1,arr2,width=0.01,color='blue')
        plt.ylabel('Percentage of Nodes')
        plt.xlabel('Eigenvector Centrality')
        plt.title('Eigenvector Centrality of the graph')
        plt.savefig('eigenvector_centrality_bar.png')
        plt.show()
    
    def bar_pagerank(self):
        """Bar Graph of the pagerank vs percentage of nodes of the graph."""
        pagerank = nx.pagerank(self.G)
        pagerank_counter = Counter(pagerank.values())
        sum1=0
        arr1=[]
        arr2=[]
        for i in pagerank_counter.values():
            sum1=sum1+i
        for i in pagerank_counter.keys():
            arr1.append(i)
            arr2.append((pagerank_counter[i]/sum1)*100)
        plt.bar(arr1,arr2,width=0.001,color='blue')
        plt.ylabel('Percentage of Nodes')
        plt.xlabel('PageRank')
        plt.title('PageRank of the graph')
        plt.savefig('pagerank_bar.png')
        plt.show()
        
obj = visualize_json("demo.json")
obj.bar_outdegree()
obj.plot_outdegree()
obj.bar_indegree()
obj.plot_indegree()
obj.visualize()
obj.bar_eigenvector_centrality()
obj.bar_pagerank()


