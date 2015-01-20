from ntpq_server import ntpq_server
import subprocess

class remote_server(ntpq_server):
    """Description
    
    """
    def __init__(self, ip_address="0.0.0.0", name="init"):
    	print ip_address,
    	print name
    	
    	ntpq_server.__init__(self, ip_address)  # Call parents init server to populate all fields
    	self.name = name
    	
    	 
    def update(self):
        """update() will extract the important information (offset, when and jitter) from the ntpq_output.
        From a remote server the ntpq output is gathered from a 'ntpq -pn <ip_address>' query. To insert the information in the object
        the parents update function is called. 
        """
        # Gather ntpq_output from the remote machine
        ntpq_output = subprocess.check_output(['ntpq', '-pn', self.ip_address])  # Get remote ntpq output
        
        # Populate the object with the info from the ntpq_output
        ntpq_server.update(self, ntpq_output)
        
        return         
