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
import utility

class HealthService():

    def __init__(self):
        
        self.micro_service_config_path = f"{project_root}/ConfigFiles/micro_service_config.json"
        
        self.util = utility.Utility()
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

        # gets the id for the health database
        id = self.create_id(msg_parts)

        self.health.create_health_entry_from_api(id, model_data)
        
        if warning.guid and warning.flag is not None:
            updated = self.update_track_db(warning.guid, warning.flag)
            if updated is False:
                return False
        else:
            warning.guid = "No guid"

        # TODO check if this needs to happen. Create db for this to keep track of the errors warnings recevied within time frames and from various services. Should be moved to health checker
        self.inform_mail(id, msg_parts, warning.guid, warning.service_name)

        self.inform_slack(msg_parts, warning.guid, warning.service_name)

        return True
    
    def mail_check_requirements(self, service_name, log_id, severity_level,  ):
        pass

    def slack_check_requirements(self):
        pass
    
    def pause_run_status_check_requirements(self):
        pass

    """
    Receives a error message from the api with a message and potentially guid that something isnt going as well as it could. 
    Handles the message accordingly and sends out information to staff about the status if needed.
    Returns true when it could handle the message correctly, false otherwise.  
    """
    def receive_error(self, error):

        msg_parts = self.split_message(error.message)

        # create db entry in health db
        model_data = self.create_health_model(error, msg_parts)

        # gets the id for the health database
        id = self.create_id(msg_parts)

        self.health.create_health_entry_from_api(id, model_data)
        
        if error.guid and error.flag is not None:
            updated = self.update_track_db(error.guid, error.flag)
            if updated is False:
                return False
        else:
            error.guid = "No guid"
        
        # TODO check if this needs to happen. Create db for this to keep track of the errors warnings received within time frames and from various services. Should be moved to health checker
        self.inform_mail(id, msg_parts, error.guid, error.service_name)

        self.inform_slack(msg_parts, error.guid, error.service_name)

        return True
    
    """
    Receives a run status change message from the api with a message that a service has changed its run status. 
    Handles the message accordingly and sends out information to staff about the status change.
    Returns true.  
    """
    def run_status_change(self, info):

        parts = self.split_message(info.message)

        # gets the id for the health database
        id = self.create_id(parts)

        model_data = self.change_run_status_create_health_model(info, parts)

        self.health.create_health_entry_from_api(id, model_data)

        self.mail.send_status_change_mail(health_id=id, service_name=info.service_name, run_status=info.run_status, timestamp=parts[2])

        #self.mail.send_error_mail(id, service_name=info.service_name, service=parts[3], status=parts[1], error_msg=parts[4], timestamp=parts[2])
        self.slack.change_run_status_msg(parts[1], info.service_name, info.run_status)

        return True

    def create_health_model(self, warning, msg_parts):
        
        model = health_model.HealthModel()
        model.service = warning.service_name
        model.timestamp = msg_parts[2]
        model.severity_level = msg_parts[1]
        model.message = msg_parts[4]
    
        if warning.guid is not None:
            model.guid = warning.guid
        if warning.flag is not None:
            model.flag = warning.flag
        if len(msg_parts) == 6:
            model.exception = msg_parts[5]
        
        model_data = model.model_dump_json()
        model_data = json.loads(model_data)

        return model_data
    
    def change_run_status_create_health_model(self, warning, msg_parts):
        
        model = health_model.HealthModel()
        model.service = warning.service_name
        model.timestamp = msg_parts[2]
        model.severity_level = msg_parts[1]
        model.message = msg_parts[4]

        model_data = model.model_dump_json()
        model_data = json.loads(model_data)

        return model_data

    def update_track_db(self, guid, flag):
        return self.track.update_entry(guid, flag, self.validate_enum.ERROR.value)

    def inform_mail(self, health_id, parts, asset_guid, service_name):
        if len(parts) == 6:
            if asset_guid != "No guid":
                self.mail.send_error_mail(health_id, asset_guid, service_name, parts[3], parts[1], parts[4], parts[2], parts[5])
            else:
                self.mail.send_error_mail(health_id, service_name=service_name, service=parts[3], status=parts[1], error_msg=parts[4], timestamp=parts[2], exception=parts[5])      
                
        if len(parts) == 5:
            if asset_guid != "No guid":
                self.mail.send_error_mail(health_id, asset_guid, service_name, parts[3], parts[1], parts[4], parts[2])
            else:
                self.mail.send_error_mail(health_id, service_name=service_name, service=parts[3], status=parts[1], error_msg=parts[4], timestamp=parts[2])      
                
    def inform_slack(self, parts, asset_guid, service_name):
        if asset_guid != "No guid":
            self.slack.message_from_integration(asset_guid, service_name, parts[3], parts[1])
        else:
            self.slack.message_from_integration(service_name=service_name, service=parts[3], status=parts[1])

    """
    Splits the message received into: prefix_id, level, timestamp, python file, message, exception
    Returns a list with the above.
    """
    def split_message(self, message):
        # parts will consist of: prefix_id[0], severity level[1], timestamp[2], service[3], message[4], exception[5]
        parts = message.split("###")

        return parts
    
    """
    Creates the id for the health database.
    Takes a split message as input cleans the timestamp for special characters and spaces.
    Returns the id created from the prefix_id and the cleaned timestamp.
    """
    def create_id(self, msg_parts):
        prefix_id = msg_parts[0]
        clean_timestamp = self.util.clean_string(msg_parts[2])
        id = f"{prefix_id}_{clean_timestamp}"
        return id
