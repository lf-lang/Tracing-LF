#!/usr/bin/env python3
import yaml
from collections import defaultdict


class parse_yaml:
    """ Parse yaml files generated from LF programs (currently only in the C++ target). Set 'export-to-yaml' option to true to generate the file. \n
        Allows parsing of the yaml file"""
        
    def __init__(self, filepath):
        
        # Attributes
        self.reaction_dict = {}
       
        # Open yaml file and parse with pyyaml
        self.data = yaml.load(open(filepath), Loader=yaml.FullLoader)
        
    
        # Iteration variable
        reactor_instances = self.data['all_reactor_instances']
    
        # Delete the first item in the dict (this is the top level reactor)
        del reactor_instances[next(iter(reactor_instances))]
                       
        # Iterate through reactors and get reactions 
        for reactor, reactions in reactor_instances.items():
            
            if reactor not in self.reaction_dict:
                self.reaction_dict[reactor] = {}
            
            # For each reaction, add it to the list of reactions
            for reaction in reactions["reactions"]:
                
                # Rename to include reactor name in reaction name
                reaction_name = reaction.pop("name")
                reaction["reaction_name"] = reaction_name
                self.reaction_dict[reactor][reaction_name] = reaction
                
                
test = parse_yaml("YamlFiles/ReflexGame.yaml")
print("lol")


                
