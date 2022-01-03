#!/usr/bin/env python3
import yaml
from collections import defaultdict


class parse_yaml:
    """ Parse yaml files generated from LF programs (currently only in the C++ target). Set 'export-to-yaml' option to true to generate the file. \n
        Allows parsing of the yaml file"""
        
    def __init__(self, filepath):
        
        # Structure: Nested dict of reactions
        # {reactor : {reaction : {attribute : value}}}
        self.reaction_dict = {}
       
        # Open yaml file and parse with pyyaml
        self.data = yaml.load(open(filepath), Loader=yaml.FullLoader)
                       
        # Iterate through reactors and get reactions 
        for reactor, items in self.data['all_reactor_instances'].items():
            
            if reactor not in self.reaction_dict:
                self.reaction_dict[reactor] = {}
                
            # For each reaction, add it to the list of reactions
            if items["reactions"] is not None:
                for reaction in items["reactions"]:

                    self.reaction_dict[reactor][reaction["name"]] = reaction
                    
            if items["triggers"] is not None:
                for trigger in items["triggers"]:
                    
                    self.reaction_dict[reactor][trigger["name"]] = trigger
            
            
                
            # if reactions["inputs"] is not None:
            # if reactions["outputs"] is not None:
                
