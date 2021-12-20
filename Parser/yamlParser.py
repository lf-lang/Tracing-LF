#!/usr/bin/env python3
import yaml
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt


class parse_yaml:
    """ Parse yaml files generated from LF programs (currently only in the C++ target). Set 'export-to-yaml' option to true to generate the file. \n
        Allows parsing of the yaml file"""
        
    def __init__(self, filepath):
        
        # Attributes
        self.reaction_list = list()
        self.dependecy_dict = defaultdict(list)
        self.graph = nx.DiGraph()
       
        # Open yaml file and parse with pyyaml
        self.data = yaml.load(open(filepath), Loader=yaml.FullLoader)
        
    
        # Iteration variable
        reactor_instances = self.data['all_reactor_instances']
    
        # Delete the first item in the dict (this is the top level reactor)
        del reactor_instances[next(iter(reactor_instances))]
                       
        # Iterate through reactors and get reactions 
        for reactor in reactor_instances.items():
            reactor_name = reactor[0]
            
            # For each reaction, add it to the list of reactions
            for reaction in reactor[1]["reactions"]:
                
                # Rename to include reactor name in reaction name
                reaction["name"] = reactor_name + "." + reaction["name"]
                self.reaction_list.append(reaction)
              
                
        # Determine dependency list for each reaction and build a DiGraph
        dependencies = self.data['reaction_dependencies']
        
        iterator = iter(dependencies)
        for node in iterator:
            from_node = node["from"]
            to_node = next(iterator)["to"]
            
            # Add to dependecy dict
            self.dependecy_dict[from_node].append(to_node)
            
            # Add nodes and edge to digraph
            self.graph.add_edge(from_node, to_node)
            
            
            
        # find all nodes without dependecies and add these
        for reaction in self.reaction_list:
            reaction_name = reaction["name"]
            if reaction_name not in self.dependecy_dict:
                self.dependecy_dict[reaction_name] = []
        
        
        

        
                
   
    def get_level(self, node_name):
        """ Finds the level of a given node """
        
        for reaction in self.reaction_list:
            if node_name == reaction["name"]:
                return reaction["level"]
        
        raise ValueError("The given node does not exist. Possibly wrong name given")   
    
    
    def get_dependencies(self, node_name):
        """ Gets the list of dependencies for a given node """
        if node_name in self.dependecy_dict:
            return self.dependecy_dict[node_name]
        else:
            raise ValueError(
                "The given node does not exist. Possibly wrong name given")
            
    def get_dependency_graph(self):
        return self.graph
        

            
            
            
            
    
        
        
# test = parse_yaml("YamlFiles/ReflexGame.yaml")
# print(test.get_level("ReflexGame.p.reaction_2"))
# print(test.get_dependencies("ReflexGame.p.reaction_2"))

# test.plot()


