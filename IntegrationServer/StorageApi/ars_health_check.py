import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import requests
from dotenv import load_dotenv

""""
Calls the health endpoints to check nothing is wrong with ARS. 
"""
class HealthCaller():

    def __init__(self):

        load_dotenv()
        
        self.fileproxy_url = os.getenv("fileproxy_url")
        self.ars_url = os.getenv("ars_url")
        self.cloak_url = os.getenv("cloak_url")

    
    def get_fileproxy_health(self):
        try:    
            response = requests.post(self.fileproxy_url)
            
            if response.status_code != 200:
                pass 

        except Exception as e:
            # TODO create log entry
            print(e)

    def get_ars_health(self):
        pass

    def get_cloak_health(self):
        pass