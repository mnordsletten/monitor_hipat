import subprocess, threading
from config import config
from remote_server import remote_server
import time

"""Will perform an update of the remote sites using threading. 
    1. Ping remote sites if they don't respond. 
    2. Perform ntpq -pn <ip_address> requests to remote sites.
    3. Update the remote_server objects with updated information."""
    
server_objects = []
for server in config['ip_address']:
    server_instance = remote_server(ip_address = server[0], name = server[1])
    server_objects.append(server_instance)
    
class myThread(threading.Thread):
    def __init__(self, server_object):
        threading.Thread.__init__(self)
        self.server_object = server_object
        return
        
    def run(self):
        ntpq_output = subprocess.check_output(['ntpq', '-pn', self.server_object.ip_address], stderr=subprocess.PIPE)
        self.server_object.update(ntpq_output)
        return        
    