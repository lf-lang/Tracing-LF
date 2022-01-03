#!/usr/bin/env python3
import json



class parse_json:
    
    def __init__(self, filepath):
        self.data = json.load(open(filepath))
        
        # Structure: 
        # {reactor: {reaction: [list of executions of reactions]}}
        
        # Dictionary containing all duration events
        execution_dict = {}
        
        # Iterate and correctly name keys (0 = Thread 0, else Worker(x))
        for key, value in self.data.pop("Execution").items():
            if key == "0":
                execution_dict["Thread 0"] = value
            else:
                execution_dict["Worker" + key] = value
        
        self.data["Execution"] = execution_dict
        
        
        
        # Determine start time, then remove this from all other timestamps
        start_time = 0
        
        for reactor, reactions in self.data.items():
            for reaction in reactions:
                if reaction == "startup":
                    start_time = self.data[reactor][reaction][0]["ts"]
                    break
        
        # Set new start time 
        for reactions in self.data.values():
            for reaction in reactions.values():
                for reaction_execution in reaction:
                    new_start_time = reaction_execution["ts"] - start_time
                    reaction_execution["ts"] = new_start_time
                    


       
    def get_reactions(self, reactor_name, reaction_name):
        """Returns the trace information of a given reactor and reaction"""
        for reactor, reactions in self.data.items():
            if reactor == reactor_name:
                for reaction in reactions:
                    if reaction == reaction_name:
                        return reactions[reaction]
    

    
                
    


