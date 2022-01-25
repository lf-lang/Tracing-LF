
from Parser.parse_files import parser


from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, HoverTool, Arrow, OpenHead
from bokeh.plotting import figure, show
from bokeh.palettes import Spectral as spectral_palette


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
    
    def build_graph(self, draw_arrows, draw_colors):
        """Builds the bokeh graph"""
        
        self.draw_arrows = draw_arrows
        self.draw_colors = draw_colors

        # Output to 
        output_file(self.graph_name + ".html")

        # Define figure
        p = figure(sizing_mode="stretch_both",
                   title=self.graph_name)
        
        
        # -------------------------------------------------------------------

        # Arrows
        if self.draw_arrows is True:
            for i in range(len(self.ordered_inst_events_actions["name"])):
                action_effects = self.ordered_inst_events_actions["effects"][i]
                action_triggers = self.ordered_inst_events_actions["triggers"][i]
                action_time_start = self.ordered_inst_events_actions["time_start"][i]
                action_y_coord = self.ordered_inst_events_actions["y_axis"][i]
                for effect in action_effects:
                    for reaction in range(len(self.ordered_inst_events_reactions["name"])):
                        reaction_name = self.ordered_inst_events_reactions["name"][reaction]
                        reaction_time = self.ordered_inst_events_reactions["time_start"][reaction]
                        if reaction_name == effect and reaction_time >= action_time_start:
                            p.add_layout(Arrow(end=OpenHead(
                                line_width=1, size=10), x_start=action_time_start, y_start=action_y_coord,
                                x_end=reaction_time, y_end=self.ordered_inst_events_reactions["y_axis"][reaction]))
                            break

                for trigger in action_triggers:
                    previous_reactions = reversed(
                        range(len(self.ordered_inst_events_reactions["name"])))
                    for reaction in previous_reactions:
                        reaction_name = self.ordered_inst_events_reactions["name"][reaction]
                        reaction_time = self.ordered_inst_events_reactions["time_start"][reaction]
                        if reaction_name == trigger and reaction_time <= action_time_start:
                            p.add_layout(Arrow(end=OpenHead(
                                line_width=1, size=10), x_start=reaction_time, y_start=self.ordered_inst_events_reactions["y_axis"][reaction],
                                x_end=action_time_start, y_end=action_y_coord))
                            break

        # -------------------------------------------------------------------

        # Colors for action/reaction pairs

        if draw_colors is True:
            colour_reactions = []
            for i in range(len(self.ordered_inst_events_actions["name"])):
                action_effects = self.ordered_inst_events_actions["effects"][i]
                action_time_start = self.ordered_inst_events_actions["time_start"][i]
                for effect in action_effects:
                    for reaction in range(len(self.ordered_inst_events_reactions["name"])):
                        reaction_name = self.ordered_inst_events_reactions["name"][reaction]
                        reaction_time = self.ordered_inst_events_reactions["time_start"][reaction]
                        if reaction_name == effect and reaction_time == action_time_start:
                            colour_reactions.append(spectral_palette[6][i % 6])
                        else:
                            colour_reactions.append("darkgrey")
            
            colour_actions = colour_reactions 
        else:
            colour_reactions = ["hotpink" for x in self.ordered_inst_events_reactions["name"]]
            colour_actions = ["cadetblue" for x in self.ordered_inst_events_reactions["name"]]
        
        # -------------------------------------------------------------------
        # All execution events

        
        # data source
        source_exec_events = ColumnDataSource(self.ordered_exe_events)
        
            
        # https://docs.bokeh.org/en/latest/docs/user_guide/plotting.html#line-glyphs

        exe_line = p.multi_line(xs='x_multi_line', ys='y_multi_line', width=8, color="cornflowerblue", hover_alpha=0.5,
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
        source_inst_events_reactions = ColumnDataSource(self.ordered_inst_events_reactions)

        inst_reaction_hex = p.hex(x='time_start', y='y_axis', fill_color=colour_reactions, line_color="lightgrey",
                                  size=10, source=source_inst_events_reactions, legend_label="Reactions", muted_alpha=0.2)

        # -------------------------------------------------------------------
        
        # All instantaneous events that are actions
        source_inst_events_actions = ColumnDataSource(self.ordered_inst_events_actions)

        inst_action_hex = p.hex(x='time_start', y='y_axis', fill_color=colour_actions, line_color="lightgrey",
                                size=10, source=source_inst_events_actions, legend_label="Actions", muted_alpha=0.2)
        
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
        
        # Define tooltips for Reactions and Execution Events
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
        
        # Hover tool only for instantaneous events and execution event lines (so that markers for exe events dont also have a tooltip)
        hover_tool = HoverTool(tooltips=TOOLTIPS, renderers=[
                               inst_reaction_hex, exe_line])
        
        # Define tooltips for Reactions and Execution Events
        TOOLTIPS = [
            ("name", "@name"),
            ("time_start", "@time_start"),
            ("trace_event_type", "@trace_event_type"),
            ("triggers", "@triggers"),
            ("effects", "@effects"),
        ]

        # Hover tool only for instantaneous events and execution event lines (so that markers for exe events dont also have a tooltip)
        hover_tool_actions = HoverTool(
            tooltips=TOOLTIPS, renderers=[inst_action_hex])
        
        
        p.add_tools(hover_tool, hover_tool_actions)
                
        show(p)




if(__name__ == "__main__"):
    vis = visualiser("yaml_files/ReflexGame.yaml",
                     "traces/ReflexGame.json")

    vis.build_graph(False, True)
