from ntpq_server import ntpq_server
import subprocess

class remote_server(ntpq_server):
    """ remote_server extends the base ntpq_server class with methods for updating a remote server. It contains methods for:
    1. Call the parents init method and set the name of the server.
    2. Updating the status (offset, when, jitter) of the individual server while performing a remote NTPQ-query.   
    """
    def __init__(self, ip_address="0.0.0.0", name="init"):
      	
    	ntpq_server.__init__(self, ip_address)  # Call parents init server to populate all fields
    	self.name = name # Set name
        self.hipat_status = False
        self.net_status = False
        self.cesium_status = False
    
    def __str__(self):
        return ("{0}"
                "Hipat_status: {1} \n"
                "Net_status: {2} \n"
                "Cesium_status: {3}").format(ntpq_server.__str__(self),
                                                self.hipat_status,
                                                self.net_status,
                                                self.cesium_status)
    	
    	 
    def update(self):
        """ update() will extract the important information (offset, when and jitter) from the ntpq_output. 
        From a remote server the ntpq output is gathered from a 'ntpq -pn <ip_address>' query. To insert the information in the object
        the parents update function is called. 
        """
        # ntpq_output is found and stderr is piped
        ntpq_output = subprocess.check_output(['ntpq', '-pn', self.ip_address], stderr=subprocess.PIPE) 
        
        # Check ntpq_output, if this is emtpy it means that no output was received from the 'ntpq -pn' query.                 
        if ntpq_output == '':
        	if subprocess.Popen(['ping', '-t','2', self.ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait() == 1:
        		self.net_status = False	# If pingtest fails, net_status will be False
        	else: 
        		self.hipat_status = False # If network is ok, and no ntpq_output is recieved, then HiPAT is down      	
        else: # If valid, Populate the object with the info from the ntpq_output
            self.net_status = True      # All is ok, set to True
            self.hipat_status = True    # All is ok, set to True
            
            ntpq_server.update(self, ntpq_output)   # The object is updated with info from ref_server
            if ntpq_server.update(self, ntpq_output, '158.112.116.2', True) > 0:    # If Cesium can be reached it returns > 0
                self.cesium_status = True   # The HiPAT server has valid data from the Cesium oscillator
        return         
