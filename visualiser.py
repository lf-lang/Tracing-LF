
from Parser.jsonParser import parse_json
from Parser.yamlParser import parse_yaml

from collections import defaultdict

from bokeh.plotting import figure, show, output_file
import pandas as pd





class visualiser:
    
    def __init__(self, yaml_filepath, json_filepath):
        
        # list of tuples - [(reactor1, reaction1),(reactor2, reaction2)]
        self.y_axis_labels = []

        yaml_data = parse_yaml(yaml_filepath).reaction_dict
        # {reactor : {reaction : {attribute : value}}}
        
        json_data = parse_json(json_filepath).data
        # {reactor: {reaction: [list of executions of reactions]}}
        
        
        # Dictionary containing all compiled data for each reaction execution
        ordered_data_dict = {"reactor": [], "reaction": [], "name": [], "time_start": [], "trace_event_type": [], "priority": [], "level": [], "triggers": [], "effects": []}

        
        for reactor, reactions in json_data.items():
            
            # TODO: Handle duration events
            if reactor == "Execution":
                continue
            
            for reaction in reactions:
                self.y_axis_labels.append((reactor, reaction))
                
                for reaction_instance in json_data[reactor][reaction]:
                    
                    ordered_data_dict["reactor"].append(reactor)
                    ordered_data_dict["reaction"].append(reaction)
                    
                    ordered_data_dict["name"].append(reaction_instance["name"])
                    ordered_data_dict["time_start"].append(reaction_instance["ts"])
                    ordered_data_dict["trace_event_type"].append(reaction_instance["ph"])
                    
                    current_reaction = yaml_data[reactor][reaction]
                    
                    attribute_list = ["priority",
                                      "level", "triggers", "effects"]
                    
                    for attribute in attribute_list:
                        if attribute in current_reaction:
                            ordered_data_dict[attribute].append(current_reaction[attribute])
                        else:
                            ordered_data_dict[attribute].append(None)
                    
        print(ordered_data_dict)
                
                    
                
            
                
                


    
    def build_graph(self):

        # output to static HTML file
        output_file("test.html")
        
        x = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2]
        y = ['.'.join(tup) for tup in self.y_axis_labels]
        
        p = figure(width=400, height=400, y_range=y)
        p.yaxis.axis_label = 'Reactions'
        p.xaxis.axis_label = 'Time'

        
        # add a circle renderer with a size, color, and alpha
        p.circle(x, y, size=20)

        # show the results
        show(p)

        
        # Add info to edges:
        # - trigger, triggered by, dependency?
        
        # Add info to nodes (each node is an instance of a reaction, as recorded in the program trace):
        # - Level, reactor
        
        







vis = visualiser("YamlFiles/ReflexGame.yaml",
                 "traces/reflextrace_formatted.json")

vis.build_graph()

