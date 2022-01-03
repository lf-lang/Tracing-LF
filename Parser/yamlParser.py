#!/usr/bin/env python3
import yaml
from collections import defaultdict


class parse_yaml:
    """ Parse yaml files generated from LF programs (currently only in the C++ target). Set 'export-to-yaml' option to true to generate the file. \n
        Allows parsing of the yaml file"""
        
    def __init__(self, filepath):
        
        # Attributes
        self.reaction_list = list()
        self.dependecy_dict = defaultdict(list)
       
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
                reaction["reaction_name"] = reaction.pop("name")
                reaction["reactor_name"] = reactor_name
                self.reaction_list.append(reaction)
              
                
        # Determine dependency list for each reaction
        dependencies = self.data['reaction_dependencies']
        
        iterator = iter(dependencies)
        for node in iterator:
            from_node = node["from"]
            to_node = next(iterator)["to"]
            
            # Add to dependecy dict
            self.dependecy_dict[from_node].append(to_node)
            
            
            
        # find all nodes without dependecies and add these
        for reaction in self.reaction_list:
            reaction_name = reaction["name"]
            if reaction_name not in self.dependecy_dict:
                self.dependecy_dict[reaction_name] = []
        
        

        
                
   
    def get_level(self, reaction_name):
        """ Finds the level of a given node """
        
        for reaction in self.reaction_list:
            if reaction_name == reaction["name"]:
                return reaction["level"]
        
        raise ValueError("The given node does not exist. Possibly wrong name given")   
    
    def get_dependencies(self, reaction_name):
        """ Gets the list of dependencies for a given node """
        if reaction_name in self.dependecy_dict:
            return self.dependecy_dict[reaction_name]
        else:
            raise ValueError(
                "The given node does not exist. Possibly wrong name given")
            
    def get_dependency_iterator(self):
        return iter(self.data['reaction_dependencies'])

