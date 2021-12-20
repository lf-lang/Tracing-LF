#!/usr/bin/env python3
import json



class parse_json:
    
    def __init__(self, filepath):
        self.raw_data = json.load(open(filepath))
        
        # Structure: 
        # {reactor: {reaction: [list of executions of reactions]}}
        
        # dictionary containing all duration events
        self.execution_dict = self.raw_data.pop("Execution")
        
        
        
        # process the data
        
        # Determine start time, then remove this from all other timestamps
        start_time = 0
        
        for reactor, reactions in self.raw_data.items():
            for reaction in reactions:
                if reaction == "startup":
                    start_time = self.raw_data[reactor][reaction][0]["ts"]
                    break
        
        
        for reactions in self.raw_data.values():
            for reaction in reactions.values():
                for reaction_execution in reaction:
                    new_start_time = reaction_execution["ts"] - start_time
                    reaction_execution["ts"] = new_start_time
                    


       
    def get_reactions(self, reactor_name, reaction_name):
        """Returns the trace information of a given reactor and reaction"""
        for reactor, reactions in self.raw_data.items():
            if reactor == reactor_name:
                for reaction in reactions:
                    if reaction == reaction_name:
                        return reactions[reaction]
    
            
       



