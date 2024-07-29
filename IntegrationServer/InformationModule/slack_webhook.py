import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import requests
import json
import utility
from MongoDB import service_repository
from Enums import status_enum
from Enums import log_enum
from dotenv import load_dotenv

class SlackWebhook:

    def __init__(self):
        load_dotenv()

        self.service_mongo = service_repository.ServiceRepository()
        self.util = utility.Utility()
        self.status_enum = status_enum.StatusEnum
        self.log_enum = log_enum.LogEnum
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

        if status == self.log_enum.TESTING.value:
            payload = {
                    "text": f"{status} - receive message warning/error"
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
            print(f"Slack webhook not working for service: {service_name} asset: {guid} With error: {e}")
    
    def change_run_status_msg(self, severity, service_name, status):
        
        # Define the content that will be displayed in the slack chat. 
        payload = {
            "text": f"{severity} - Service: {service_name} - Status change to: {status}"
        }
        if status == self.log_enum.TESTING.value:
            payload = {
                "text": f"{severity} - change run status test"
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
            print(f"Slack webhook not working for service: {service_name}. With error: {e}")

    def attempted_unpause_msg(self, service_name):
        # Define the content that will be displayed in the slack chat. 
        payload = {
            "text": f"{service_name} - Attempting to unpause self."
        }

        if service_name == "Test health api":
            payload = {
                "text": f"TESTING - unpause message"
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
            print(f"Slack webhook not working for service: {service_name}. With error: {e}")

    def unexpected_error_msg(self, health_id, service_name):
        # Define the content that will be displayed in the slack chat. 
        payload = {
            "text": f"UNEXPECTED ERROR - {service_name} - Health ID: {health_id}"
        }

        if service_name == "Test health api":
            payload = {
                "text": f"TESTING - unexpected error message"
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
            print(f"Slack webhook not working for service: {service_name}. With error: {e}")

    """
    Returns the overall run status for the service name provided.
    """
    def get_run_status(self, service_name):
        
        all_run = self.service_mongo.get_value_for_key("all_run", "run_status")
        service_run = self.service_mongo.get_value_for_key(service_name, "run_status")

        if all_run == self.status_enum.STOPPED.value or service_run == self.status_enum.STOPPED.value:
            return self.status_enum.STOPPED.value
        
        if all_run == self.status_enum.PAUSED.value or service_run == self.status_enum.PAUSED.value:
            return self.status_enum.PAUSED.value

        return self.status_enum.RUNNING.value
    
    