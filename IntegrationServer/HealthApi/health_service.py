import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import email_sender
import slack_webhook

class HealthService():

    def __init__(self):
        self.mail = email_sender.EmailSender("test")
        self.slack = slack_webhook.SlackWebhook()

    """
    Splits the message received into: level, timestamp, python file, message, exception
    Returns a list with the above.
    """
    def split_message(self, message):
        parts = message.split("#")
        return parts
    
    def receive_warning(self, message, guid = "No guid"):
        parts = self.split_message(message)
        message = ""
        if len(parts) == 5:
            if parts[4] is not None:
                message = f"{parts[3]}: {parts[4]}"
            else:
                message = parts[3]
        else:
            message = parts[3]

        if guid != "No guid":
            self.mail.send_error_mail(guid, parts[2], parts[0], message)
            self.slack.message_from_integration(guid, parts[2], parts[0])
        else:
            self.mail.send_error_mail(service=parts[2], status=parts[0], error_msg=message)      
            self.slack.message_from_integration(service=parts[2], status=parts[0])