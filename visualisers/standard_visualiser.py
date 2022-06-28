#!/usr/bin/env python3
import os
from scripts.read_ctf import parser

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, HoverTool, Arrow, OpenHead, PrintfTickFormatter, Segment
from bokeh.plotting import figure, show
from bokeh.palettes import Set1 as palette
from bokeh.models import Title
from bokeh.models import CustomJS, MultiChoice, Panel, Tabs
import argparse
import regex
import os
import sys
import time



class visualiser:
    
    def __init__(self, ctf_filepath, yaml_filepath, plain_view, logic_lines_view):
        self.data_parser = parser()
        self.data_parser.parse(ctf_filepath, yaml_filepath)
        
        # All execution events
        self.ordered_exe_events = self.data_parser.get_ordered_exe_events()
        
        # All instantaneous reactions
        self.ordered_inst_events_reactions = self.data_parser.get_ordered_inst_events_reactions()
        
        # All instantaneous actions
        self.ordered_inst_events_actions = self.data_parser.get_ordered_inst_events_actions()
        
        # Dictionaries which contain pairs for the numbers assigned to a reactor
        self.labels = self.data_parser.get_y_axis_labels()

        # Dictionary that is the inverse of self.labels
        self.number_labels = self.data_parser.get_number_label()
        
        # Dictionary containing a port as a key, with the value containing the reactions triggered by the downstream port (of the current port)
        self.port_dict = self.data_parser.get_port_dict()
        
        # Dictionary containing all dependencies between reactions
        self.dependency_dict = self.data_parser.get_dependency_dict()
        
        # List containing all reaction names
        self.action_names = self.data_parser.get_action_names()
        
        # List containing 4-tuples for arrow drawing
        self.arrow_pos = []
        
        # Stores whether to show coloured graph
        self.diable_arrows = False
        
        # Graph name is the name of the main reactor
        self.graph_name = self.data_parser.get_main_reactor_name()

        self.plain_view = plain_view 
        self.logic_lines_view = logic_lines_view
        
        
    
    def build_graph(self, args):
        """Builds the bokeh visualisation. First assembles the plots and all options,"""
        
        # Output to 
        output_file(self.graph_name + ".html")

        # plot which displays colours
        p_colours = figure(sizing_mode="stretch_both",
                           title=self.graph_name)
        # plot for arrows
        p_arrows = figure(sizing_mode="stretch_both",
                           title=self.graph_name)
        
        # plot for physical time only events
        p_physical_time = figure(sizing_mode="stretch_both",
                          title=self.graph_name)

        # plot for worker view
        p_workers = figure(sizing_mode="stretch_both",
                          title=self.graph_name)
        
        # -------------------------------------------------------------------
        # Set default colours
            
        # default colours
        default_colour = "lightgrey"
        
        # Set the default colours for all actions and reactions
        for data_dict in [self.ordered_inst_events_reactions, self.ordered_inst_events_actions, self.ordered_exe_events]:
            data_dict["default_colours"] = [default_colour for x in data_dict["name"]]
            data_dict["colours"] = [default_colour for x in data_dict["name"]]

        # -------------------------------------------------------------------
        # Draw colours
        
        # Sets the colour of reactions based on their logical time. Each microstep is assigned a new colour from a palette of 9 colours. 
        
        
        # Find all possible logical times, by getting the logical time of all possible events (actions, reactions and physical executions).
        action_logic_times = set(zip(
            self.ordered_inst_events_actions["logical_time"], self.ordered_inst_events_actions["microstep"]))
        
        reaction_logic_times = set(zip(
            self.ordered_inst_events_reactions["logical_time"], self.ordered_inst_events_reactions["microstep"]))

        execution_logic_times = set(zip(
            self.ordered_exe_events["logical_time"], self.ordered_exe_events["microstep"]))
        
        # compile all tuples of logical times into one list
        action_logic_times.update(reaction_logic_times, execution_logic_times)
        
        # Sorted set of all logical times (time, microstep)
        all_logic_times = sorted(action_logic_times)
        
        # Dictionary containing tuple as key, colour as value
        logical_colours_dict = {}
        
        # Assign colours to logical times
        palette_pos = 0
        for logical_time in all_logic_times:
            logical_colours_dict[logical_time] = palette[9][palette_pos % 9]
            palette_pos += 1
            
        # Assign colours to reactions
        for dictonary in [self.ordered_exe_events, self.ordered_inst_events_actions, self.ordered_inst_events_reactions]:
            for pos in range(len(dictonary["name"])):
                logic_time_tuple = (dictonary["logical_time"][pos], dictonary["microstep"][pos])
                dictonary["colours"][pos] = logical_colours_dict[logic_time_tuple]


        # -------------------------------------------------------------------
        # Include/Exclude Reactions
        
        # Too many args
        if args.include and args.exclude:
            raise TypeError("Too many arguments")

        # Include reactions
        filtered_labels = []
        if args.include:
            for label in self.labels:
                if regex.search(args.include, label):
                    filtered_labels.append(label)
            self.labels = filtered_labels
            self.diable_arrows = True

        # Exclude reactions
        if args.exclude:
            for label in self.labels:
                if not regex.search(args.exclude, label):
                    filtered_labels.append(label)
            self.labels = filtered_labels
            self.diable_arrows = True

        self.remove_reactions()


        # -------------------------------------------------------------------
        # Draw dependency arrows 
        
        # Disbale arrows if reactions are removed in above block.
        if not self.diable_arrows:
            # Discover all dependencies
            self.find_dependencies()
        
        # Draw
        for x_start, y_start, x_end, y_end in self.arrow_pos:
            p_arrows.add_layout(Arrow(end=OpenHead(
                line_width=1, size=5), line_color="lightblue", x_start=x_start, y_start=y_start, line_width=0.7,
                x_end=x_end, y_end=y_end))


        # -------------------------------------------------------------------
        # Draw vertical lines for each logical time (if enabled)

        if self.logic_lines_view: 
            # Get the min and max y values of the plot
            min_y = list(self.number_labels.keys())[0]
            max_y = list(self.number_labels.keys())[-1]

            # list to track x values of lines
            line_x_coords = []
            
        # Each new logical time (logical_time, microstep) is encoded with a new colour
            if len(self.ordered_exe_events["colours"]) > 0: #If more than one event exists
                
                # Get the first colour
                current_colour = self.ordered_exe_events["colours"][0]

                # Iterate through all positions in the self.ordered_exe_events list
                for i in range(len(self.ordered_exe_events["colours"])):
                    new_colour = self.ordered_exe_events["colours"][i]

                    # New logical time reached when a colour change occurs (colours are computed earlier in the script)
                    if current_colour != new_colour:
                        
                        # Get the x value between the end of old logical time and the start of the new one (so that the line falls in the middle, between
                        # logical times)
                        x_value = (self.ordered_exe_events["time_start"][i] + self.ordered_exe_events["time_end"][i-1]) / 2

                        # Append the x-value where the line is to be placed to the list
                        line_x_coords.append(x_value)

                        # Assign current_colour variable the newly reached colour
                        current_colour = new_colour


            # Segment plotting requires x0, y0, x1, y1 to plot a line. Below lists are as long as line_x_coords list, containing the same y value
            # corresponding to the top and bottom of the plot
            line_y0_coords = [min_y for y in line_x_coords]
            line_y1_coords = [max_y for y in line_x_coords]

            p_physical_time.segment(x0=line_x_coords, y0=line_y0_coords, x1=line_x_coords,
                y1=line_y1_coords, color="lightgrey", line_width=1)     

        # -------------------------------------------------------------------
        # All execution events

        # Plot the data with multiline, adding it to each available plot. 

        
        # data source
        source_exec_events = ColumnDataSource(self.ordered_exe_events)
        
        # Plotting with bokeh:
        # https://docs.bokeh.org/en/latest/docs/user_guide/plotting.html#line-glyphs

        exe_line_colours = p_colours.multi_line(xs='x_multi_line', ys='y_multi_line', width=8, color="colours", hover_alpha=0.5,
                                               source=source_exec_events, legend_label="Execution Events", muted_alpha=0.2)
        
        exe_line_arrows = p_arrows.multi_line(xs='x_multi_line', ys='y_multi_line', width=8, color="colours", hover_alpha=0.5,
                                                source=source_exec_events, legend_label="Execution Events", muted_alpha=0.2)
        
        exe_line_physical_time = p_physical_time.multi_line(xs='x_multi_line', ys='y_multi_line', width=8, color="colours", hover_alpha=0.5,
                                                source=source_exec_events, legend_label="Execution Events", muted_alpha=0.2)
        # -------------------------------------------------------------------      
        
        # Execution event markers 
        # Markers denoting the middle of an execution event. The marker is small, such that it is invisible when the line is visible.
        # Primary purpose is for showing the user where very short execution events are on the graph, which would not be 
        # visible without large amounts of zoom

        # Find the middle point of every execution. x_multi_line contains start and end time as tuple. Take the middle value of this
        exe_x_marker = [((x1 + x2)/2)
                        for x1, x2 in self.ordered_exe_events["x_multi_line"]]
        
        # Y-value of the marker
        exe_y_marker = self.ordered_exe_events["y_axis"]
        
        # Assemble dict
        dict_exec_markers = {"x_values" : exe_x_marker,
                            "y_values" : exe_y_marker,
                            "name": self.ordered_exe_events["name"],
                            "default_colours" : self.ordered_exe_events["default_colours"],
                            "colours" : self.ordered_exe_events["colours"]}
        # Set datasource
        source_exec_markers = ColumnDataSource(data=dict_exec_markers)

        # Add to plots
        p_colours.diamond(x='x_values', y='y_values', color="colours",
                          size=7, source=source_exec_markers, legend_label="Execution Event Markers", muted_alpha=0.2)
        
        p_arrows.diamond(x='x_values', y='y_values', color="colours",
                          size=7, source=source_exec_markers, legend_label="Execution Event Markers", muted_alpha=0.2)


        p_physical_time.diamond(x='x_values', y='y_values', color="colours",
                        size=7, source=source_exec_markers, legend_label="Execution Event Markers", muted_alpha=0.2)

        # -------------------------------------------------------------------
        
        # All reactions
        # The markers denoting the logical time execution of a reaction. 

        # Add to data source
        source_inst_events_reactions = ColumnDataSource(self.ordered_inst_events_reactions)
        
        # Add to plots
        inst_reaction_hex_colours = p_colours.hex(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                  size=10, source=source_inst_events_reactions, legend_label="Reactions", muted_alpha=0.2)


        inst_reaction_hex_arrows = p_arrows.hex(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                                size=10, source=source_inst_events_reactions, legend_label="Reactions", muted_alpha=0.2)

        # -------------------------------------------------------------------
        
        # All actions
        # The markers denoting the logical time execution of an action. 

        # Add to data source
        source_inst_events_actions = ColumnDataSource(self.ordered_inst_events_actions)

        # Add to plots
        inst_action_hex_colours = p_colours.inverted_triangle(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                              size=10, source=source_inst_events_actions, legend_label="Actions", muted_alpha=0.2)
        
        inst_action_hex_arrows = p_arrows.inverted_triangle(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                                              size=10, source=source_inst_events_actions, legend_label="Actions", muted_alpha=0.2)


        inst_action_hex_physical_time = p_physical_time.inverted_triangle(x='time_start', y='y_axis', fill_color='colours', line_color="lightgrey",
                                                      size=10, source=source_inst_events_actions, legend_label="Actions", muted_alpha=0.2)

        
        # -------------------------------------------------------------------

        # Worker view 
        # Includes only exection events as these are the physical executions done by the workers. Each y-axis value is a numbered worker. 
        
        worker_y_marker = list()
        
        # Build list of tuples of workers (y-axis integer), needed to plot multiline graph
        for y_value in self.ordered_exe_events["worker"]:
            worker_y_marker.append([y_value, y_value])

        # Assemble dictionary
        dict_workers = {"x_values" : self.ordered_exe_events["x_multi_line"],
                            "y_values" : worker_y_marker,
                            "name": self.ordered_exe_events["name"],
                            "default_colours" : self.ordered_exe_events["default_colours"],
                            "colours" : self.ordered_exe_events["colours"],
                            "time_start" : self.ordered_exe_events["time_start"],
                            "time_end" : self.ordered_exe_events["time_end"],
                            "priority" : self.ordered_exe_events["priority"],
                            "level" : self.ordered_exe_events["level"],
                            "logical_time" : self.ordered_exe_events["logical_time"],
                            "microstep" : self.ordered_exe_events["microstep"]}

        source_workers = ColumnDataSource(data=dict_workers)

        # Add to plot
        workers = p_workers.multi_line(xs='x_values', ys='y_values', width=8, color="colours", hover_alpha=0.5,
                                               source=source_workers, legend_label="Execution Events", muted_alpha=0.2)


        # -------------------------------------------------------------------
        
        # Identical to execution markers. Denote executions with a marker, to make small (short) executions visible on the graph
        # Here markers are invisible until toggled in the legend. Abused by making the normal alpha = 0, muted alpha = 0.5
        exe_x_marker = [((x1 + x2)/2)
                        for x1, x2 in self.ordered_exe_events["x_multi_line"]]
        exe_y_marker = self.ordered_exe_events["worker"]
        
        dict_workers_markers = {"x_values" : exe_x_marker,
                            "y_values" : exe_y_marker,
                            "name": self.ordered_exe_events["name"],
                            "default_colours" : self.ordered_exe_events["default_colours"],
                            "colours" : self.ordered_exe_events["colours"]}
        
        source_workers_markers = ColumnDataSource(data=dict_workers_markers)

        workers_markers = p_workers.diamond(x='x_values', y='y_values', color="colours",
                          size=7, source=source_workers_markers, legend_label="Execution Event Markers", alpha=0, muted_alpha=0.5)


        # -------------------------------------------------------------------

        # ALL PLOT OPTIONS
        # Here all plot options and customisations are done, such as changing axis titles, formatting tickers,
        # configuring hover tools and setting which tabs to show


        location = "top_left"

        # Toggle to hide/show events
        click_policy = "mute"

        # Remove the main reactor name from all strings, to shorten them (Philosophers.Philosopher.Reaction_2 --> Philosopher.Reaction_2)
        short_y_labels = {k: v.split(".", 1)[1] for k, v in self.number_labels.items()}

        # Override y-axis labels to display the reaction name, not the y-value itself
        major_label_overrides = short_y_labels
        
        # Format ticks and set positions of ticks on the y-axis, such that they correspond to each reaction
        ticker = [y for y in range(len(self.labels))]
        formatter = PrintfTickFormatter(format="%f")
        

        # Worker y-axis display labels and ticker formating
        worker_ticker = [y for y in range(max(self.ordered_exe_events["worker"]) + 1)]
        worker_major_label_overrides = {i : ("Worker " + str(i)) for i in range(max(self.ordered_exe_events["worker"]) + 1)}

        # Add axis labels
        xaxis_label = "Time (ms)"
        xaxis_label_text_font_size = "24px"
        xaxis_label_text_color = "cadetblue"
        yaxis_label = "Reaction Name"
        yaxis_label_text_font_size = "24px"
        yaxis_label_text_color = "cadetblue"

        # Text below graph
        title_text = "Graph visualisation of a recorded LF trace. Use options (-a and -c) to show arrows and colours respectively. \n The tools on the right can be used to navigate the graph. Legend items can be clicked to mute series"
       
        # Add all properties to plots    
        for plot in [p_colours, p_arrows, p_physical_time, p_workers]:
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

        # Override labels and ticker for p_workers
        p_workers.yaxis.ticker = worker_ticker
        p_workers.yaxis.major_label_overrides = worker_major_label_overrides
        
        # Override text
        p_workers.add_layout(Title(text="Visualisation from the worker view. Click the on 'Execution Event Markers' in the legend to show any small data points", align="center"), "below")
        
        # Deactivate x-grid lines for worker view
        p_physical_time.xgrid.visible = False


        # Define tooltips for Reactions and Execution Events
        tooltips_reactions = [
            ("name", "@name"),
            ("time_start", "@time_start{0,0.00}"),
            ("priority", "@priority"),
            ("level", "@level"),
            ("logical_time", "@logical_time"),
            ("microstep", "@microstep")
        ]

        # Define tooltips for Reactions and Execution Events
        tooltips_actions = [
            ("name", "@name"),
            ("time_start", "@time_start{0,0.00}"),
            ("trace_event_type", "@trace_event_type"),
            ("logical_time", "@logical_time"),
            ("microstep", "@microstep")
        ]
        
        tooltips_executions = [
            ("name", "@name"),
            ("time_start", "@time_start{0,0.00}"),
            ("time_end", "@time_end{0,0.00}"),
            ("priority", "@priority"),
            ("level", "@level"),
            ("logical_time", "@logical_time"),
            ("microstep", "@microstep")
        ]
        
        # Hover tool only for instantaneous events 
        hover_tool_colours = HoverTool(tooltips=tooltips_reactions, renderers=[inst_reaction_hex_colours])
        hover_tool_arrows = HoverTool(tooltips=tooltips_reactions, renderers=[inst_reaction_hex_arrows])
        
        # Hover tool only for instantaneous events and execution event lines (so that markers for exe events dont also have a tooltip)
        hover_tool_actions_colours = HoverTool(tooltips=tooltips_actions, renderers=[inst_action_hex_colours])
        hover_tool_actions_arrows = HoverTool(tooltips=tooltips_actions, renderers=[inst_action_hex_arrows])
        hover_tool_actions_physical_time = HoverTool(tooltips=tooltips_actions, renderers=[inst_action_hex_physical_time])
        
        # Hover tool only for execution events (so that markers for exe events dont also have a tooltip)
        hover_tool_executions_colours = HoverTool(tooltips=tooltips_executions, renderers=[exe_line_colours])
        hover_tool_executions_arrows = HoverTool(tooltips=tooltips_executions, renderers=[exe_line_arrows])
        hover_tool_executions_physical_time = HoverTool(tooltips=tooltips_executions, renderers=[exe_line_physical_time])

        # Hover tool for wokers
        hover_tool_workers = HoverTool(tooltips=tooltips_executions, renderers=[workers])
        
        # Add the tools to the plot
        p_colours.add_tools(hover_tool_colours, hover_tool_actions_colours, hover_tool_executions_colours)
        p_arrows.add_tools(hover_tool_arrows, hover_tool_actions_arrows, hover_tool_executions_arrows)
        p_physical_time.add_tools(hover_tool_actions_physical_time, hover_tool_executions_physical_time)
        p_workers.add_tools(hover_tool_workers)
        
        
        # Define the tabs for each of the views
        coloured_trace = Panel(child=p_colours, title="coloured trace")
        dependencies = Panel(child=p_arrows, title="dependencies")
        physical_time = Panel(child=p_physical_time, title="physical time")
        workers = Panel(child=p_workers, title="workers")
        
        # Logic for showing different views, based on flags set by users
        if not self.diable_arrows:
            if self.plain_view and self.logic_lines_view:
                show(Tabs(tabs=[coloured_trace, dependencies, physical_time, workers]))
            elif self.logic_lines_view:
                show(Tabs(tabs=[dependencies, physical_time, workers]))
            elif self.plain_view:
                show(Tabs(tabs=[coloured_trace, dependencies, workers]))
            else:
                show(Tabs(tabs=[dependencies, workers]))
        
        else:
            if self.logic_lines_view:
                show(Tabs(tabs=[coloured_trace, physical_time, workers]))
            else:
                show(Tabs(tabs=[coloured_trace, workers]))

        # 2x exec events because of exec markers 
        total_data_points = len(self.ordered_inst_events_reactions["name"]) + len(self.ordered_inst_events_actions["name"]) + (2 * len(self.ordered_exe_events["name"]))
        print("Number of points: " + str(total_data_points))









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




    
              
    def find_dependencies(self):
        
        event_dict = self.ordered_exe_events
        
        total_dependencies = len(event_dict["logical_time"])
        current_dependency = 1
        for pos in range(len(event_dict["logical_time"])):

            event_logical_time = event_dict["logical_time"][pos]
            event_logical_microstep = event_dict["microstep"][pos]
            
            inc_index = pos + 1

            # iterate, incrementing pos
            for time in event_dict["logical_time"][inc_index:]:
                
                # logical time greater, so no dependency
                if time > event_logical_time:
                    break
                
                # if the logical time is the same, check if there is a dependency
                if time == event_logical_time and event_logical_microstep == event_dict["microstep"][inc_index]:
                    
                    event_name = event_dict["name"][pos]
                    dependent_event_name = event_dict["name"][inc_index]
                    
                    # if there is a dependency, draw an arrow
                    if dependent_event_name in self.dependency_dict[event_name]:
                        self.arrow_pos.append((event_dict["time_end"][pos], event_dict["y_axis"][pos],
                                               event_dict["time_start"][inc_index], event_dict["y_axis"][inc_index]))
                        
                        
                # increment index
                inc_index += 1
                
        
    