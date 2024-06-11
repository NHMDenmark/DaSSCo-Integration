import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import requests
import json
import utility
from Enums import status_enum
from dotenv import load_dotenv

class SlackWebhook:

    def __init__(self):
        load_dotenv()
        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.util = utility.Utility()
        self.status_enum = status_enum.StatusEnum
        # the url to the slack webhook app that we are using. 
        self.url = os.getenv("slack_url")
    
    def message_from_integration(self, guid = "No guid", service_name = "No service name", service = "No service", status = "Status not found"):
        
        run_status = "None"
        if service_name != "No service name":
            run_status = self.get_run_status(service_name)

        # Define the content that will be displayed in the slack chat.
        if guid != "No guid": 
            payload = {
                "text": f"{status} - Service: {service_name} - Status: {run_status} - GUID: {guid}"
            }
        else:
            payload = {
                "text": f"{status} - Service: {service_name} - Status: {run_status}"
            }

        try:
            response = requests.post(
                self.url, 
                data=json.dumps(payload), 
                headers={"Content-Type": "application/json"}
            )            
            if response.status_code != 200:
                raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")
        
        except Exception as e:
            print(f"Slack webhook not working for asset: {guid} With error: {e}")
    
    def change_run_status_msg(self, severity, service_name, status):
        
        # Define the content that will be displayed in the slack chat. 
        payload = {
            "text": f"{severity} - Service: {service_name} - Status change to: {status}"
        }

        try:
            response = requests.post(
                self.url, 
                data=json.dumps(payload), 
                headers={"Content-Type": "application/json"}
            )            
            if response.status_code != 200:
                raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")
        
        except Exception as e:
            print(f"Slack webhook not working. With error: {e}")

    """
    Returns the overall run status for the service name provided.
    """
    def get_run_status(self, service_name):
        
        all_run = self.util.get_value(self.run_config_path, "all_run")
        service_run = self.util.get_value(self.run_config_path, service_name)

        if all_run == self.status_enum.STOPPED.value or service_run == self.status_enum.STOPPED.value:
            return self.status_enum.STOPPED.value
        
        if all_run == self.status_enum.PAUSED.value or service_run == self.status_enum.PAUSED.value:
            return self.status_enum.PAUSED.value

        return self.status_enum.RUNNING.value