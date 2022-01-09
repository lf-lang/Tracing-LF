
from Parser.jsonParser import parse_json
from Parser.yamlParser import parse_yaml

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show
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
        
        
        # Dictionary containing all compiled data for each instantaneous event execution
        self.ordered_inst_events_dict = {"name": [], "reactor": [], "reaction": [], "event_name": [], "time_start": [], "trace_event_type": [], "priority": [], "level": [], "triggers": [], "effects": []}
        
        # Dictionary containing all compiled data for each instantaneous event execution
        self.ordered_inst_events_dict = {"name": [], "reactor": [], "reaction": [], "event_name": [], "time_start": [], "time_end": [], "trace_event_type": [], "priority": [], "level": [], "triggers": [], "effects": []}

        
        for reactor, reactions in json_data.items():
            

            if reactor == "Execution":
                # execution_events_iter = iter(reactions)
                # for reaction in execution_events_iter:
                continue
                    
            
            for reaction in reactions:
                self.y_axis_labels.append((reactor, reaction))
                
                for reaction_instance in json_data[reactor][reaction]:
                    
                    self.ordered_inst_events_dict["name"].append(reactor + "." + reaction)
                    self.ordered_inst_events_dict["reactor"].append(reactor)
                    self.ordered_inst_events_dict["reaction"].append(reaction)
                    
                    self.ordered_inst_events_dict["event_name"].append(
                        reaction_instance["name"])
                    self.ordered_inst_events_dict["time_start"].append(
                        reaction_instance["ts"])
                    self.ordered_inst_events_dict["trace_event_type"].append(
                        reaction_instance["ph"])
                    
                    current_reaction = yaml_data[reactor][reaction]
                    
                    attribute_list = ["priority",
                                      "level", "triggers", "effects"]
                    
                    for attribute in attribute_list:
                        if attribute in current_reaction:
                            self.ordered_inst_events_dict[attribute].append(
                                current_reaction[attribute])
                        else:
                            self.ordered_inst_events_dict[attribute].append(None)
    
    
    
    def build_graph(self):
        """Builds the bokeh graph"""

        # output to static HTML file
        output_file("test.html")
        
        df = pd.DataFrame({"name": self.ordered_inst_events_dict["name"]})
        df.insert(1, "time_start", self.ordered_inst_events_dict["time_start"])
        df.insert(2, "trace_event_type",
                  self.ordered_inst_events_dict["trace_event_type"])
        df.insert(3, "priority",
                  self.ordered_inst_events_dict["priority"])
        df.insert(4, "level",
                  self.ordered_inst_events_dict["level"])
        df.insert(5, "triggers",
                  self.ordered_inst_events_dict["triggers"])
        df.insert(6, "effects",
                  self.ordered_inst_events_dict["trace_event_type"])

        source = ColumnDataSource(df)
        
        TOOLTIPS = [
            ("name", "@name"),
            ("time_start", "@time_start"),
            ("trace_event_type", "@trace_event_type"),
            ("priority", "@priority"),
            ("level", "@level"),
            ("triggers", "@triggers"),
            ("effects", "@effects"),
        ]

        y = ['.'.join(tup) for tup in self.y_axis_labels]

        p = figure(y_range=y, sizing_mode="stretch_both",
                title="Trace Visualisation", tooltips=TOOLTIPS)

        # All instantaneous events
        p.diamond(x='time_start', y=jitter('name', width=0.6, range=p.y_range),
                  size=10, source=source, legend_label="Instantaneous Events", muted_alpha=0.2)
        
        # Use multi_line to generate a line for each of the execution events
        # https://docs.bokeh.org/en/latest/docs/user_guide/plotting.html#line-glyphs
        # Add muted_alpha=0.2 to allow toggle 


        # Legend 
        p.legend.location = "top_left"
        # Toggle to hide/show events
        p.legend.click_policy = "mute"        

        show(p)
                
    
    
    
        
        







vis = visualiser("YamlFiles/ReflexGame.yaml",
                 "traces/reflextrace_formatted.json")

vis.build_graph()

