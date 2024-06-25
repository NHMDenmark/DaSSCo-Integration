import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import json
import InformationModule.email_sender as email_sender
import InformationModule.slack_webhook as slack_webhook
from MongoDB import track_repository, health_repository, health_model
from Enums import status_enum, validate_enum

class HealthService():

    def __init__(self):
        self.mail = email_sender.EmailSender("test")
        self.slack = slack_webhook.SlackWebhook()
        self.track = track_repository.TrackRepository()
        self.health = health_repository.HealthRepository()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum

    """
    Receives a warning message from the api with a message and potentially guid that something isnt going as well as it could. 
    Handles the message accordingly and sends out information to staff about the status if needed.
    Returns true when it could handle the message correctly, false otherwise.  
    """
    def receive_warning(self, warning):

        msg_parts = self.split_message(warning.message)

        # create db entry in health db
        model_data = self.create_health_model(warning, msg_parts)
        self.health.create_health_entry_from_api(model_data)
        
        if warning.guid and warning.flag is not None:
            updated = self.update_track_db(warning.guid, warning.flag)
            if updated is False:
                return False
        else:
            warning.guid = "No guid"

        # TODO check if this needs to happen. Create db for this to keep track of the errors warnings recevied within time frames and from various services. Should be moved to health checker
        self.inform_slack_mail(msg_parts, warning.guid, warning.service)

        return True
    
    """
    Receives a error message from the api with a message and potentially guid that something isnt going as well as it could. 
    Handles the message accordingly and sends out information to staff about the status if needed.
    Returns true when it could handle the message correctly, false otherwise.  
    """
    def receive_error(self, error):

        msg_parts = self.split_message(error.message)

        # create db entry in health db
        model_data = self.create_health_model(error, msg_parts)
        self.health.create_health_entry_from_api(model_data)
        
        if error.guid and error.flag is not None:
            updated = self.update_track_db(error.guid, error.flag)
            if updated is False:
                return False
        else:
            error.guid = "No guid"
        
        # TODO check if this needs to happen. Create db for this to keep track of the errors warnings recevied within time frames and from various services. Should be moved to health checker
        self.inform_slack_mail(msg_parts, error.guid, error.service)

        return True
    
    def create_health_model(self, warning, msg_parts):
        
        model = health_model.HealthModel()
        model.service = warning.service
        model.timestamp = msg_parts[1]
        model.severity_level = msg_parts[0]
        model.message = msg_parts[3]
        if warning.guid is not None:
            model.guid = warning.guid
        if warning.flag is not None:
            model.flag = warning.flag
        if len(msg_parts) == 5:
            model.exception = msg_parts[4]
        
        model_data = model.model_dump_json()
        model_data = json.loads(model_data)

        return model_data

    def update_track_db(self, guid, flag):
        self.track.update_entry(guid, flag, self.validate_enum.ERROR.value)

    def inform_slack_mail(self, parts, guid, service_name):
        if len(parts) == 5:
            if guid != "No guid":
                self.mail.send_error_mail(guid, service_name, parts[2], parts[0], parts[3], parts[1], parts[4])
                self.slack.message_from_integration(guid, service_name, parts[2], parts[0])
            else:
                self.mail.send_error_mail(service_name=service_name, service=parts[2], status=parts[0], error_msg=parts[3], timestamp=parts[1], exception=parts[4])      
                self.slack.message_from_integration(service_name=service_name, service=parts[2], status=parts[0])
        
        if len(parts) == 4:
            if guid != "No guid":
                self.mail.send_error_mail(guid, service_name, parts[2], parts[0], parts[3], parts[1])
                self.slack.message_from_integration(guid, service_name, parts[2], parts[0])
            else:
                self.mail.send_error_mail(service_name=service_name, service=parts[2], status=parts[0], error_msg=parts[3], timestamp=parts[1])      
                self.slack.message_from_integration(service_name=service_name, service=parts[2], status=parts[0])
    
    def run_status_change(self, info):

        parts = self.split_message(info.message)

        self.mail.send_error_mail(service_name=info.service_name, service=parts[2], status=parts[0], error_msg=parts[3], timestamp=parts[1])
        self.slack.change_run_status_msg(parts[0], info.service_name, info.run_status)


    """
    Splits the message received into: level, timestamp, python file, message, exception
    Returns a list with the above.
    """
    def split_message(self, message):
        # parts will consist of: severity level[0], timestamp[1], service[2], message[3], exception[4]
        parts = message.split("###")
        return parts