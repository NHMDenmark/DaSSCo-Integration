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

        self.start_url = os.environ.get("integration_url")

        self.local_url = "http://localhost:8000"

        self.url = f"{self.local_url}/dev/api/v1"

    # if both guid and flag is added then the health api service will update the flag to the flag status defaulting to ERROR if none is given.
    def say_hi(self):
        new_url = f"{self.start_url}/dev/yo"
        
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
            response = requests.get("http://localhost:8000/dev/yo", timeout=5)

            return response
                
        except Exception as e:
            # TODO create log entry
            print(e)

    def derivative_file_uploaded(self, guid):
        
        try:
            param = {"asset_guid":{guid}}

            url = f"{self.url}/derivative_uploaded"

            print(url)

            response = requests.post(url, params=param)

            if response.status_code != 200:
                print(f"Call got status: {response.status_code}")
                return False
            
            return True
        
        except Exception as e:
            print(e)
            return False
        
    def asset_clean_up(self, guid):
        
        try:
            param = {"asset_guid":{guid}}

            url = f"{self.url}/asset_clean_up"

            print(url, guid)

            response = requests.post(url, params=param)

            if response.status_code != 200:
                print(f"Call got status: {response.status_code}")
                return False
            
            return True
        
        except Exception as e:
            print(e)
            return False