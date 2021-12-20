#!/usr/bin/env python3
from Parser.yamlParser import parse_yaml
import networkx as nx
from bokeh.models import Circle, MultiLine
from bokeh.plotting import figure, from_networkx, show


G = nx.DiGraph()

yaml_data = parse_yaml("YamlFiles/ReflexGame.yaml")
iter = yaml_data.get_dependency_iterator()
for reaction in iter:
    from_reaction = reaction["from"]
    to_reaction = next(iter)["to"]
    
    level_from = yaml_data.get_level(from_reaction)
    level_to = yaml_data.get_level(to_reaction)
    
    G.add_node(from_reaction, level=level_from)
    G.add_node(to_reaction, level=level_to)
    
    exists_dependency = to_reaction in yaml_data.get_dependencies(
        from_reaction)
    G.add_edge(from_reaction, to_reaction, dependency=exists_dependency)


edge_attrs = {}
for start_node, end_node in G.edges():
    edge_color = "blue" if G.nodes[start_node][
        "level"] > G.nodes[end_node]["level"] else "red"
    edge_attrs[(start_node, end_node)] = edge_color
    
nx.set_edge_attributes(G, edge_attrs, "edge_color")

plot = figure(width=400, height=400, x_range=(-1.2, 1.2), y_range=(-1.2, 1.2),
              x_axis_location=None, y_axis_location=None, toolbar_location=None,
              title="Graph Interaction Demo", background_fill_color="#efefef",
              tooltips="reaction: @index, level: @level")
plot.grid.grid_line_color = None

graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))
graph_renderer.node_renderer.glyph = Circle(size=15, fill_color="lightblue")
graph_renderer.edge_renderer.glyph = MultiLine(line_color="edge_color",
                                               line_alpha=0.8, line_width=1.5)
plot.renderers.append(graph_renderer)

show(plot)



# .layout_provider.graph_layout
