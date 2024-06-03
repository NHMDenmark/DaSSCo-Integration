import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import email_sender
import slack_webhook
from MongoDB import track_repository
from Enums import status_enum, validate_enum

class HealthService():

    def __init__(self):
        self.mail = email_sender.EmailSender("test")
        self.slack = slack_webhook.SlackWebhook()
        self.track = track_repository.TrackRepository()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum

    """
    Receives a message from the api with a message and potentially guid that something isnt going as well as it could. 
    Handles the message accordingly and sends out information to staff about the status if needed.
    Returns true when it could handle the message correctly, false otherwise.  
    """
    def receive_warning(self, warning):


        msg_parts = self.split_message(warning.message)

        # TODO create db entry in warning db
        self.create_db_entry(warning)
        
        if warning.guid and warning.flag is not None:
            updated = self.update_track_db(warning.guid, warning.flag)
            if updated is False:
                return False
        else:
            warning.guid = "No guid"

        # TODO check if this needs to happen. Create db for this to keep track of the errors warnings recevied within time frames and from various services. 
        self.inform_slack_mail(msg_parts, warning.guid)

        return True
    
    def create_db_entry(self, warning):
        pass


    def update_track_db(self, guid, flag):
        self.track.update_entry(guid, flag, self.validate_enum.ERROR.value)

    def inform_slack_mail(self, parts, guid):
        if len(parts) == 5:
            if guid != "No guid":
                self.mail.send_error_mail(guid, parts[2], parts[0], parts[3], parts[1], parts[4])
                self.slack.message_from_integration(guid, parts[2], parts[0])
            else:
                self.mail.send_error_mail(service=parts[2], status=parts[0], error_msg=parts[3], timestamp=parts[1], exception=parts[4])      
                self.slack.message_from_integration(service=parts[2], status=parts[0])
        
        if len(parts) == 4:
            if guid != "No guid":
                self.mail.send_error_mail(guid, parts[2], parts[0], parts[3], parts[1])
                self.slack.message_from_integration(guid, parts[2], parts[0])
            else:
                self.mail.send_error_mail(service=parts[2], status=parts[0], error_msg=parts[3], timestamp=parts[1])      
                self.slack.message_from_integration(service=parts[2], status=parts[0])

    """
    Splits the message received into: level, timestamp, python file, message, exception
    Returns a list with the above.
    """
    def split_message(self, message):
        # parts will consist of: severity level[0], timestamp[1], service[2], message[3], exception[4]
        parts = message.split("#")
        return parts