from Parser.dotParser import parse_dot
import networkx as nx
from bokeh.models import Circle, MultiLine
from bokeh.plotting import figure, from_networkx, show




plot = figure(width=400, height=400, x_range=(-1.2, 1.2), y_range=(-1.2, 1.2),
              x_axis_location=None, y_axis_location=None, toolbar_location=None,
              title="Graph Interaction Demo", background_fill_color="#efefef",
              tooltips="index: @index, club: @club")
plot.grid.grid_line_color = None

graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))
graph_renderer.node_renderer.glyph = Circle(size=15, fill_color="lightblue")
graph_renderer.edge_renderer.glyph = MultiLine(line_color="edge_color",
                                               line_alpha=0.8, line_width=1.5)
plot.renderers.append(graph_renderer)

show(plot)



# .layout_provider.graph_layout
