import datetime
import re
from config import config

class ntpq_server():
    """This file contains the class ntpq_server. This is a class that contains information about the remote site. 
    The ntpq servers can be found and populated in one of two ways:
    1. Local population: The local "ntpq -p" output is read, offset info is gathered from this output.
    2. Remote population: "ntpq -p <ip address>" is used to gather information from the remote sites. This gives a true representation of the offset to the reference server.

    Remote population is the prefered method, as the output provided by monitor_hipat will be the same regardless of where the program is run.
    Subclasses of ntpq_server will be created to fit both local and remote popuplation.
    """
    
    def __init__(self, ip_address="0.0.0.0"):
        """Initializing the generic ntpq_server"""
        self.name = ""
        self.ip_address = ip_address
        self.offset = 0.0
        self.when = 0.0
        self.jitter = 0.0
        self.status = "Init"
        self.hipat_status = 0
        self.net_status = 0
        self.remote = True  # False if it is a local ntp measurement
        self.last_fail = datetime.datetime.min
        
    def __str__(self):
        return ("Name: {0} \n"
                "Ip Address: {1} \n"
                "Offset: {2} \n"
                "When: {3} \n"
                "Jitter: {4} \n"
                "Status: {5} \n"
                "Remote: {6} \n"
                "Last Fail: {7}").format(self.name, 
                                         self.ip_address,
                                         self.offset,
                                         self.when,
                                         self.jitter,
                                         self.status,
                                         self.remote,
                                         self.last_fail)
                                         
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
    
    def update(self, ntpq_output, ip_address = config["ref_ip_address"], cesium_reach = False):
        """update() will extract the important information (offset, when and jitter) from the ntpq_output.
        If there are multiple lines in the output the server specified by ip_address is chosen. The default server 
        is the ip address of the reference, this is read from the config.
        
        ntpq_output = The input to be analyzed, can be multiple lines. Ip addresses must be specified "ntpq -pn"
        ip_address = If there are multiple lines in the input the ip address of the server requested must be specified.
        
        Update places the result in the objects fields.
        """
        regex = (   '(?P<ip_address>{0})\s+'# ip_address to get info from
                    '(?P<refid>\S+)\s+'     # refid 
                    '(?P<st>\S+)\s+'        # stratum
                    '(?P<t>\S+)\s+'         # type of server
                    '(?P<when>\S+)\s+'      # when, time since last update
                    '(?P<poll>\S+)\s+'      # poll, how often it is polled
                    '(?P<reach>\S+)\s+'     # how reliable the server is
                    '(?P<delay>\S+)\s+'     # time in ms to the server
                    '(?P<offset>\S+)\s+'    # offset to server in ms
                    '(?P<jitter>\S+)\s+'    # jitter of the server
        ).format(ip_address)
        regex_results = re.search(regex, ntpq_output, re.MULTILINE)    # search for the line from the ntpq output
        
        # Now offset, when and jitter are all processed and submitted to the object
        # Offset and jitter are processed, make sure when is also in the regex_results
        try:          
            self.offset = float(regex_results.group('offset'))  # The offset value is converted to float and saved
            self.jitter = float(regex_results.group('jitter'))  # The jitter value is converted to float and saved
            when_output = regex_results.group('when')           # when_output is easier to work with
            if cesium_reach:
            	return int(regex_results.group('reach')) 		# Special occurance where reach is needed
        except IndexError:                                      # If an argument is not found in the regex results.
            print "Offset not found in ntpq_output"
        
        # When is processed, the answer is converted to seconds.
        if when_output == '-':                          # If no updates received a '-' is displayed
            self.when = 0.0
        elif when_output[-1] == 'm':                    # 'm' = minutes
            self.when = float(when_output[:-1]) * 60
        elif when_output[-1] == 'h':                    # 'h' = hours
            self.when = float(when_output[:-1]) * 3600
        elif when_output[-1] == 'd':                    # 'd' = days
            self.when = float(when_output[:-1]) * 86400
        else:
        	self.when = float(when_output) 				# already in seconds
        
        # Lastly we set the status of the object
        self.find_status()
        return

