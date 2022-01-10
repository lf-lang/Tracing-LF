
from Parser.jsonParser import parse_json
from Parser.yamlParser import parse_yaml

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show
from bokeh.transform import jitter




class visualiser:
    
    def __init__(self, yaml_filepath, json_filepath):
        
        # list of tuples - [(reactor1, reaction1),(reactor2, reaction2)]
        self.y_axis_labels = []

        yaml_data = parse_yaml(yaml_filepath).reaction_dict
        # {reactor : {reaction : {attribute : value}}}
        
        json_data = parse_json(json_filepath).data
        # {reactor: {reaction: [list of executions of reactions]}}
        
        
        # Dictionary containing all compiled data for each instantaneous event execution
        self.ordered_inst_events_dict = {"name": [], "reactor": [], "reaction": [], "time_start": [], "trace_event_type": [], "priority": [], "level": [], "triggers": [], "effects": []}
        
        # Dictionary containing all compiled data for each execution event execution
        self.ordered_exe_events_dict = {"name": [], "time_start": [], "time_end": [], "priority": [], "level": [], "triggers": [], "effects": [], "x_multi_line" : [], "y_multi_line" : []}

        
        # Iterate through all recorded reactions and order into dicts
        for reactor, reactions in json_data.items():
            
            # Execution events (not instantaneous)
            if reactor == "Execution":
                for reaction in reactions:
                    execution_events_iter = iter(json_data[reactor][reaction])
                    for reaction_instance in execution_events_iter:
                    
                        # JSON Data
                        self.ordered_exe_events_dict["name"].append(reaction_instance["name"])
                        self.ordered_exe_events_dict["time_start"].append(
                            reaction_instance["ts"])
                        
                        # x - main reactor name
                        # y - reactor name
                        # z - reaction name
                        x,y,z = reaction_instance["name"].split(".", 2)
                        
                        current_reactor_name = x + "." + y
                        current_reaction_name = z
                        
                        current_reaction = yaml_data[current_reactor_name][current_reaction_name]
                        
                        # YAML Data
                        attribute_list = ["priority", "level", "triggers", "effects"]
                        for attribute in attribute_list:
                            if attribute in current_reaction:
                                self.ordered_exe_events_dict[attribute].append(
                                    current_reaction[attribute])
                            else:
                                self.ordered_exe_events_dict[attribute].append(
                                    "Not Found")
                        
                        # Get end time of event by going to the next json event (start and end events are distinct)
                        try:
                            next_reaction = next(execution_events_iter)
                            self.ordered_exe_events_dict["time_end"].append(
                                next_reaction["ts"])
                        
                        # If no end event exists, add end time as same timestamp (i.e. the last element of time_start)
                        except StopIteration as e:
                            self.ordered_exe_events_dict["time_end"].append(
                                self.ordered_exe_events_dict["time_start"][-1])
                    
            # All other events from the trace 
            else:
                for reaction in reactions:
                    self.y_axis_labels.append((reactor, reaction))
                    
                    for reaction_instance in json_data[reactor][reaction]:
                        
                        # JSON Data
                        self.ordered_inst_events_dict["name"].append(reactor + "." + reaction)
                        self.ordered_inst_events_dict["reactor"].append(reactor)
                        self.ordered_inst_events_dict["reaction"].append(reaction)
                        self.ordered_inst_events_dict["time_start"].append(
                            reaction_instance["ts"])
                        self.ordered_inst_events_dict["trace_event_type"].append(
                            reaction_instance["ph"])
                        
                        # YAML Data
                        current_reaction = yaml_data[reactor][reaction]
                        
                        attribute_list = ["priority", "level", "triggers", "effects"]
                        for attribute in attribute_list:
                            if attribute in current_reaction:
                                self.ordered_inst_events_dict[attribute].append(
                                    current_reaction[attribute])
                            else:
                                self.ordered_inst_events_dict[attribute].append("Not Found")
        
    
    
    
    def build_graph(self):
        """Builds the bokeh graph"""

        # output to static HTML file
        output_file("test.html")
        
        TOOLTIPS = [
            ("name", "@name"),
            ("time_start", "@time_start"),
            ("trace_event_type", "@trace_event_type"),
            ("priority", "@priority"),
            ("level", "@level"),
            ("triggers", "@triggers"),
            ("effects", "@effects"),
        ]
        
        y_axis_names = ['.'.join(tup) for tup in self.y_axis_labels]

        p = figure(y_range=y_axis_names, sizing_mode="stretch_both",
                   title="Trace Visualisation", tooltips=TOOLTIPS)
        
        
        # -------------------------------------------------------------------
        # All instantaneous events
        source_inst_events = ColumnDataSource(self.ordered_inst_events_dict)

        p.diamond(x='time_start', y=jitter('name', width=0.6, range=p.y_range),
                  size=10, source=source_inst_events, legend_label="Instantaneous Events", muted_alpha=0.2)
        
        
        # -------------------------------------------------------------------
        # All execution events
        
        # order data for multiline graph
        for start_time, end_time in zip(self.ordered_exe_events_dict["time_start"], self.ordered_exe_events_dict["time_end"]):
            self.ordered_exe_events_dict["x_multi_line"].append(
                [start_time, end_time])

        for reaction_name in self.ordered_exe_events_dict["name"]:
            self.ordered_exe_events_dict["y_multi_line"].append(
                [reaction_name, reaction_name])

        
        # data source
            # source_exec_events = ColumnDataSource(
            #     self.ordered_exe_events_dict)
                
            # # https://docs.bokeh.org/en/latest/docs/user_guide/plotting.html#line-glyphs

            # p.line( ,
            #             legend_label="Execution Events", muted_alpha=0.2)

        # -------------------------------------------------------------------      


        p.legend.location = "top_left"

        # Toggle to hide/show events
        p.legend.click_policy = "mute"
        
        
        show(p)



vis = visualiser("YamlFiles/ReflexGame.yaml",
                 "traces/reflextrace_formatted.json")

vis.build_graph()

