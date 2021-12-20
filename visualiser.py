#!/usr/bin/env python3
from Parser.jsonParser import parse_json
from Parser.yamlParser import parse_yaml

import networkx as nx

from bokeh.models import Circle, MultiLine
from bokeh.plotting import figure, from_networkx, show




class visualiser:
    
    def __init__(self, yaml_filepath, json_filepath):

        self.yaml_data = parse_yaml(yaml_filepath)
        self.json_data = parse_json(json_filepath)
        
    
    def build_graph(self):
        graph = nx.DiGraph
        
        # Add info to edges:
        # - trigger, triggered by, dependency?
        
        # Add info to nodes (each node is an instance of a reaction, as recorded in the program trace):
        # - Level, reactor
        
        

    def plot(self):
        plot = figure(width=400, height=400, x_range=(-1.2, 1.2), y_range=(-1.2, 1.2),
                    x_axis_location=None, y_axis_location=None, toolbar_location=None,
                    title="TEST", background_fill_color="#efefef")
                    #   tooltips="index: @index, club: @club")
        plot.grid.grid_line_color = None

        graph_renderer = from_networkx(
            self.yaml_data.get_dependency_graph(), nx.circular_layout, scale=1, center=(0, 0))
        graph_renderer.node_renderer.glyph = Circle(size=15, fill_color="lightblue")
        plot.renderers.append(graph_renderer)

        show(plot)






vis = visualiser("YamlFiles/ReflexGame.yaml",
                 "traces/reflextrace_formatted.json")

vis.build_graph()

