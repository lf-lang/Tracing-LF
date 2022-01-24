
from Parser.parse_files import parser


from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, show
from bokeh.transform import jitter


class visualiser:
    
    def __init__(self, yaml_filepath, json_filepath):
        data_parser = parser()
        data_parser.parse(yaml_filepath, json_filepath)
        
        self.ordered_exe_events = data_parser.get_ordered_exe_events()
        self.ordered_inst_events_reactions = data_parser.get_ordered_inst_events_reactions()
        self.ordered_inst_events_actions = data_parser.get_ordered_inst_events_actions()
        
        self.y_axis_labels = data_parser.get_y_axis_labels()
        self.number_label = data_parser.get_number_label()
        
        
        self.graph_name = "Trace"
    
    
    def build_graph(self):
        """Builds the bokeh graph"""

        # Output to 
        output_file(self.graph_name + ".html")
        
        # Define tooltips
        TOOLTIPS = [
            ("name", "@name"),
            ("time_start", "@time_start"),
            ("time_end", "@time_end"),
            ("trace_event_type", "@trace_event_type"),
            ("priority", "@priority"),
            ("level", "@level"),
            ("triggers", "@triggers"),
            ("effects", "@effects"),
        ]

        # Define figure
        p = figure(sizing_mode="stretch_both",
                   title=self.graph_name)
        
        
        
        # -------------------------------------------------------------------
        # All execution events

        
        # data source
        source_exec_events = ColumnDataSource(self.ordered_exe_events)
        
            
        # https://docs.bokeh.org/en/latest/docs/user_guide/plotting.html#line-glyphs

        exe_line = p.multi_line(xs='x_multi_line', ys='y_multi_line', width=12, color="mediumseagreen", hover_alpha=0.5,
                    source=source_exec_events, legend_label="Execution Events", muted_alpha=0.2)

        # -------------------------------------------------------------------      
        
        # Execution event markers 
        exe_x_marker = [((x1 + x2)/2)
                        for x1, x2 in self.ordered_exe_events["x_multi_line"]]
        exe_y_marker = self.ordered_exe_events["y_axis"]
        
        exe_marker = p.diamond(exe_x_marker, exe_y_marker, color="mediumspringgreen",
                    size = 10, legend_label = "Execution Event Markers", muted_alpha = 0.2)
        
        # -------------------------------------------------------------------
        
        # All instantaneous events that are reactions
        source_inst_events = ColumnDataSource(self.ordered_inst_events_reactions)

        inst_reaction_hex = p.hex(x='time_start', y=jitter('y_axis', width=0, mean=0.25), fill_color="hotpink",
                         size=10, source=source_inst_events, legend_label="Instantaneous Events", muted_alpha=0.2)

        # -------------------------------------------------------------------
        
        # All instantaneous events that are actions
        source_inst_events = ColumnDataSource(self.ordered_inst_events_actions)

        inst_action_hex = p.hex(x='time_start', y=jitter('y_axis', width=0, mean=0.25), fill_color=" cadetblue",
                         size=10, source=source_inst_events, legend_label="Instantaneous Events", muted_alpha=0.2)

        # -------------------------------------------------------------------


        p.legend.location = "top_left"

        # Toggle to hide/show events
        p.legend.click_policy = "mute"
        
        # Rename Axes
        p.yaxis.ticker = [y for y in range(len(self.y_axis_labels))]
        p.yaxis.major_label_overrides = self.number_label

        # background
        p.background_fill_color = "beige"
        p.background_fill_alpha = 0.5
        
        # Hover tool only for instantaneous events and execution event lines (so that markers for exe events dont also have a tooltip)
        hover_tool = HoverTool(tooltips=TOOLTIPS, renderers=[
                               inst_reaction_hex, exe_line])
        p.add_tools(hover_tool)
        
                
        show(p)




if(__name__ == "__main__"):
    vis = visualiser("yaml_files/Throughput.yaml",
                     "traces/throughput_new.json")

    vis.build_graph()
