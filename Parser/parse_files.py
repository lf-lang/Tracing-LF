from collections import defaultdict
import json
import yaml


class parser:
    
    def parse(self, yaml_filepath, json_filepath):

        # Variables
        self.x_offset = 0.15
        
        self.parse_yaml(yaml_filepath)
        yaml_data = self.reaction_dict
        json_data = self.parse_json(json_filepath)
        
        # list of reactor names - [reactor.name0, reactor.name1, ...]
        self.y_axis_labels = []

        # list of axis labels to assign reactor names to y-values {reactor.name0 : 0, reactor.name1 : 1, ...}
        # Solves problem: https://github.com/bokeh/bokeh/issues/6907
        self.reactor_number = {}
        
        # reversal of reactor_number
        self.number_label = {}
        
        # Get reactor number and label, as well as setting timestamps to begin at 0
        
        # Get first reaction 
        start_time = json_data["traceEvents"][0]["ts"]
        
        # Axis time scaling
        # end_tine = json_data["traceEvents"][-1]["ts"]
        # if end_time - start_time > :
            
        
        for item in json_data["traceEvents"]:
            
            # set new start time
            current_start_time = item["ts"]
            item["ts"] = current_start_time - start_time
            
            # add reaction to reactions
            if item["reactor"] != "Execution":
                reaction_name = item["reactor"] + "." + item["reaction"]
                
                if reaction_name not in self.y_axis_labels:
                    self.number_label[len(
                        self.y_axis_labels)] = reaction_name

                    # Add reactor name to list
                    self.y_axis_labels.append(reaction_name)
                
        # inverse of number_label dictionary
        self.reactor_number = {v: k for k, v in self.number_label.items()}
        
        # Dictionary containing all compiled data for each instantaneous event execution (reactions)
        # Note: time_start is used for the x-axis, y-axis is the y value which is later substituted for a reaction name
        self.ordered_inst_events_reactions = {"name": [], "reactor": [], "reaction": [], "time_start": [], "time_end": [],
                                              "trace_event_type": [], "y_axis": [], "priority": [], "level": [], "triggers": [], "effects": []}
        
        # Dictionary containing all compiled data for each instantaneous event execution
        self.ordered_inst_events_actions = {"name": [], "reactor": [], "reaction": [], "time_start": [], "time_end": [],
                                            "trace_event_type": [], "y_axis": [], "effects": [], "triggers": []}

        # Dictionary containing all compiled data for each execution event execution
        # x_multi_line and y_multi_line contain nested lists with start and end x and y values respectively. These are used to draw the multilines
        self.ordered_exe_events = {"name": [], "time_start": [], "time_end": [], "trace_event_type": [], "priority": [],
                                        "level": [], "triggers": [], "effects": [], "x_multi_line": [], "y_multi_line": [], "y_axis": []}

        # YAML attribute list
        attribute_list = ["priority", "level", "triggers", "effects"]


        # Iterate through all recorded reactions and order into dicts
        json_data_iterator = iter(json_data["traceEvents"])
        for item in json_data_iterator:
            
            reactor_name = item["reactor"]
            reaction_name = item["reaction"]
            reactor_reaction_name = reactor_name + "." + reaction_name
            time_start = item["ts"]
            # time_start = item["args"]["timestamp_ns"]
            
            
            # Execution events (not instantaneous)
            if item["reactor"] == "Execution":
            
                # Extract reactor and reaction name from trace (reverse the string, everything before "." is the reaction name)
                rev_name = item["name"][::-1]
                a, b = rev_name.split(".", 1)
                current_reactor_name = b[::-1]
                current_reaction_name = a[::-1]
            
                
                reaction_yaml_data = yaml_data[current_reactor_name][current_reaction_name]

                # JSON Data
                self.ordered_exe_events["name"].append(item["name"])
                self.ordered_exe_events["time_start"].append(time_start)
                self.ordered_exe_events["y_axis"].append(
                    self.reactor_number[item["name"]])
                self.ordered_exe_events["trace_event_type"].append("execution")

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


                # Get end time of event by going to the next json event (start and end events are distinct)
                try:
                    next_reaction = next(json_data_iterator)
                    self.ordered_exe_events["time_end"].append(
                        next_reaction["ts"])

                # If no end event exists, add end time as same timestamp (i.e. the last element of time_start)
                except StopIteration as e:
                    self.ordered_exe_events["time_end"].append(
                        self.ordered_exe_events["time_start"][-1])

            # All other events from the trace
            else:
                
                reaction_yaml_data = yaml_data[reactor_name][reaction_name]
                
                # If the the event is an action, add to self.ordered_inst_events_actions
                if "type" in reaction_yaml_data and (reaction_yaml_data["type"] == "logical action" or reaction_yaml_data["type"] == "physical action"):
                    # JSON Data
                    self.ordered_inst_events_actions["name"].append(reactor_reaction_name)
                    self.ordered_inst_events_actions["reactor"].append(reactor_name)
                    self.ordered_inst_events_actions["reaction"].append(reaction_name)
                    self.ordered_inst_events_actions["time_start"].append(time_start)
                    self.ordered_inst_events_actions["time_end"].append(time_start)   #same for instant events
                    self.ordered_inst_events_actions["trace_event_type"].append(reaction_yaml_data["type"])
                    self.ordered_inst_events_actions["y_axis"].append(self.reactor_number[reactor_reaction_name] + self.x_offset)  # Add some to display 0.25 above and make room
                    self.ordered_inst_events_actions["effects"].append(reaction_yaml_data["effects"])
                    self.ordered_inst_events_actions["triggers"].append(
                        reaction_yaml_data["triggers"])

                
                # If the the event is a reaction, add to self.ordered_inst_events_reactions
                else:
                    # JSON Data
                    self.ordered_inst_events_reactions["name"].append(reactor_reaction_name)
                    self.ordered_inst_events_reactions["reactor"].append(reactor_name)
                    self.ordered_inst_events_reactions["reaction"].append(reaction_name)
                    self.ordered_inst_events_reactions["time_start"].append(time_start)
                    self.ordered_inst_events_reactions["time_end"].append(time_start)  # start and end is the same for instant events
                    self.ordered_inst_events_reactions["trace_event_type"].append("reaction")
                    self.ordered_inst_events_reactions["y_axis"].append(self.reactor_number[reactor_reaction_name] + self.x_offset)  # Add some to display 0.25 above and make room

                    # YAML Data
                    for attribute in attribute_list:
                        if attribute in reaction_yaml_data:
                            self.ordered_inst_events_reactions[attribute].append(reaction_yaml_data[attribute])
                        else:
                            self.ordered_inst_events_reactions[attribute].append("n.a.")
         
            
        # order data for multiline graph
        for start_time, end_time in zip(self.ordered_exe_events["time_start"], self.ordered_exe_events["time_end"]):
            self.ordered_exe_events["x_multi_line"].append(
                [start_time, end_time])

        for y_value in self.ordered_exe_events["y_axis"]:
            self.ordered_exe_events["y_multi_line"].append(
                [y_value, y_value])
                
        



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

        # Iterate through reactors and get reactions
        for reactor, items in yaml_data['all_reactor_instances'].items():

            if reactor not in self.reaction_dict:
                self.reaction_dict[reactor] = {}

            # For each reaction, add it to the list of reactions
            if items["reactions"] is not None:
                for reaction in items["reactions"]:

                    self.reaction_dict[reactor][reaction["name"]] = reaction
                    

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
                        
                        
                
           

                

        
    
    def parse_json(self, filepath):
        data = json.load(open(filepath))
        return data
    
    
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