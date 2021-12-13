import yaml


class analyse_lf:
    """ Can be used to parse yaml files generated from LF programs (currently only in the C++ target) with the 'export-to-yaml' option set to true. \n
        Allows parsing of the yaml file"""
        
    def __init__(self, filepath):
        # Open yaml file and parse with pyyaml
        self.data = yaml.load(open(filepath), Loader=yaml.FullLoader)
        
        self.reaction_dict = []
    
        # 
        reactor_instances = self.data['all_reactor_instances']
    
        # Delete the first item in the dict
        del reactor_instances[next(iter(reactor_instances))]
        
               
        # Iterate through dict
        for reactor in reactor_instances.items():
            reactor_name = reactor[0]
            for reaction in reactor[1]["reactions"]:
                print(reaction["priority"])
                reaction_name = reactor_name + "." + reaction["name"]
                self.reaction_dict[str(reaction_name)] = []
                
            
            
            
            
    
        
        
test = analyse_lf("YamlFiles/ReflexGame.yaml")
        


        
