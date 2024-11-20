import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import requests
from dotenv import load_dotenv

""""
Calls the hpc api endpoints.  
"""
class CallerHPCApi():

    def __init__(self):

        load_dotenv()

        start_url = os.environ.get("integration_url")

        self.url = f"{start_url}/api/v1/dev"

    # if both guid and flag is added then the health api service will update the flag to the flag status defaulting to ERROR if none is given.
    def say_hi(self):
        
        url = f"{self.url}/yo"
        """
        content = {
                "guid": guid,
                "service_name": service,
                "flag": flag,
                "flag_status": flag_status,
                "message": message
                }
        """
        try:    
            #response = requests.post(url, json=content)
            response = requests.get(url)


            return response.json()
                
        except Exception as e:
            # TODO create log entry
            print(e)