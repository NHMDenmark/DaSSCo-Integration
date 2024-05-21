import requests
import json
import os
from dotenv import load_dotenv

class SlackWebhook:

    def __init__(self):
        load_dotenv()
        self.url = os.getenv("slack_url")
    
    def message_from_integration(self, guid = "NO_GUID", service = "No_SERVICE", status = "NO_SERVICE"):
        
        # Define the payload
        payload = {
            "text": f"STATUS: {status} - SERVICE: {service} - GUID: {guid}"
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
            print(f"Slack webhook not working: {e}")
