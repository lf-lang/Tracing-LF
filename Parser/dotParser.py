#!/usr/bin/env python3

import networkx as nx
from networkx.algorithms.shortest_paths.generic import shortest_path
import pydot 
import matplotlib.pyplot as plt


class parse_dot:
    """ Deprecated. \n
        Can be used to parse dotfiles generated from LF programs (currently only in the C++ target) with the 'export-dependency-graph' option set to true. \n
        Allows parsing of the dotfile, getting the level of each node and plotting the dependecy graph of the reactions"""
    
    def __init__(self, filename):
        self.filename = filename
        self.graph = nx.DiGraph
    
    
    def parse_graph_from_dot(self):                
        # Parse Graph from file
        graph = pydot.graph_from_dot_file(self.filename)

        # Conversion from pydot (had problems with reading dot graphs using networkx)
        # Edges are resversed such that edges run from the source node to those that are dependent upon them
        G = nx.DiGraph(nx.nx_pydot.from_pydot(graph[0])).reverse()
        
        # Set the graph 
        self.graph = G
        
        return G



    # Function to determine level of nodes (determine levels of LF reactions)
    def levels(self):

        # Get source nodes (The nodes[reactions] with in degree 0, meaning the are not dependent upon any other nodes [reactions])
        sourceNodes = list(
        [node for node, in_degree in self.graph.in_degree() if in_degree == 0])

        # Determine shortest_path from each source node to each node (essentially determines the levels, as in LF)
        shortest_path = {}
        for sourceNode in sourceNodes:
            source_node_paths = nx.single_source_shortest_path_length(self.graph, sourceNode)
            
            # Take maximum of the shortest path from source and set this as level
            for key, value in source_node_paths.items():
                if (key in shortest_path):
                    shortest_path[key] = max(shortest_path[key], value)
                else:
                    shortest_path[key] = value
        
        return shortest_path
        
        
        
    # Draw Graph and plot using matplotlib
    def plot(self):    
        nx.draw_networkx(self.graph, arrows=True)
        plt.show()
        
    # Getter for Graph
    def get_graph(self):
        return self.graph


    def remove_hidden_edges(self):
        # Remove the hidden edges from the dotgraph
        with open(self.filename, "r") as f:
            lines = f.readlines()
        with open(self.filename, "w") as f:
            for line in lines:
                if "[style=invis]" not in line:
                    f.write(line)


# Example
# reflex_game = parse_dot("DotFiles/ReflexGameNoHiddenEdges.dot")
# graph = reflex_game.parse_graph_from_dot()
# print(reflex_game.levels())

# reflex_game.plot()
