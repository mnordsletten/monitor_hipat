#!/usr/bin/env python
# To Do
# Version 1.1-Alpha pre release
# - Look at sorting of prints, so that they don't change order when multiple are failing at the same time.
# - Can we include when it actually failed, instead of just failing?

from local_server import local_server
from remote_server import remote_server
from config import config
from update_remote import myThread
import datetime
import subprocess
import re
import time
import os
import shelve
import socket

"""	monitor_hipat.py will create an overview over the status of the hipat system.
"""
        
def find_servers():
    """ Finds out of the server is either remote or local. Then based on the result, makes a list of IP-addresses. 
    server_objects are created from the IP-adresses and returned as a list. 
    Will now also import previously used servers from a shelvefile. Will update the name and possible remote ip for a new server.
    
    returns: list of server objects
	"""
    s = shelve.open('shelvefile.db')
    if not s.__contains__("server_list"):
        s["server_list"] = []
    
    if config["remote_status"] == "remote":
        server_ips = config['ip_address']   # List of lists containing server_ip and server_name
    elif config["remote_status"] == "local":
        ntpq_output = subprocess.check_output(['ntpq', '-pn'])
        regex = r'^.(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'   # Start of line, one character and ip address
        server_ips = re.findall(regex, ntpq_output, re.MULTILINE)
    
    server_objects = []
    for new_server in server_ips:
        previously_stored = False
        for stored_server in s["server_list"]:
            if new_server[0] == stored_server.ip_address:
                stored_server.name = new_server[1]
                stored_server.remote_ip = new_server[2]
                server_instance = stored_server
                previously_stored = True
        if config["remote_status"] == "remote" and not previously_stored:
            server_instance = remote_server(ip_address = new_server[0], name = new_server[1], remote_ip = new_server[2])
        elif config["remote_status"] == "local":
            server_instance = local_server(ip_address = new_server)
        server_objects.append(server_instance)
    
    s.close()
    return server_objects 

def print_servers(server_list):
    """Will print the server objects represented in the server_list.
    server_list: list containing the ntpq_server objects.
    """ 

    server_list.sort(key=lambda y: socket.inet_aton(y.ip_address))   # Sorting list with last_fail first
    
    # To ensure the print output is formatted correctly a few operations are performed:
    # 1. Minimum string lengths are saved in string_lengths, this is the length of the headers
    # 2. All the fields in the server objects are scanned and the length of the longest entry is saved in string_lengths
    # 3. The lengths taken from string_lengths are used in the two print statements
    string_lengths = {"name":5, "comment":7, "offset":7, "when":5, "ip_address":11} # Saves minimum length of strings
    
    # Extracts the maximum length of the various fields printed
    for variable, length in string_lengths.items(): # Loop through the different items
    	for server in server_list:                  # Loop through the different servers
    		if (len(str(vars(server)[variable]))) >= string_lengths[variable]:  # If the length of the string exceeds the saved string_length
    			string_lengths[variable] = len(str(vars(server)[variable])) + 1 # Always save the maximum string length

    # Print the header fields
    print ("{0:<{6[name]}}"
    	   "{1:<{7}} "
    	   "{2:<{6[offset]}}"
    	   "{3:<{6[when]}}"
    	   "{4:<13}"
           "{8:<13}"
    	   "{5:<{6[ip_address]}}").format("Name",
    	   									"Status",
    	   									"Offset",
    	   									"When",
    	   									"Last Failed",
    	   									"Ip address",
    	   									string_lengths,
                                            (string_lengths['comment']-1),
                                            "Last Working")
                                            
    def convert_seconds(delta):
        last_update_string = ""
        if delta < datetime.timedelta(seconds=60):  # Delta is below 1 minute
            last_update_string += str(delta.seconds) + " Second(s)"
        elif delta < datetime.timedelta(seconds=3600): # Delta is below 1 hour
            last_update_string += str(delta.seconds/60) + " Minute(s)"
        elif delta < datetime.timedelta(days=1):      # Delta is below 1 day
            last_update_string += str(delta.seconds/3600) + " Hour(s)"
        else:
            last_update_string += str(delta.days) + " Day(s)"
        return last_update_string
        
    # Loop through the servers and print the various fields
    for server in server_list:
        delta = datetime.timedelta(seconds = 0)
        last_failed_string = ""
        last_working_string = ""
        
        # Decide what the last_update_string variable will say based on the server status
        if server.status == "Init":
            last_failed_string = "Init"
            last_working_string = "Init"
        elif server.last_fail == datetime.datetime.min:
            last_failed_string = "Never"
        elif server.status == "Green" or server.status == "Yellow":
            delta = datetime.datetime.now() - server.last_fail # Calculate timedelta to last fail
            last_failed_string = convert_seconds(delta)
        elif server.status == "Red":
            if server.last_active != 0: # If server has never been active last_active is set to 0
                delta = datetime.datetime.now() - server.last_active # Calculate timedelta to last active
                last_working_string = convert_seconds(delta)
            else:
                last_working_string = "Never active "    # 
        

             
        # Will modify the background colour of the text based on the status used. 
        if server.status == "Green":
            background_colour = "\033[30;42m"   # Black text (30) on Green background (42)
        elif server.status == "Red":
            background_colour = "\033[37;41m"   # White text (37) on Red background (41)
        elif server.status == "Yellow":
            background_colour = "\033[30;43m"   # Black text (30) on Yellow Background (43)
        else:
            background_colour = ""
        
        background_colour_end = "\033[0m"
        print ("{0.name:<{4[name]}}"
        	   "{2}{0.comment:<{5}}{3} "
        	   "{0.offset:<{4[offset]}}"
        	   "{0.when:<{4[when]}}"
        	   "{1:<13}"
               "{6:<13}"
        	   "{0.ip_address:<{4[ip_address]}}").format(server, 
        	   								   		last_failed_string, 
        	   								   		background_colour, 
        	   								   		background_colour_end, 
        	   								   		string_lengths,
                                                    (string_lengths['comment'] -1),
                                                    last_working_string)

def main():
    # Get a list of servers
    server_list = find_servers()
    
    while(True):
        # Create threads for every server so that the updates happen at the same time
        for server in server_list:
            thread_update = myThread(server)    
            thread_update.start()
        time.sleep(5)
        os.system('cls' if os.name == 'nt' else 'clear')    # Clear the screen before the next print
        print_servers(server_list)                          # Print all the servers
        time.sleep(5)
        s = shelve.open('shelvefile.db')
        s["server_list"] = server_list
        s.close()
         
if __name__ == '__main__':
    main()
