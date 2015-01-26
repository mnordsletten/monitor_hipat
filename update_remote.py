import subprocess, threading
from config import config
from remote_server import remote_server

"""Will perform an update of the remote sites using threading. 
    1. Ping remote sites if they don't respond. 
    2. Perform ntpq -pn <ip_address> requests to remote sites.
    3. Update the remote_server objects with updated information."""
    
class Command():
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
    
    server_objects = []
    for server in config['ip_address']:
        server_instance = remote_server(ip_address = server[0], name = server[1])
        server_objects.append(server_instance)
        
    