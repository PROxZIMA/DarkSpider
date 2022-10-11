---
layout: default
title: Visualization of the Network Structure
parent: How to Use
nav_order: 5
---

# Visualization of the Network Structure
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
