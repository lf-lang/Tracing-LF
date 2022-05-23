#!/usr/bin/python

# Copyright (C) 2020 TU Dresden
# All rights reserved.
#
# Authors:
#   Christian Menard



import bt2
from collections import defaultdict
import yaml
import itertools
import time


pid_registry = {}
tid_registry = {}

class parser:

    def get_ids(self, process, thread):
        if process not in pid_registry:
            pid_registry[process] = len(pid_registry) + 1
            tid_registry[process] = {}
        pid = pid_registry[process]
        tid_reg = tid_registry[process]
        if thread not in tid_reg:
            tid_reg[thread] = len(tid_reg)
        tid = tid_reg[thread]
        return pid, tid


    def parse(self, ctf_path, yaml_filepath):
        
        # Variables
        self.x_offset = 0

        # List of reactions which have no triggers or effects, which are removed from the visualisation
        self.redundant_reactions = []

        # Parse the YAML data from the file
        self.parse_yaml(yaml_filepath)
        self.yaml_data = self.reaction_dict

        # list of reactor names - [reactor.name0, reactor.name1, ...]
        self.y_axis_labels = []

        # list of axis labels to assign reactor names to y-values {reactor.name0 : 0, reactor.name1 : 1, ...}
        # Solves problem: https://github.com/bokeh/bokeh/issues/6907
        self.reactor_number = {}

        # reversal of reactor_number
        self.number_label = {}

        # Get first reaction
        self.start_time = 0
        self.start_time_logical = 0

        # Find the `ctf` plugin (shipped with Babeltrace 2).
        ctf_plugin = bt2.find_plugin('ctf')

        # Get the `source.ctf.fs` component class from the plugin.
        fs_cc = ctf_plugin.source_component_classes['fs']

        # Create a trace collection message iterator, instantiating a single
        # `source.ctf.fs` component class with the `inputs` initialization
        # parameter set to open a single CTF trace.
        msg_it = bt2.TraceCollectionMessageIterator(bt2.ComponentSpec(fs_cc, {
            # Get the CTF trace path from the first command-line argument.
            'inputs': [ctf_path],
        }))

        msg_it1, msg_it2, msg_it3 = itertools.tee(msg_it, 3)
        
        # Dictonary to match pairs of execution messages
        execution_messages_dict = {}
        
        # Dictionary containing all compiled data for each instantaneous event execution (reactions)
        # Note: time_start is used for the x-axis, y-axis is the y value which is later substituted for a reaction name
        self.ordered_inst_events_reactions = {"name": [], "reactor": [], "reaction": [], "time_start": [], "time_end": [], "trace_event_type": [], "y_axis": [],
                                              "priority": [], "level": [], "triggers": [], "effects": [], "logical_time": [], "microstep": []}

        # Dictionary containing all compiled data for each instantaneous event execution
        self.ordered_inst_events_actions = {"name": [], "reactor": [], "reaction": [], "time_start": [], "time_end": [],
                                            "trace_event_type": [], "y_axis": [], "effects": [], "triggers": [], "logical_time": [], "microstep": []}

        # Dictionary containing all compiled data for each execution event execution
        # x_multi_line and y_multi_line contain nested lists with start and end x and y values respectively. These are used to draw the multilines
        self.ordered_exe_events = {"name": [], "time_start": [], "time_end": [], "trace_event_type": [], "priority": [], "level": [], "triggers": [],
                                "effects": [], "x_multi_line": [], "y_multi_line": [], "y_axis": [], "logical_time": [], "microstep": []}

        
        # Get the start times
        for msg in msg_it1:
            # `bt2._EventMessageConst` is the Python type of an event message.
            if type(msg) is bt2._EventMessageConst:
                self.start_time = self.get_timestamp_us(msg)
                self.start_time_logical = int(msg.event["timestamp_ns"])
                break
        
        # Get the labels of all reactions
        for msg in msg_it2:
            # `bt2._EventMessageConst` is the Python type of an event message.
            if type(msg) is bt2._EventMessageConst:
                event = msg.event
                if (event.name == "reactor_cpp:schedule_action"):
                    event_name = str(event["reactor_name"]) + "." + str(event["action_name"])
                    if not event_name in self.redundant_reactions:
                        self.add_to_reaction_labels(event_name)
                
                if (event.name == "reactor_cpp:trigger_reaction"):
                    event_name = str(event["reactor_name"]) + "." + str(event["reaction_name"])
                    if not event_name in self.redundant_reactions:
                        self.add_to_reaction_labels(event_name)
                
        
        # inverse of number_label dictionary. Gives the y-value (height) of the given reaction
        self.reactor_number = {v: k for k, v in self.number_label.items()}

        # Iterate the trace messages
        for msg in msg_it3:

            # `bt2._EventMessageConst` is the Python type of an event message.
            if type(msg) is bt2._EventMessageConst:
                
                event = msg.event
                
                if (event.name == "reactor_cpp:reaction_execution_starts"):
                    
                    # Add the starting information to the dictionary
                    execution_messages_dict[str(event["reaction_name"])] = msg
                    
                elif (event.name == "reactor_cpp:reaction_execution_finishes"):
                    
                    msg_e = execution_messages_dict[str(event["reaction_name"])]
                    
                    self.write_execution_to_dict(msg_e, msg)
                
                elif (event.name == "reactor_cpp:schedule_action"):
                    
                    self.write_to_dict(msg, False)
                
                elif (event.name == "reactor_cpp:trigger_reaction"):
                    
                    self.write_to_dict(msg, True)

        # order data for multiline graph
        for start_time, end_time in zip(self.ordered_exe_events["time_start"], self.ordered_exe_events["time_end"]):
            self.ordered_exe_events["x_multi_line"].append(
                [start_time, end_time])

        for y_value in self.ordered_exe_events["y_axis"]:
            self.ordered_exe_events["y_multi_line"].append(
                [y_value, y_value])



    def get_timestamp_us(self, msg):
        timestamp_ns = msg.default_clock_snapshot.ns_from_origin
        return timestamp_ns / 1000.0

    def write_execution_to_dict(self, msg_b, msg_e):
        # msg_b - beginning message 
        # msg_e - end message
        
        event_b = msg_b.event
        
        rec_name = str(event_b["reaction_name"])
        
        rev_name = rec_name[::-1]
        a, b = rev_name.split(".", 1)
        reactor_name = b[::-1]
        reaction_name = a[::-1]

        # leave function if reaction is redundant
        if rec_name in self.redundant_reactions:
            return
        
        reaction_yaml_data = self.yaml_data[reactor_name][reaction_name]
        
        self.ordered_exe_events["name"].append(rec_name)
        self.ordered_exe_events["time_start"].append(self.get_timestamp_us(msg_b) - self.start_time)
        self.ordered_exe_events["time_end"].append(self.get_timestamp_us(msg_e) - self.start_time)
        self.ordered_exe_events["y_axis"].append(self.reactor_number[rec_name])
        self.ordered_exe_events["trace_event_type"].append("execution")
        self.ordered_exe_events["logical_time"].append(int(event_b["timestamp_ns"]) - self.start_time_logical)
        self.ordered_exe_events["microstep"].append(
            int(event_b["timestamp_microstep"]))

        # YAML Data
        attribute_list = ["priority",
                        "level", "triggers", "effects"]
        # YAML Data
        for attribute in attribute_list:
            if attribute in reaction_yaml_data:
                self.ordered_exe_events[attribute].append(
                    reaction_yaml_data[attribute])
            else:
                self.ordered_exe_events[attribute].append("n.a.")
        
        
    def write_to_dict(self, msg, is_reaction):
        event = msg.event
        
        # name and timestart of reaction
        reactor_name = str(event["reactor_name"])
        reaction_name = ""
        ordered_inst_events_dict = {}
        
        if is_reaction:
            reaction_name = str(event["reaction_name"])
            ordered_inst_events_dict = self.ordered_inst_events_reactions
        else:
            reaction_name = str(event["action_name"])
            ordered_inst_events_dict = self.ordered_inst_events_actions

        reactor_reaction_name = reactor_name + "." + reaction_name
        
        # leave function if reaction is redundant
        if reactor_reaction_name in self.redundant_reactions:
            return
        
        time_start = float(event["timestamp_ns"]) - self.start_time_logical

        reaction_yaml_data = self.yaml_data[reactor_name][reaction_name]

        # special case for startup and shutdown
        if not is_reaction:
            if reaction_yaml_data["type"] == "startup" or reaction_yaml_data["type"] == "shutdown":
                is_reaction = True
                ordered_inst_events_dict = self.ordered_inst_events_reactions

        ordered_inst_events_dict["name"].append(reactor_reaction_name)
        ordered_inst_events_dict["reactor"].append(reactor_name)
        ordered_inst_events_dict["reaction"].append(reaction_name)
        ordered_inst_events_dict["time_start"].append(time_start)
        ordered_inst_events_dict["time_end"].append(time_start)  # same for instant events
        ordered_inst_events_dict["y_axis"].append(self.reactor_number[reactor_reaction_name] + self.x_offset)
        ordered_inst_events_dict["effects"].append(reaction_yaml_data["effects"])
        ordered_inst_events_dict["triggers"].append(reaction_yaml_data["triggers"])
        ordered_inst_events_dict["logical_time"].append(int(event["timestamp_ns"])- self.start_time_logical)
        ordered_inst_events_dict["microstep"].append(int(event["timestamp_microstep"]))
        
        if is_reaction:
            ordered_inst_events_dict["trace_event_type"].append("reaction")
            
            # YAML Data
            attribute_list = ["priority", "level"]
            
            for attribute in attribute_list:
                if attribute in reaction_yaml_data:
                    ordered_inst_events_dict[attribute].append(reaction_yaml_data[attribute])
                else:
                    ordered_inst_events_dict[attribute].append("n.a.")
            
        else:
            ordered_inst_events_dict["trace_event_type"].append(
                reaction_yaml_data["type"])
        
    
    def add_to_reaction_labels(self, event_name):
        if event_name not in self.y_axis_labels:
            self.number_label[len(
                self.y_axis_labels)] = event_name

            # Add reactor name to list
            self.y_axis_labels.append(event_name)
    
    
    def parse_yaml(self, filepath):
        # Structure: Nested dict of reactions
        # {reactor : {reaction : {attribute : value}}}
        self.reaction_dict = {}

        # Dictionary of inputs and their triggers/effects
        input_output_dict = {}

        # List containing the name of all reactions
        self.action_names = []

        # Open yaml file and parse with pyyaml
        yaml_data = yaml.load(open(filepath), Loader=yaml.FullLoader)

        self.reactor_name = yaml_data["top_level_instances"][0]

        # Iterate through reactors and get reactions
        for reactor, items in yaml_data['all_reactor_instances'].items():

            if reactor not in self.reaction_dict:
                self.reaction_dict[reactor] = {}

            # For each reaction, add it to the list of reactions
            if items["reactions"] is not None:
                for reaction in items["reactions"]:

                    self.reaction_dict[reactor][reaction["name"]] = reaction   

                    if reaction["triggers"] is None:
                        if reaction["effects"] is None:
                            self.redundant_reactions.append(reactor + "." + reaction["name"])

            if items["triggers"] is not None:
                for trigger in items["triggers"]:

                    # rename trigger_of and event_of for clarity
                    trigger["triggers"] = trigger.pop("effect_of")
                    trigger["effects"] = trigger.pop("trigger_of")

                    self.reaction_dict[reactor][trigger["name"]] = trigger

                    # add all logical and physical actions to a list
                    action_name = reactor + "." + trigger["name"]
                    if action_name not in self.action_names and "action" in trigger["type"]:
                        self.action_names.append(action_name)
                    
                    if trigger["triggers"] is None:
                        if trigger["effects"] is None:
                            self.redundant_reactions.append(action_name)

            # For each input, add it to the input & output dictionary
            if items["inputs"] is not None:
                for input, values in items["inputs"].items():
                    port_name = reactor + "." + str(input)

                    values["port_name"] = port_name
                    input_output_dict[port_name] = values

            # For each input, add it to the input & output dictionary
            if items["outputs"] is not None:
                for output, values in items["outputs"].items():
                    port_name = reactor + "." + str(output)

                    values["port_name"] = port_name
                    input_output_dict[port_name] = values

        # Add all reaction dependencies to data structure
        self.dependency_dict = defaultdict(list)
        dependencies_iter = iter(yaml_data['reaction_dependencies'])
        for item in dependencies_iter:
            from_item = item["from"]
            to_item = next(dependencies_iter)["to"]
            self.dependency_dict[to_item].append(from_item)

        # Iterate through inputs_outputs_dict, discover chain such that:
        # Reaction_i -> output -> input -> Reaction_j
        # Where reaction_i triggers reaction_j
        self.port_dict = defaultdict(list)

        for port in input_output_dict.values():
            # Find an output port (without and upstream port)
            if port["upstream_port"] is None and port["downstream_ports"] is not None:

                # Find the corresponding downstream ports (inputs)
                downstream_ports = port["downstream_ports"]
                for item in downstream_ports:
                    port_triggers = input_output_dict[item]["trigger_of"]

                    # Simple Case: Reaction -> output_port -> input_port -> Reaction
                    if port_triggers is not None:
                        self.port_dict[port["port_name"]].extend(port_triggers)

                    # Complex Case: Reaction -> output_port -> ?ports? -> input_port -> Reaction
                    else:
                        downstream_ports.extend(
                            input_output_dict[item]["downstream_ports"])



    def get_ordered_inst_events_reactions(self):
        return self.ordered_inst_events_reactions

    def get_ordered_inst_events_actions(self):
        return self.ordered_inst_events_actions

    def get_ordered_exe_events(self):
        return self.ordered_exe_events

    def get_y_axis_labels(self):
        return self.y_axis_labels

    def get_number_label(self):
        return self.number_label

    def get_port_dict(self):
        return self.port_dict

    def get_action_names(self):
        return self.action_names

    def get_dependency_dict(self):
        return self.dependency_dict

    def get_main_reactor_name(self):
        return self.reactor_name
    
    def get_reaction_pos(self, reaction_name, prev_reaction_time, react_dict):
        '''Given some reaction and its start time, find its position in the dictionary of reactions'''

        reaction_pos = None

        for i in range(len(react_dict["name"])):

            # Time of the current reaction
            i_time = react_dict["time_start"][i]

            # Find the first reaction which matches the given name and has a start time greater than the given time
            if i_time >= prev_reaction_time:
                i_name = react_dict["name"][i]
                if reaction_name == i_name:
                    reaction_pos = i
                    break

        return reaction_pos

if(__name__ == "__main__"):
    data_parser = parser()
    data_parser.parse()