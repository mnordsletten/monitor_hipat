import subprocess, threading

"""Will perform an update of the remote sites using threading. 
    1. Update the remote_server objects with updated information."""
    
class myThread(threading.Thread):
    def __init__(self, server_object):
        """The server object is made part of the Thread object.
        """
        threading.Thread.__init__(self)
        self.server_object = server_object
        return
        
    def run(self):
        """The server_objects update function is called."""  
        self.server_object.update()
        return        
    