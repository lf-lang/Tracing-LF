
from Parser.jsonParser import parse_json
from Parser.yamlParser import parse_yaml

from bokeh.models.sources import ColumnarDataSource
from bokeh.plotting import figure, show, output_file






class visualiser:
    
    def __init__(self, yaml_filepath, json_filepath):
        
        # list of tuples - [(reactor1, reaction1),(reactor2, reaction2)]
        self.y_axis_labels = []

        yaml_data = parse_yaml(yaml_filepath).reaction_dict
        # {reactor : {reaction : {attribute : value}}}
        
        json_data = parse_json(json_filepath).data
        # {reactor: {reaction: [list of executions of reactions]}}
        
        
        # Dictionary containing all compiled data for each reaction execution
        self.ordered_data_dict = {"reactor": [], "reaction": [], "name": [], "time_start": [], "trace_event_type": [], "priority": [], "level": [], "triggers": [], "effects": []}

        
        for reactor, reactions in json_data.items():
            
            # TODO: Handle duration events
            if reactor == "Execution":
                continue
            
            for reaction in reactions:
                self.y_axis_labels.append((reactor, reaction))
                
                for reaction_instance in json_data[reactor][reaction]:
                    
                    self.ordered_data_dict["reactor"].append(reactor)
                    self.ordered_data_dict["reaction"].append(reaction)
                    
                    self.ordered_data_dict["name"].append(
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
                    
                
                    
                
            
                
                


    
    def build_graph(self):

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
        
        # Configyre y-axis range to be the concatenation of reactor and reaction (E.g. Reactor1, reaction1 -> Reactor1.reaction1 would be the new label)
        y = ['.'.join(tup) for tup in self.y_axis_labels]
        p = figure(width=400, height=400, tooltips=TOOLTIPS, y_range=y)
        p.yaxis.axis_label = 'Reactions'
        p.xaxis.axis_label = 'Time'
        
        
        # Provide DataSource
        
        source = ColumnarDataSource(data=self.ordered_data_dict)
        
        p.circle(x="reactor", y="time_start", size=20, source=source)
        

        # show the results
        show(p)
        
        







vis = visualiser("YamlFiles/ReflexGame.yaml",
                 "traces/reflextrace_formatted.json")

vis.build_graph()

