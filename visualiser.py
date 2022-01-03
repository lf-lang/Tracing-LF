
from Parser.jsonParser import parse_json
from Parser.yamlParser import parse_yaml

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import jitter

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
        self.ordered_data_dict = {"name": [], "reactor": [], "reaction": [], "event_name": [], "time_start": [], "trace_event_type": [], "priority": [], "level": [], "triggers": [], "effects": []}

        
        for reactor, reactions in json_data.items():
            
            # TODO: Handle duration events
            if reactor == "Execution":
                continue
            
            for reaction in reactions:
                self.y_axis_labels.append((reactor, reaction))
                
                for reaction_instance in json_data[reactor][reaction]:
                    
                    self.ordered_data_dict["name"].append(reactor + "." + reaction)
                    self.ordered_data_dict["reactor"].append(reactor)
                    self.ordered_data_dict["reaction"].append(reaction)
                    
                    self.ordered_data_dict["event_name"].append(
                        reaction_instance["name"])
                    self.ordered_data_dict["time_start"].append(
                        reaction_instance["ts"])
                    self.ordered_data_dict["trace_event_type"].append(
                        reaction_instance["ph"])
                    
                    current_reaction = yaml_data[reactor][reaction]
                    
                    attribute_list = ["priority",
                                      "level", "triggers", "effects"]
                    
                    for attribute in attribute_list:
                        if attribute in current_reaction:
                            self.ordered_data_dict[attribute].append(
                                current_reaction[attribute])
                        else:
                            self.ordered_data_dict[attribute].append(None)

    def get_ordered_data(self):
        return self.ordered_data_dict
    
    def build_graph(self):

        # output to static HTML file
        output_file("test.html")

        TOOLTIPS = [
            ("time_start", "@time_start"),
            ("trace_event_type", "@trace_event_type"),
            ("priority", "@priority"),
            ("level", "@level"),
            ("triggers", "@triggers"),
            ("effects", "@effects"),
        ]
        
        df = pd.DataFrame({"names": self.ordered_data_dict["name"]})
        df.insert(1, "times", self.ordered_data_dict["time_start"])

        source = ColumnDataSource(df)

        y = ['.'.join(tup) for tup in self.y_axis_labels]

        p = figure(height=300, y_range=y, sizing_mode="stretch_width",
                title="test")

        p.circle(x='times', y=jitter('names', width=0.6, range=p.y_range),  source=source, alpha=0.3)

        p.x_range.range_padding = 0
        p.ygrid.grid_line_color = None

        show(p)
                
    
    
    
        
        







vis = visualiser("YamlFiles/ReflexGame.yaml",
                 "traces/reflextrace_formatted.json")

vis.build_graph()

