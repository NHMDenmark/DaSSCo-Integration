import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import datetime
import smtplib
import utility
import subprocess
from dotenv import load_dotenv

class EmailSender:
    """
    Note only one version of send_error_mail should be available at a time. Which one depends on which OS we are on. 
    """
    def __init__(self, mail):
        load_dotenv()
        self.util = utility.Utility()
        self.mail_config_path = f"{project_root}/ConfigFiles/mail_config.json"
        self.mail_configs = self.util.get_value(self.mail_config_path, mail)
        self.server_host = self.mail_configs.get("server_host") 
        self.server_port = self.mail_configs.get("server_port")  
        self.address_from = self.mail_configs.get("sender_address")
        self.address_to = self.mail_configs.get("receiver_address")
        
        # avoids putting emails used for testing into github, just leave config fields blank and configure fields in dotenv file
        if self.address_from == "":
            self.address_from = os.getenv("temp_address_from")
        if self.address_to == "":
            self.address_to = os.getenv("temp_address_to")

        self.mail_server_user = os.getenv(f"mail_server_user_{mail}")
        self.mail_server_pass = os.getenv(f"mail_server_pass_{mail}")

    """
    This requires sendmail to be installed on the system. Also requires the system to be linux.
    """
    # TODO needs to be tested
    """
    def send_error_mail(self, guid = "NO_GUID", service_name = "NO_NAME", service = "NO_SERVICE", status = "NO_STATUS", error_msg = "NO_MESSAGE"):
        
        subj, message =self.create_error_mail_content(guid, service, status, error_msg)

        subject = f"{subj}\n\n{message}"
        
        command = ['sendmail', self.address_to]

        # Using subprocess.Popen for more control, including sending input via stdin
        process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True)
        process.communicate(input=subject)
    """
    """
    This requires a mailserver to be setup and configured.
    """
    def send_error_mail(self, guid = "NO_GUID", service_name = "NO_NAME", service = "NO_SERVICE", status = "NO_STATUS", error_msg = "NO_MESSAGE", timestamp = None, exception = "None"):

        mail_subject, msg_content = self.create_error_mail_content(guid, service_name, service, status, error_msg, timestamp, exception)

        msg_from = "From: " + self.address_from + "\r\n"
        msg_to = "To: " + self.address_to + "\r\n"
        msg_subject = "Subject: " + mail_subject + "\r\n"
        msg_timestamp = '{:%a, %d %b %Y %H %M:%S %z}'.format(datetime.datetime.now())
        msg_date = "Date: " + msg_timestamp + "\r\n"
        msg = msg_from + msg_to + msg_subject + msg_date + "\r\n" + msg_content
        # connect to smarthost, login, send mail and disconnect
        server = smtplib.SMTP(self.server_host, self.server_port)
        server.ehlo()
        server.starttls()
        server.login(self.mail_server_user, self.mail_server_pass)
        server.sendmail(self.address_from, self.address_to, msg)
        server.quit()
    
        
    # Creates the email content that is being send.     
    def create_error_mail_content(self, guid = "No guid", service_name = "No name", service = None, status = None, error_msg = None, timestamp = None, exception = "None"):

        add_time = ""
        mail_subject = f"{status} - {service_name} - {guid}"
        if timestamp is None:
            timestamp = '{:%d %b %Y %H:%M:%S %z}'.format(datetime.datetime.now())
            add_time = "- The timestamp was added by the mail sender."

        mail_msg = f"""
This is an autogenerated message from the integration server.

SERVICE: {service_name}
GUID: {guid}
FILE_LOCATION: {service}
STATUS: {status}
TIMESTAMP: {timestamp} {add_time}   
MESSAGE: {error_msg}
EXCEPTION: {exception} 
                    """

        return mail_subject, mail_msg
