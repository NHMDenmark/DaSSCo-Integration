import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import requests
from dotenv import load_dotenv

""""
Calls the ars/keycloak to get a status. 
"""
class ArsHealthCheck():

    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("client_id")
        self.client_secret = os.getenv("client_secret")
        self.auth_token_url = os.getenv("auth_token_keycloak_url")
        self.asset_service_health_url = os.getenv("ars_url")
        self.keycloak_health_url = os.getenv("cloak_url")
        self.fileproxy_health_url = os.getenv("fileproxy_url")

    def check_asset_service_health(self):
        
        try:    
            response = requests.get(url=self.asset_service_health_url)
            
            if response.status_code != 200:
                return False

            if response.status_code == 200:
                data = response.json()
                
                if data["status"] == "UP":
                        return True
            return False
        except Exception as e:
            # TODO create log entry
            print(e)
            return False

    def check_keycloak_health(self):
        
        try:    
            response = requests.get(url=self.keycloak_health_url)
            
            if response.status_code != 200:
                return False

            if response.status_code == 200:
                data = response.json()
                
                if data["status"] == "UP":

                    if data["checks"][0]["status"] == "UP":
                        return True
            return False
        except Exception as e:
            # TODO create log entry
            print(e)
            return False

    def check_fileproxy_health(self):
        
        try:    
            response = requests.get(url=self.fileproxy_health_url)
            
            if response.status_code != 200:
                return False

            if response.status_code == 200:
                data = response.json()
                
                if data["status"] == "UP":

                    if data["components"]["diskSpace"]["details"]["free"] > 10000000:
                        return True
            return False
        except Exception as e:
            # TODO create log entry
            print(e)
            return False
        

    def get_access_token(self):
        """
        Authenticates the client_id and client_secret. If the credentials are valid, an access token is obtained.
        Returns a valid access token or false.
        """
        """
        how to use token:
        token = self.get_access_token()

        if token is False:
            print("failed token")
            return False
        
        headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
        }
        """
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'openid'
        }

        res = requests.post(url=self.auth_token_url, data=data)

        if res.status_code == 200:
            token_data = res.json()
            return token_data.get("access_token")
        else:
            return False