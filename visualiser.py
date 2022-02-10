
from Parser.parse_files import parser


from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, HoverTool, Arrow, OpenHead, NormalHead
from bokeh.plotting import figure, show
from bokeh.palettes import Spectral as spectral_palette
from numpy import true_divide


class visualiser:
    
    def __init__(self, yaml_filepath, json_filepath):
        self.data_parser = parser()
        self.data_parser.parse(yaml_filepath, json_filepath)
        
        # All execution events
        self.ordered_exe_events = self.data_parser.get_ordered_exe_events()
        
        # All instantaneous reactions
        self.ordered_inst_events_reactions = self.data_parser.get_ordered_inst_events_reactions()
        
        # All instantaneous actions
        self.ordered_inst_events_actions = self.data_parser.get_ordered_inst_events_actions()
        
        # Dictionaries which contain pairs for the numbers assigned to a reactor
        self.labels = self.data_parser.get_y_axis_labels()
        self.number_label = self.data_parser.get_number_label()
        
        # Dictionary containing a port as a key, with the value containing the reactions triggered by the downstream port (of the current port)
        self.port_dict = self.data_parser.get_port_dict()
        
        # List containing all reaction names
        self.action_names = self.data_parser.get_action_names()
        
        # Graph name
        self.graph_name = "Trace"
        
    
    
    
    def colour_nodes(self, reaction_pos, palette_pos):
        '''Function which recursively colours reaction chains (triggers/effects) from a given origin reaction
        First assigns the colour to a given reaction, then finds the reactions triggered and calls itself'''

        # Assign the current colour to the reaction
        self.ordered_inst_events_reactions["colours"][reaction_pos] = spectral_palette[5][palette_pos % 5]

        # Check if the reaction has further effects
        reaction_effects = self.ordered_inst_events_reactions[
            "effects"][reaction_pos]
        
        # For each reaction effect, colour iteratively 
        for reaction_effect in (reaction_effects or []):
            
            # Check if the reaction effect is a reaction (If not, its an action and causes cycles while colouring)
            if reaction_effect not in self.action_names:
            
                reaction_effect_time = self.ordered_inst_events_reactions["time_start"][reaction_pos]
                
                # If the reaction effect is a write to a port, deduce the downstream port and its corresponding effect. This is the reaction which is to be coloured
                if reaction_effect not in self.labels:
                    port_triggered_reactions = self.port_dict[reaction_effect]
                    
                    for reaction in port_triggered_reactions:
                        reaction_effect_pos = self.data_parser.get_reaction_pos(
                            reaction, reaction_effect_time)
                        
                        if reaction_effect_pos is not None:
                            self.colour_nodes(reaction_effect_pos, palette_pos)
                
                else:
                    # Find the position of the reaction effect in the dict, using its name and the position of the reaction it was triggered by
                    # The reactions in the dictionary are ordered chronologically
                    reaction_effect_pos = self.data_parser.get_reaction_pos(
                        reaction_effect, reaction_effect_time)
                    
                    if reaction_effect_pos is not None:
                        self.colour_nodes(reaction_effect_pos, palette_pos)
                    

        
        
    
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
            
            # Iterate through all actions 
            for i in range(len(self.ordered_inst_events_actions["name"])):
                action_effects = self.ordered_inst_events_actions["effects"][i]
                action_triggers = self.ordered_inst_events_actions["triggers"][i]
                action_time_start = self.ordered_inst_events_actions["time_start"][i]
                action_y_coord = self.ordered_inst_events_actions["y_axis"][i]
                
                for effect in action_effects:
                    # Iterate through all reactions
                    for reaction in range(len(self.ordered_inst_events_reactions["name"])):
                        reaction_name = self.ordered_inst_events_reactions["name"][reaction]
                        reaction_time = self.ordered_inst_events_reactions["time_start"][reaction]
                        if reaction_name == effect and reaction_time >= action_time_start:
                            
                            # Add the arrow 
                            p.add_layout(Arrow(end=NormalHead(
                                line_width=1, size=5), line_color="burlywood", x_start=action_time_start, y_start=action_y_coord,
                                x_end=reaction_time, y_end=self.ordered_inst_events_reactions["y_axis"][reaction]))
                            break
                
                # Iterate through each trigger of the action
                for trigger in action_triggers:
                    previous_reactions = reversed(
                        range(len(self.ordered_inst_events_reactions["name"])))
                    for reaction in previous_reactions:
                        reaction_name = self.ordered_inst_events_reactions["name"][reaction]
                        reaction_time = self.ordered_inst_events_reactions["time_start"][reaction]
                        if reaction_name == trigger and reaction_time <= action_time_start:
                            
                            # Add the arrow
                            p.add_layout(Arrow(end=NormalHead(
                                line_width=1, size=5), line_color="burlywood", x_start=reaction_time, y_start=self.ordered_inst_events_reactions["y_axis"][reaction],
                                x_end=action_time_start, y_end=action_y_coord))
                            break

        # -------------------------------------------------------------------

        # Colours chains of reactions originating from an action. 
        # Uses the colour_nodes function to recursively assign a colour to nodes which are triggered by an action
        
        # Set the default colours for all actions and reactions
        self.ordered_inst_events_reactions["colours"] = [
            "hotpink" for x in self.ordered_inst_events_reactions["name"]]
        self.ordered_inst_events_actions["colours"] = [
            "cadetblue" for x in self.ordered_inst_events_actions["name"]]

        if draw_colors is True:
            
            palette_pos = 0
            
            # Iterate through all actions
            for i in range(len(self.ordered_inst_events_actions["name"])):
                
                effects = self.ordered_inst_events_actions["effects"][i]
                action_time_start = self.ordered_inst_events_actions["time_start"][i]
                
                self.ordered_inst_events_actions["colours"][i] = spectral_palette[5][palette_pos % 5]
                
                # Iterate through all effects of the action and colour accordingly
                for effect in effects:
                    
                    # Retrieve the position of the reaction within the reaction dictionary (of lists)
                    current_reaction_pos = self.data_parser.get_reaction_pos(effect, action_time_start)
                    
                    if current_reaction_pos is not None:
                        self.colour_nodes(current_reaction_pos, palette_pos)
                    
                    # Increment the palette colour
                    palette_pos += 1




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

        inst_reaction_hex = p.hex(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                  size=10, source=source_inst_events_reactions, legend_label="Reactions", muted_alpha=0.2)

        # -------------------------------------------------------------------
        
        # All instantaneous events that are actions
        source_inst_events_actions = ColumnDataSource(self.ordered_inst_events_actions)

        inst_action_hex = p.hex(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                size=10, source=source_inst_events_actions, legend_label="Actions", muted_alpha=0.2)
        
        # -------------------------------------------------------------------

        
        p.legend.location = "top_left"

        # Toggle to hide/show events
        p.legend.click_policy = "mute"

        # Rename Axes
        p.yaxis.ticker = [y for y in range(len(self.labels))]
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

    arrows = False
    colours = True
    vis.build_graph(arrows, colours)
