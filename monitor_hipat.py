#!/usr/bin/env python
# Version 2.1
# To Do
# - Look at sorting of prints, so that they don't change order when multiple are failing at the same time.
# - Can we include when it actually failed, instead of just failing?
# - Variable length to the comment/status field?

from local_server import local_server
from remote_server import remote_server
from config import config
from update_remote import myThread
import datetime
import subprocess
import re
import time
import os

"""	monitor_hipat.py will create an overview over the status of the hipat system.
"""
        
def find_servers():
    """ Finds out of the server is either remote or local. Then based on the result, makes a list of IP-addresses. 
    server_objects are created from the IP-adresses and returned as a list. 
    
    returns: list of server objects
	"""
    if config["remote_status"] == "remote":
        server_ips = config['ip_address']   # List of lists containing server_ip and server_name
    elif config["remote_status"] == "local":
        ntpq_output = subprocess.check_output(['ntpq', '-pn'])
        regex = r'^.(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'   # Start of line, one character and ip address
        server_ips = re.findall(regex, ntpq_output, re.MULTILINE)
    
    server_objects = []
    for server in server_ips:
        if config["remote_status"] == "remote":
            server_instance = remote_server(ip_address = server[0], name = server[1])
        elif config["remote_status"] == "local":
            server_instance = local_server(ip_address = server)
        server_objects.append(server_instance)
    
    return server_objects 

def print_servers(server_list):
    """Will print the server objects represented in the server_list.
    server_list: list containing the ntpq_server objects.
    """ 
    server_list.sort(key=lambda y: y.last_fail, reverse=True)
    
    string_lengths = {"name":5, "comment":7, "offset":7, "when":5, "last_fail":12, "ip_address":11}
    
    for variable, length in string_lengths.items():
    	for server in server_list:
    		# print "Variable:{0} Length:{1} Server:{2}".format(variable, length, vars(server)[variable])
    		if (len(str(vars(server)[variable]))) > length:
    			string_lengths[variable] = len(str(vars(server)[variable])) + 1    
    

    
    print ("{0:<{6[name]}}"
    	   "{1:<{6[comment]}}"
    	   "{2:<{6[offset]}}"
    	   "{3:<{6[when]}}"
    	   "{4:<{6[last_fail]}}"
    	   "{5:<{6[ip_address]}}").format("Name",
    	   									"Status",
    	   									"Offset",
    	   									"When",
    	   									"Last Failed",
    	   									"Ip address",
    	   									string_lengths)
    for server in server_list:
        delta_last_fail = datetime.datetime.now() - server.last_fail    # Calculate timedelta to last fail
        if server.status == "Init":
            last_fail_string = "Init"
        elif server.last_fail == datetime.datetime.min:
            last_fail_string = "Never Failed"
        elif delta_last_fail < datetime.timedelta(seconds=10) or server.status == "Red":  # Delta is below 10 seconds
            last_fail_string = "Failing"
        elif delta_last_fail < datetime.timedelta(seconds=60):  # Delta is below 1 minute
            last_fail_string = str(delta_last_fail.seconds) + " Seconds"
        elif delta_last_fail < datetime.timedelta(seconds=3600): # Delta is below 1 hour
            last_fail_string = str(delta_last_fail.seconds/60) + " Minutes"
        elif delta_last_fail < datetime.timedelta(days=1):      # Delta is below 1 day
            last_fail_string = str(delta_last_fail.seconds/3600) + " Hours"
        else:
            last_fail_string = str(delta_last_fail.days) + " Days"
        
        # Will modify the background colour of the text based on the status used. Confirmed to work on a Mac
        if server.status == "Green":
            background_colour = "\033[30;42m"   # Black text (30) on Green background (42)
        elif server.status == "Red":
            background_colour = "\033[41m"      # Red background (41)
        elif server.status == "Yellow":
            background_colour = "\033[30;43m"   # Black text (30) on Yellow Background (43)
        else:
            background_colour = ""
        
        background_colour_end = "\033[0m"
        print ("{0.name:<{4[name]}}"
        	   "{2}{0.comment:<{4[comment]}}{3}"
        	   "{0.offset:<{4[offset]}}"
        	   "{0.when:<{4[when]}}"
        	   "{1:<{4[last_fail]}}"
        	   "{0.ip_address:<{4[ip_address]}}").format(server, 
        	   								   		last_fail_string, 
        	   								   		background_colour, 
        	   								   		background_colour_end, 
        	   								   		string_lengths)

def main():
    # Get a list of servers
    server_list = find_servers()
    
    while(True):
        # Create threads for every server so that the updates happen at the same time
        for server in server_list:
            thread_update = myThread(server)    
            thread_update.start()   
        time.sleep(2)                                       # Wait 2 seconds for the update to finish
        os.system('cls' if os.name == 'nt' else 'clear')    # Clear the screen before the next print
        print_servers(server_list)                          # Print all the servers
        time.sleep(20)
        
if __name__ == '__main__':
    main()
