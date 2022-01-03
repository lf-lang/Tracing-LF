#!/usr/bin/env python3
from Parser.jsonParser import parse_json
from Parser.yamlParser import parse_yaml





class visualiser:
    
    def __init__(self, yaml_filepath, json_filepath):

        self.yaml_data = parse_yaml(yaml_filepath)
        self.json_data = parse_json(json_filepath)
        
    
    def build_graph(self):
        
        # Retrieve the json data
        data = self.json_data.raw_data
        yaml_data = self.yaml_data.reaction_list
        
        x = []
        y = []
        
        # Iterate through reactors and their reactions
        for reactor, reactions in data.items():
            
            # Add all reactors to y axis 
            if reactor not in y:
                y.append(reactor)
                
            # Iterate through all reactions
            for reaction in reactions:
                print(reaction)
        
        # Add info to edges:
        # - trigger, triggered by, dependency?
        
        # Add info to nodes (each node is an instance of a reaction, as recorded in the program trace):
        # - Level, reactor
        
        







vis = visualiser("YamlFiles/ReflexGame.yaml",
                 "traces/reflextrace_formatted.json")

vis.build_graph()

