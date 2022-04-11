from Parser.parse_files import parser

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, HoverTool, Arrow, OpenHead, PrintfTickFormatter
from bokeh.plotting import figure, show
from bokeh.palettes import Set1 as palette
from bokeh.models import Title
from bokeh.models import CustomJS, MultiChoice, Panel, Tabs
import argparse
import regex



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
        
        # Dictionary containing a port as a key, with the value containing the reactions triggered by the downstream port (of the current port)
        self.port_dict = self.data_parser.get_port_dict()
        
        # List containing all reaction names
        self.action_names = self.data_parser.get_action_names()
        
        # List containing 4-tuples for arrow drawing
        self.arrow_pos = []
        
        # Stores whether to show coloured graph
        self.diable_arrows = False
        
        # Graph name
        self.graph_name = "Trace"
        
        
    
    def build_graph(self):
        """Builds the bokeh graph"""

        # Output to 
        output_file(self.graph_name + ".html")

        # Define figure
        p = figure(sizing_mode="stretch_both",
                   title=self.graph_name)
        # second plot which displays colours
        p_colours = figure(sizing_mode="stretch_both",
                           title=self.graph_name)
        # third plot for arrows
        p_arrows = figure(sizing_mode="stretch_both",
                           title=self.graph_name)
        
        # fourth plot for physical time only events
        p_physical_time = figure(sizing_mode="stretch_both",
                          title=self.graph_name)
        
        # -------------------------------------------------------------------
        # Draw colours (if enabled)
        
        # Colours chains of reactions originating from an action. (Assumes all chains begin with an action)
        # Uses the colour_nodes function to recursively assign a colour to nodes which are triggered by an action
        
    
        # default colours
        default_reaction_colour = "gold"
        default_action_colour = "cadetblue"
        default_exection_event_colour = "burlywood"
        
        # Set the default colours for all actions and reactions
        self.ordered_inst_events_reactions["default_colours"] = [
            default_reaction_colour for x in self.ordered_inst_events_reactions["name"]]
        self.ordered_inst_events_actions["default_colours"] = [
            default_action_colour for x in self.ordered_inst_events_actions["name"]]
        self.ordered_exe_events["default_colours"] = [
            default_exection_event_colour for x in self.ordered_exe_events["name"]]


        # If colouring, set colour to grey
        self.ordered_inst_events_reactions["colours"] = [
            "lightgrey" for x in self.ordered_inst_events_reactions["name"]]
        self.ordered_inst_events_actions["colours"] = [
            "lightgrey" for x in self.ordered_inst_events_actions["name"]]
        self.ordered_exe_events["colours"] = [
            "lightgrey" for x in self.ordered_exe_events["name"]]
        
        # Colour and find arrow positions
        self.colour()
        
        # -------------------------------------------------------------------
        # Include/Exclude Reactions
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--include", type=str,
                            help="Regex to INCLUDE only certain reactors or reactions")
        parser.add_argument("-x", "--exclude", type=str,
                            help="Regex to EXCLUDE certain reactors or reactions")
        args = parser.parse_args()

        if args.include and args.exclude:
            raise TypeError("Too many arguments")

        filtered_labels = []
        if args.include:
            for label in self.labels:
                if regex.search(args.include, label):
                    filtered_labels.append(label)
            self.labels = filtered_labels
            self.diable_arrows = True

        if args.exclude:
            for label in self.labels:
                if not regex.search(args.exclude, label):
                    filtered_labels.append(label)
            self.labels = filtered_labels
            self.diable_arrows = True

        self.remove_reactions()

        # -------------------------------------------------------------------
        # Draw arrows (if enabled) (self.arrows is constructed in colour())

        if not self.diable_arrows:
            for x_start, y_start, x_end, y_end in self.arrow_pos:
                p_arrows.add_layout(Arrow(end=OpenHead(
                    line_width=1, size=5), line_color="burlywood", x_start=x_start, y_start=y_start,
                    x_end=x_end, y_end=y_end))

        # -------------------------------------------------------------------
        # All execution events

        
        # data source
        source_exec_events = ColumnDataSource(self.ordered_exe_events)
        
            
        # https://docs.bokeh.org/en/latest/docs/user_guide/plotting.html#line-glyphs

        exe_line = p.multi_line(xs='x_multi_line', ys='y_multi_line', width=8, color="default_colours", hover_alpha=0.5,
                    source=source_exec_events, legend_label="Execution Events", muted_alpha=0.2)
        
        exe_line_colours = p_colours.multi_line(xs='x_multi_line', ys='y_multi_line', width=8, color="colours", hover_alpha=0.5,
                                               source=source_exec_events, legend_label="Execution Events", muted_alpha=0.2)
        
        exe_line_arrows = p_arrows.multi_line(xs='x_multi_line', ys='y_multi_line', width=8, color="colours", hover_alpha=0.5,
                                                source=source_exec_events, legend_label="Execution Events", muted_alpha=0.2)
        
        exe_line_physical_time = p_physical_time.multi_line(xs='x_multi_line', ys='y_multi_line', width=8, color="colours", hover_alpha=0.5,
                                                source=source_exec_events, legend_label="Execution Events", muted_alpha=0.2)
        # -------------------------------------------------------------------      
        
        # Execution event markers 
        exe_x_marker = [((x1 + x2)/2)
                        for x1, x2 in self.ordered_exe_events["x_multi_line"]]
        exe_y_marker = self.ordered_exe_events["y_axis"]
        
        dict_exec_markers = {"x_values" : exe_x_marker,
                            "y_values" : exe_y_marker,
                             "name": self.ordered_exe_events["name"],
                            "default_colours" : self.ordered_exe_events["default_colours"],
                            "colours" : self.ordered_exe_events["colours"]}
        
        source_exec_markers = ColumnDataSource(data=dict_exec_markers)

        p.diamond(x='x_values', y='y_values', color="default_colours",
                  size=7, source=source_exec_markers, legend_label="Execution Event Markers", muted_alpha=0.2)
        
        p_colours.diamond(x='x_values', y='y_values', color="colours",
                          size=7, source=source_exec_markers, legend_label="Execution Event Markers", muted_alpha=0.2)
        
        p_arrows.diamond(x='x_values', y='y_values', color="colours",
                          size=7, source=source_exec_markers, legend_label="Execution Event Markers", muted_alpha=0.2)


        p_physical_time.diamond(x='x_values', y='y_values', color="colours",
                        size=7, source=source_exec_markers, legend_label="Execution Event Markers", muted_alpha=0.2)

        # -------------------------------------------------------------------
        
        # All instantaneous events that are reactions
        source_inst_events_reactions = ColumnDataSource(self.ordered_inst_events_reactions)

        inst_reaction_hex = p.hex(x='time_start', y='y_axis', fill_color='default_colours', line_color="lightgrey",
                                  size=10, source=source_inst_events_reactions, legend_label="Reactions", muted_alpha=0.2)
        
        inst_reaction_hex_colours = p_colours.hex(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                  size=10, source=source_inst_events_reactions, legend_label="Reactions", muted_alpha=0.2)


        inst_reaction_hex_arrows = p_arrows.hex(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                                size=10, source=source_inst_events_reactions, legend_label="Reactions", muted_alpha=0.2)

        # -------------------------------------------------------------------
        
        # All instantaneous events that are actions
        source_inst_events_actions = ColumnDataSource(self.ordered_inst_events_actions)

        inst_action_hex = p.inverted_triangle(x='time_start', y='y_axis', fill_color='default_colours', line_color="lightgrey",
                                size=10, source=source_inst_events_actions, legend_label="Actions", muted_alpha=0.2)
        
        inst_action_hex_colours = p_colours.inverted_triangle(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                              size=10, source=source_inst_events_actions, legend_label="Actions", muted_alpha=0.2)
        
        inst_action_hex_arrows = p_arrows.inverted_triangle(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                                              size=10, source=source_inst_events_actions, legend_label="Actions", muted_alpha=0.2)


        inst_action_hex_physical_time = p_physical_time.inverted_triangle(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                                      size=10, source=source_inst_events_actions, legend_label="Actions", muted_alpha=0.2)

        
        # -------------------------------------------------------------------

        # PLOT OPTIONS
        location = "top_left"

        # Toggle to hide/show events
        click_policy = "mute"
        
        # Rename Axes and format ticks
        ticker = [y for y in range(len(self.labels))]
        major_label_overrides = self.number_labels
        formatter = PrintfTickFormatter(format="%f")

        # Add axis labels
        xaxis_label = "Time (ns)"
        xaxis_label_text_font_size = "24px"
        xaxis_label_text_color = "cadetblue"
        yaxis_label = "Reaction Name"
        yaxis_label_text_font_size = "24px"
        yaxis_label_text_color = "cadetblue"

        # Text below graph
        title_text = "Graph visualisation of a recorded LF trace. Use options (-a and -c) to show arrows and colours respectively. \n The tools on the right can be used to navigate the graph. Legend items can be clicked to mute series"
       
        # Add all properties to plots    
        for plot in [p, p_colours, p_arrows, p_physical_time]:
            plot.legend.location = location
            plot.legend.click_policy = click_policy
            plot.yaxis.ticker = ticker
            plot.yaxis.major_label_overrides = major_label_overrides
            plot.xaxis[0].formatter = formatter
            plot.xaxis.axis_label = xaxis_label
            plot.xaxis.axis_label_text_font_size = xaxis_label_text_font_size
            plot.xaxis.axis_label_text_color = xaxis_label_text_color
            plot.yaxis.axis_label = yaxis_label
            plot.yaxis.axis_label_text_font_size = yaxis_label_text_font_size
            plot.yaxis.axis_label_text_color = yaxis_label_text_color
            plot.add_layout(Title(text=title_text, align="center"), "below")

        # Define tooltips for Reactions and Execution Events
        tooltips_reactions = [
            ("name", "@name"),
            ("time_start", "@time_start"),
            ("priority", "@priority"),
            ("level", "@level"),
            ("triggers", "@triggers"),
            ("effects", "@effects"),
        ]

        # Define tooltips for Reactions and Execution Events
        tooltips_actions = [
            ("name", "@name"),
            ("time_start", "@time_start"),
            ("trace_event_type", "@trace_event_type"),
            ("triggers", "@triggers"),
            ("effects", "@effects"),
        ]
        
        tooltips_executions = [
            ("name", "@name"),
            ("time_start", "@time_start"),
            ("time_end", "@time_end"),
            ("trace_event_type", "@trace_event_type"),
            ("priority", "@priority"),
            ("level", "@level"),
            ("triggers", "@triggers"),
            ("effects", "@effects"),
            ("logical_time", "@logical_time"),
            ("microstep", "@microstep")
        ]
        
        # Hover tool only for instantaneous events 
        hover_tool = HoverTool(tooltips=tooltips_reactions, renderers=[inst_reaction_hex])
        hover_tool_colours = HoverTool(tooltips=tooltips_reactions, renderers=[inst_reaction_hex_colours])
        hover_tool_arrows = HoverTool(tooltips=tooltips_reactions, renderers=[inst_reaction_hex_arrows])
        
        # Hover tool only for instantaneous events and execution event lines (so that markers for exe events dont also have a tooltip)
        hover_tool_actions = HoverTool(tooltips=tooltips_actions, renderers=[inst_action_hex])
        hover_tool_actions_colours = HoverTool(tooltips=tooltips_actions, renderers=[inst_action_hex_colours])
        hover_tool_actions_arrows = HoverTool(tooltips=tooltips_actions, renderers=[inst_action_hex_arrows])
        hover_tool_actions_physical_time = HoverTool(tooltips=tooltips_actions, renderers=[inst_action_hex_physical_time])
        
        # Hover tool only for execution events (so that markers for exe events dont also have a tooltip)
        hover_tool_executions = HoverTool(tooltips=tooltips_executions, renderers=[exe_line])
        hover_tool_executions_colours = HoverTool(tooltips=tooltips_executions, renderers=[exe_line_colours])
        hover_tool_executions_arrows = HoverTool(tooltips=tooltips_executions, renderers=[exe_line_arrows])
        hover_tool_executions_physical_time = HoverTool(tooltips=tooltips_executions, renderers=[exe_line_physical_time])

        
        # Add the tools to the plot
        p.add_tools(hover_tool, hover_tool_actions, hover_tool_executions)
        p_colours.add_tools(hover_tool_colours, hover_tool_actions_colours, hover_tool_executions_colours)
        p_arrows.add_tools(hover_tool_arrows, hover_tool_actions_arrows, hover_tool_executions_arrows)
        p_physical_time.add_tools(hover_tool_actions_physical_time, hover_tool_executions_physical_time)
        
        
        # js radio buttons
        multi_choice = MultiChoice(
            value=self.labels, options=self.labels, sizing_mode="stretch_both")
        
        # Tim hier!!! 
        multi_choice.js_on_change("value", CustomJS(args=dict(sources=[source_inst_events_reactions, source_inst_events_actions, source_exec_events, source_exec_markers]), code="""
            sources.forEach(source => {
                console.log(source.data)
            let active_values = this.value
            let delete_us = []
            source.data.name.forEach(function(name, i) {
                if (!active_values.includes(name)) delete_us.push(i)
            })
            delete_us = delete_us.reverse()
            delete_us.forEach(i => {
                for (const [key, value] of Object.entries(source.data)) {
                    source.data[key].splice(i, 1)
                }
            })
            source.change.emit()
            })
        """))
        
        trace = Panel(child=p, title="trace") 
        coloured_trace = Panel(child=p_colours, title="coloured trace")
        arrows = Panel(child=p_arrows, title="arrows")
        physical_time = Panel(child=p_physical_time, title="physical time")
        data_picker = Panel(child=multi_choice, title="data picker")
        
        if not self.diable_arrows:
            show(Tabs(tabs=[trace, coloured_trace, arrows, physical_time, data_picker]))
        else:
            show(Tabs(tabs=[trace, coloured_trace, physical_time, data_picker]))




    def remove_reactions(self):
        # Set the active labels (important for the js widget)
        self.number_labels = {}
        for i in range(len(self.labels)):
            self.number_labels[i] = self.labels[i]
        
        label_y_pos = {v: k for k, v in self.number_labels.items()}
        
        # remove excluded data
        for data_source in [self.ordered_inst_events_reactions, self.ordered_inst_events_actions, self.ordered_exe_events]:
            # find all datapoints with exluded names and add their index to a list
            active_values = self.labels
            indices_to_remove = []
            for i in range(len(data_source["name"])):
                current_label = data_source["name"][i]
                if current_label not in active_values:
                    indices_to_remove.append(i)
                else:
                    data_source["y_axis"][i] = label_y_pos[current_label]
                    if data_source is self.ordered_exe_events:
                        data_source["y_multi_line"][i] = [
                            label_y_pos[current_label], label_y_pos[current_label]]

            # Going from bottom to top, remove all datapoints with exluded names (using their index in the respective data source table)
            indices_to_remove.reverse()
            for index in indices_to_remove:
                for key in data_source.keys():
                    data_source[key].pop(index)




    def colour(self):
        palette_pos = 0
        
        # Iterate through all actions
        for i in range(len(self.ordered_inst_events_actions["name"])):
            effects = self.ordered_inst_events_actions["effects"][i]
            action_time_start = self.ordered_inst_events_actions["time_start"][i]
            
            self.ordered_inst_events_actions["colours"][i] = palette[9][palette_pos % 9]
            
            # Iterate through all effects of the action and colour accordingly
            for effect in effects:
                
                # REACTIONS as effect of action
                current_reaction_pos = self.data_parser.get_reaction_pos(effect, action_time_start, self.ordered_inst_events_reactions)
                
                if current_reaction_pos is not None:
                    # Colour recursively
                    self.colour_iteratively(current_reaction_pos, palette_pos, self.ordered_inst_events_reactions, False)
                
                # EXECUTIONS as effect of action
                current_exe_pos = self.data_parser.get_reaction_pos(
                    effect, action_time_start, self.ordered_exe_events)
                
                if current_exe_pos is not None:
                    # Add arrow if enabled
                    self.arrow_pos.append(
                        (action_time_start, self.ordered_inst_events_actions["y_axis"][i], self.ordered_exe_events["time_start"][current_exe_pos], self.ordered_exe_events["y_axis"][current_exe_pos]))

                    # Colour recursively
                    self.colour_iteratively(current_exe_pos, palette_pos, self.ordered_exe_events, True)

                # Increment the palette colour
                palette_pos += 1

        
        
    def colour_iteratively(self, reaction_pos, palette_pos, reaction_dictionary, draw_arrows):
        '''Function which recursively colours reaction chains (via triggers/effects) from a given origin reaction
            First assigns the colour to a given reaction, then finds the reactions triggered and calls itself'''

        # Assign the current colour to the reaction
        reaction_dictionary["colours"][reaction_pos] = palette[9][palette_pos % 9]

        # Check if the reaction has further effects
        reaction_effects = reaction_dictionary[
            "effects"][reaction_pos]

        # For each reaction effect, colour iteratively
        for reaction_effect in (reaction_effects or []):

            # Check if the reaction effect is a reaction (If not, its an action and causes cycles while colouring)
            if reaction_effect not in self.action_names:

                reaction_effect_time = reaction_dictionary["time_end"][reaction_pos]

                # If the reaction effect is a write to a port, deduce the downstream port and its corresponding effect. This is the triggered reaction which is to be coloured
                if reaction_effect not in self.labels:
                        port_triggered_reactions = self.port_dict[reaction_effect]

                        for reaction in port_triggered_reactions:
                            reaction_effect_pos = self.data_parser.get_reaction_pos(
                                reaction, reaction_effect_time, reaction_dictionary)

                            if reaction_effect_pos is not None:
                                # If arrow drawing is true, add the beginning (x,y) and ending (x,y) as 4-tuple to arrow dict
                                if draw_arrows:
                                    self.arrow_pos.append((reaction_dictionary["time_end"][reaction_pos], reaction_dictionary["y_axis"][reaction_pos], reaction_dictionary["time_start"][reaction_effect_pos], reaction_dictionary["y_axis"][reaction_effect_pos]))
                            
                                self.colour_iteratively(reaction_effect_pos, palette_pos, reaction_dictionary, draw_arrows)

                else:
                    # Find the position of the reaction effect in the dict, using its name and the position of the reaction it was triggered by
                    # The reactions in the dictionary are ordered chronologically
                    reaction_effect_pos = self.data_parser.get_reaction_pos(
                        reaction_effect, reaction_effect_time)

                    if reaction_effect_pos is not None:
                        # If arrow drawing is true, add the beginning (x,y) and ending (x,y) as 4-tuple to arrow dict
                        self.arrow_pos.append(
                            (reaction_dictionary["time_end"][reaction_pos], reaction_dictionary["y_axis"][reaction_pos], reaction_dictionary["time_start"][reaction_effect_pos], reaction_dictionary["y_axis"][reaction_effect_pos]))
                        
                        self.colour_iteratively(reaction_effect_pos, palette_pos, reaction_dictionary, draw_arrows)
                        



if(__name__ == "__main__"):
    vis = visualiser("yaml_files/SleepingBarber.yaml",
                     "traces/SleepingBarber.json")

    vis.build_graph()
