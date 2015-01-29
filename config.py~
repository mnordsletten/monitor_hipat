import os
import re

def scan_config():
    """Will scan config.txt and extract the config items.
    The items will be added to a dictionary.
    
    return: dictionary containing the config items.
    """
    # Start by opening the config.txt file
    directory = os.path.dirname(os.path.realpath(__file__))     #Will return the directory regardless of where the script is run from
    config_file = os.path.join(directory, 'config.txt')         #Appends config.txt to the directory
    file = open(config_file, 'r')
    
    # Read every line extracting the necessary information
    config = {"ip_address":[]}  # config is preconfigured with a field for ip_address
    for line in file:
        if line[0] == "#":  # All comment lines are ignored
            continue
        match = re.search('(\w+):\s(.+)', line) # Regex search for matches
        if match:
            config_item = match.group(1)        # Extract the config_item
            config_value = match.group(2)       # Extract the config value
            
            if config_item == "ip_address":     # If we are dealing with an ip address both the name and ip must be saved
                ip_match = re.search("(\S+):(\S+)", config_value)   # One group for ip and one for name
                config["ip_address"].append([ip_match.group(1), ip_match.group(2)]) # Append ip and name as a list to the ip_address list in the config dict
                continue                        # Ip address has already been saved so we continue the loop
                
            config[config_item] = config_value  # All normal items are saved here
            
    file.close()
    return config
    
config = scan_config()
