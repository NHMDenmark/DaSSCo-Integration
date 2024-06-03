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
        if guid and flag is not None:
            content = {
                    "guid": guid,
                    "service": service,
                    "flag": flag,
                    "message": message
                        }
        else:
            content = {
                "service": service,
                "message": message
            }
        
        try:
            response = requests.post(url, json=content)
            print(response)
        except Exception as e:
            print(e)

        