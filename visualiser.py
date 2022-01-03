
from Parser.jsonParser import parse_json
from Parser.yamlParser import parse_yaml

from bokeh.plotting import figure, show, output_file





class visualiser:
    
    def __init__(self, yaml_filepath, json_filepath):

        yaml_data = parse_yaml(yaml_filepath).reaction_dict
        # {reactor : {reaction : {attribute : value}}}
        
        json_data = parse_json(json_filepath).data
        # {reactor: {reaction: [list of executions of reactions]}}
        
        
        
        # Compile all related data into a single data structure
        self.data = yaml_data
        
        for reactor, reactions in json_data.items():
            if reactor not in yaml_data:
                continue
            
            for reaction in reactions:
                if reaction not in yaml_data[reactor]:
                    continue
                
                self.data[reactor][reaction]["traces"] = json_data[reactor][reaction]
        
        
        
        
    
    def build_graph(self):

        # output to static HTML file
        output_file("test.html")
        
        x = [1,2,3,4,5]
        y_1 = [1, 2, 3, 4, 5]
        y_2 = ["a", "b", "c", "d", "e"]
        
        p = figure(width=400, height=400, y_range=y_2)

        # add a circle renderer with a size, color, and alpha
        p.circle(x, y_2, size=20)

        # show the results
        show(p)

        
        # Add info to edges:
        # - trigger, triggered by, dependency?
        
        # Add info to nodes (each node is an instance of a reaction, as recorded in the program trace):
        # - Level, reactor
        
        







vis = visualiser("YamlFiles/ReflexGame.yaml",
                 "traces/reflextrace_formatted.json")

vis.build_graph()

