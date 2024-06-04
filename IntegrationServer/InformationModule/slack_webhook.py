import requests
import json
import os
from dotenv import load_dotenv

class SlackWebhook:

    def __init__(self):
        load_dotenv()
        # the url to the slack webhook app that we are using. 
        self.url = os.getenv("slack_url")
    
    def message_from_integration(self, guid = "No guid", service_name = "No service name", service = "No service", status = "Status not found"):
        
        # Define the content that will be displayed in the slack chat. 
        payload = {
            "text": f"{status} - SERVICE: {service_name} - GUID: {guid}"
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
