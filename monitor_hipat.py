#!/usr/bin/env python

# TO DO
# subprocesses to call ntpq -p to remote sites
# ping test to remote sites to check complete status if they don't respond to ntpq -p
# Can find_servers be split up further? At least we need to expand it to find remote servers from config.txt as well.
# print_servers needs coloured text, not backgrounds.
# Can find_name be improved in local_server, this is very specialised for this function.
# general function descriptions needed for remote servers. 
# Move first part of main function (to make server_list) to find_servers. 

from local_server import local_server
from remote_server import remote_server
import datetime
import subprocess
import re
import time
import os

"""monitor_hipat.py will create an overview over the status of the hipat system."""
        
def find_servers():
    """Gets input from ntpq and returns a list of all the ip addresses."""
    
    ntpq_output = subprocess.check_output(['ntpq', '-pn'])
    regex = r'^.(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'   # Start of line, one character and ip address
    server_list = re.findall(regex, ntpq_output, re.MULTILINE)
    
    return server_list 

def print_servers(server_list):
    """Will print the server objects represented in the server_list.
    
    server_list: list containing the ntpq_server objects.
    """ 
    server_list.sort(key=lambda y: y.last_fail, reverse=True)
    print "{0:<20}{1:<8}{2:<8}{3:<10}{4:<14}{5}".format("Name", "Status", "Offset", "When", "Last Failed", "Ip address")
    for server in server_list:
        delta_last_fail = datetime.datetime.now() - server.last_fail    # Calculate timedelta to last fail
        if server.last_fail == datetime.datetime.min:
            last_fail_string = "Never Failed"
        elif delta_last_fail < datetime.timedelta(seconds=10):  # Delta is below 10 seconds
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
        print "{0.name:<20}{2}{0.status:<8}{3}{0.offset:<8}{0.when:<10}{1:<14}{0.ip_address}".format(server, last_fail_string, background_colour, background_colour_end)

        
        
def main():
    ntpq_servers = find_servers()
    server_list = []
    for server in ntpq_servers:
        server_object = local_server(ip_address=server)
        server_list.append(server_object)
    
    while(True):
        for server in server_list:
            server.update()
        os.system('cls' if os.name == 'nt' else 'clear')
        print_servers(server_list)
        time.sleep(20)
        
    ###TO DO
    # Sort print list by status. Last failed at the top

        
if __name__ == '__main__':
    main()
        
        
        