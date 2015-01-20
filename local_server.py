from ntpq_server import ntpq_server
import re
import subprocess

class local_server(ntpq_server):
    """local_server extends the base ntpq_server class with methods for updating a local server. It contains methods for:
    1. Call the parents init method and find the name of the server.
    2. Updating the status (offset, when, jitter) of the individual server.
    """
    
    def __init__(self, ip_address="0.0.0.0"):
        """Will call parents __init__ class. Will also add a name to the object."""
        
        ntpq_server.__init__(self, ip_address)  # Call parents init server to populate all fields
        self.remote = False                     # Set remote field to false
        
        # Find a name from /etc/hosts
        hosts_output = subprocess.check_output(['cat', '/etc/hosts'])   
        regex = r'{0}\s+(\S+)'.format(self.ip_address)  # Find the name corresponding to the ip address.
        try:
            self.name = re.search(regex, hosts_output).group(1) # If the name is found it is saved
            return
        except:
            self.name = self.ip_address # If no name is found the ip address is put in it's place
            return
    
    def update(self):
        """update() will extract the important information (offset, when and jitter) from the ntpq_output.
        From a local server the ntpq output is gathered from a 'ntpq -pn' query. To insert the information in the object
        the parents update function is called.
        """
        # Gather ntpq_output from the local machine
        ntpq_output = subprocess.check_output(['ntpq', '-pn'])  # Get local ntpq output
        
        # Populate the object with the info from the ntpq_output
        ntpq_server.update(self, ntpq_output, self.ip_address)
        
        return  