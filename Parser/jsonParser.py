#!/usr/bin/env python3
import json



class parse_json:
    
    def __init__(self, filepath):
        self.data = json.load(open(filepath))
        
        # list of reactor names - [reactor.name0, reactor.name1, ...]
        self.y_axis_labels = []

        # list of axis labels to assign reactor names to y-values {reactor.name0 : 0, reactor.name1 : 1, ...}
        # Solves problem: https://github.com/bokeh/bokeh/issues/6907
        self.reactor_number = {}
        
        # reversal of reactor_number
        self.number_label = {}
        
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
        
        # Set new start time, find all reaction names and assign number to each reaction
        for reactor, reactions in self.data.items():
            for name, reaction in reactions.items():
                
                for reaction_execution in reaction:
                    new_start_time = reaction_execution["ts"] - start_time
                    reaction_execution["ts"] = new_start_time
                    
                if reactor != "Execution":
                    reactor_name = reactor + "." + name

                    # Assigns current y-coord to reactor name
                    self.number_label[len(
                        self.y_axis_labels)] = reactor_name

                    # Add reactor name to list
                    self.y_axis_labels.append(reactor_name)

                    
        # reverse number_label dict
        self.reactor_number = {v: k for k, v in self.number_label.items()}

