#!/usr/bin/env python

import datetime
import subprocess
import re
import time
import os

"""monitor_hipat.py will create an overview over the status of the hipat system."""

class ntpq_server():
    
    def __init__(self, name="test1", ip_address="10.0.23.1"):
        """Initializing the ntpq_server"""
        self.name = name
        self.ip_address = ip_address
        self.offset = 0.0
        self.when = 0.0
        self.jitter = 0.0
        self.status = 0
        self.last_fail = datetime.datetime.min
        
    def __str__(self):
        return ("Name: {0} \n"
                "Ip Address: {1} \n"
                "Offset: {2} \n"
                "When: {3} \n"
                "Jitter: {4} \n"
                "Status: {5} \n"
                "Last Fail: {6}").format(self.name, 
                                         self.ip_address,
                                         self.offset,
                                         self.when,
                                         self.jitter,
                                         self.status,
                                         self.last_fail)
                                                                        
    def update(self):
        
        ntpq_output = subprocess.check_output(['ntpq', '-pn'])
        regex = (   '(?P<ref_server>{0})\s+'# ref_server
                    '(?P<refid>\S+)\s+'     # refid 
                    '(?P<st>\S+)\s+'        # stratum
                    '(?P<t>\S+)\s+'         # type of server
                    '(?P<when>\S+)\s+'      # when, time since last update
                    '(?P<poll>\S+)\s+'      # poll, how often it is polled
                    '(?P<reach>\S+)\s+'     # how reliable the server is
                    '(?P<delay>\S+)\s+'     # time in ms to the server
                    '(?P<offset>\S+)\s+'    # offset to server in ms
                    '(?P<jitter>\S+)\s+'    # jitter of the server
        ).format(self.ip_address)
        output = re.search(regex, ntpq_output, re.MULTILINE)    # search for the line
    
        arguments_wanted = {'offset': True, 'when': True, 'jitter': True}
        
        return_output = {}  # A dict used for return values, it's size varies with what the user wants returned.
        for argument, value in arguments_wanted.iteritems():    # loop through the arguments provided, processing the ones that are True.
            if argument.lower() == 'when' and value == True:
                when_output = output.group('when')          # A test is made to see if the when variable is using m: minutes, h: hours, d: days
                if when_output == '-':
                    when_output = 0
                elif when_output[-1] == 'm':
                    when_output = float(when_output[:-1]) * 60
                elif when_output[-1] == 'h':
                    when_output = float(when_output[:-1]) * 3600
                elif when_output[-1] == 'd':
                    when_output = float(when_output[:-1]) * 86400
                return_output['when'] = float(when_output)
            elif value == True: # All True values will be processed here.
                try:
                    return_output[argument.lower()] = float(output.group(argument.lower()))
                except ValueError:  # If they contain string only characters they are exported as strings. 
                    return_output[argument.lower()] = output.group(argument.lower())
                except IndexError:  # If an argument is not found in the regex results.
                    continue
        
        self.offset = return_output["offset"]
        self.when = return_output["when"]
        self.jitter = return_output["jitter"]
        self.find_name()
        self.find_status()
        
        return
    
    def find_name(self):
        """Will search the /etc/hosts file for a name of the ip address in use.
        """
        hosts_output = subprocess.check_output(['cat', '/etc/hosts'])
        regex = r'{0}\s+(\S+)'.format(self.ip_address)
        try:
            self.name = re.search(regex, hosts_output).group(1)
            return
        except:
            self.name = self.ip_address
            return
    
    def find_status(self):
        """Will process what the status of the ntpq_server is based on the available data.
        """
        offset = abs(self.offset)   # Get positive value of offset
        if (self.when < 120 and 10 < offset < 5):
            self.status = "Yellow"
        elif (self.when > 120 or offset > 5):
            self.status = "Red"
            self.last_fail = datetime.datetime.now()
        else:
            self.status = "Green"
            
        return       
        
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
        server_object = ntpq_server(ip_address=server)
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
        
        
        