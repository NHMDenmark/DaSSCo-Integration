import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import requests

class HealthCaller():

    def __init__(self):
        self.url = "http://localhost:8555"

    def warning(self, service, message, guid = None, flag = None):
        
        url = f"{self.url}/api/warning"
        
        content = {
                "guid": guid,
                "service": service,
                "flag": flag,
                "message": message
                }
        
        try:    
            response = requests.post(url, json=content)
            
            if response.status_code != 200:
                pass # TODO create log entry maybe direct call to slack web hook to warn that health api is not working

        except Exception as e:
            # TODO create log entry
            print(e)
    
    """
    This call will always create and send messages to email and slack. 
    Should be called when a service notices a change in its run status. 
    """
    def run_status_change(self, service, run_status, message):

        url = f"{self.url}/api/run_change_status"
        
        content = {
                "service_name": service,
                "run_status": run_status,
                "message": message
                }
        
        try:    
            response = requests.post(url, json=content)
            
            if response.status_code != 200:
                pass # TODO create log entry maybe direct call to slack web hook to warn that health api is not working

        except Exception as e:
            # TODO create log entry
            print(e)


        