#!/usr/bin/env python3
import os
from scripts.read_ctf import parser

from bokeh.palettes import Set1 as palette
import argparse
import regex
import os
import sys
import time
import pandas as pd
import holoviews as hv
from holoviews import opts
from bokeh.models import HoverTool

class holoviews_visualiser:
    
    def __init__(self, ctf_filepath, yaml_filepath):
        
        start_time = time.time()
        self.data_parser = parser()
        self.data_parser.parse(ctf_filepath, yaml_filepath)
        print("\nCTF READ TOTAL TIME: " + str(time.time() - start_time)+ "\n")
        
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

    
    
    def build_graph(self, args):
        """Builds the bokeh graph"""

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
        # Execution event markers
        exe_x_marker = [((x1 + x2)/2)
                        for x1, x2 in self.ordered_exe_events["x_multi_line"]]

        exe_y_marker = []
        for x in self.ordered_exe_events["y_axis"]:
            exe_y_marker.append(self.number_labels[x].split(".", 1)[1])
    
        

        dict_exec_markers = {"x_values": exe_x_marker,
                            "y_values": exe_y_marker,
                            "name": self.ordered_exe_events["name"],
                            "default_colours": self.ordered_exe_events["default_colours"],
                            "colours": self.ordered_exe_events["colours"],
                            "time_start" : self.ordered_exe_events["time_start"],
                            "time_end" : self.ordered_exe_events["time_end"],
                            "priority" : self.ordered_exe_events["priority"],
                            "level" : self.ordered_exe_events["level"],
                            "logical_time" : self.ordered_exe_events["logical_time"],
                            "microstep" : self.ordered_exe_events["microstep"]}
                             
        
        df_execution_events = pd.DataFrame(self.ordered_exe_events)
        df_execution_markers = pd.DataFrame(dict_exec_markers)
        df_reactions = pd.DataFrame(self.ordered_inst_events_reactions)
        df_actions = pd.DataFrame(self.ordered_inst_events_actions)

        # -------------------------------------------------------------------
         # Hover tool configuration 
        tooltips_executions = [
            ("name", "@name"),
            ("time_start", "@time_start{0,0.00}"),
            ("time_end", "@time_end{0,0.00}"),
            ("priority", "@priority"),
            ("level", "@level"),
            ("logical_time", "@logical_time"),
            ("microstep", "@microstep")
        ]

        hover = HoverTool(tooltips=tooltips_executions)
        

        # -------------------------------------------------------------------
        # Holoviews stuff

        hv.extension('bokeh')

        exe_markers = hv.Scatter(df_execution_markers, kdims=['x_values', 'y_values'], vdims=["name", "colours", "time_start", "time_end", "priority", "level", "logical_time", "microstep"]).opts(
            height=700, width=1300, color='colours', marker="diamond", tools=[hover], size=7, xformatter="%f")
        
        hv.save(exe_markers, self.graph_name + "_holoviews.html", backend='bokeh')


        
        
        
        
        
        
        
        
        
        
        
        
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


