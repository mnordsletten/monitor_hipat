from ntpq_server import ntpq_server
import subprocess

class local_server(ntpq_server):
    """local_server extends the base ntpq_server class with methods for updating a local server. It contains methods for:
    1. Updating the status (offset, when, jitter) of the individual server.
    2. Finding the name of the server in the /etc/hosts file.
    """
    
    def update(self):
        """update() will extract the important information (offset, when and jitter) from the ntpq_output.
        From a local server the ntpq output is gathered from a 'ntpq -pn' query. To insert the information in the object
        the parents update function is called. To get names of the servers another local_server method is used.
        """
        # Gather ntpq_output from the local machine
        ntpq_output = subprocess.check_output(['ntpq', '-pn'])  # Get local ntpq output
        
        # Populate the object with the info from the ntpq_output
        ntpq_server.update(self, ntpq_output, self.ip_address)
        
        # Find the name given from the /etc/hosts file.
        self.find_name()
        return
    
    def find_name(self):
        """Will search the /etc/hosts file for a name of the ip address in use. Populates the objects name field.
        """
        hosts_output = subprocess.check_output(['cat', '/etc/hosts'])
        regex = r'{0}\s+(\S+)'.format(self.ip_address)
        try:
            self.name = re.search(regex, hosts_output).group(1)
            return
        except:
            self.name = self.ip_address
            return
    
