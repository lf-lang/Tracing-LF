#!/usr/bin/env python3
from Parser.parse_files import parser


class holoviews_visualiser:
    
    def __init__(self, json_filepath, yaml_filepath):

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

        # Dictionary containing all dependencies between reactions
        self.dependency_dict = self.data_parser.get_dependency_dict()

        # List containing all reaction names
        self.action_names = self.data_parser.get_action_names()

        # List containing 4-tuples for arrow drawing
        self.arrow_pos = []

        # Stores whether to show coloured graph
        self.diable_arrows = False

        # Graph name
        self.graph_name = self.data_parser.get_main_reactor_name()

    def build_graph(self, args):
        """Builds the bokeh graph"""

        # Include/Exclude Reactions
        parser = argparse.ArgumentParser()
        parser.add_argument("tracefile", type=str,
                            help="Path to the .json trace file")
        parser.add_argument("yamlfile", type=str,
                            help="Path to the .yaml file")
        parser.add_argument("-i", "--include", type=str,
                            help="Regex to INCLUDE only certain reactors or reactions")
        parser.add_argument("-x", "--exclude", type=str,
                            help="Regex to EXCLUDE certain reactors or reactions")
        args = parser.parse_args()

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

        # Find all possible logical times and give these a colouring
        action_logic_times = set(zip(
            self.ordered_inst_events_actions["logical_time"], self.ordered_inst_events_actions["microstep"]))

        reaction_logic_times = set(zip(
            self.ordered_inst_events_reactions["logical_time"], self.ordered_inst_events_reactions["microstep"]))

        execution_logic_times = set(zip(
            self.ordered_exe_events["logical_time"], self.ordered_exe_events["microstep"]))

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
                logic_time_tuple = (
                    dictonary["logical_time"][pos], dictonary["microstep"][pos])
                dictonary["colours"][pos] = logical_colours_dict[logic_time_tuple]

        # -------------------------------------------------------------------
