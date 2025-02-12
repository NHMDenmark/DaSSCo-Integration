import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import datetime
import random
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
        # choose the name of the sender OCTOPUS, STARFISH
        self.sender_name = "STARFISH"
        
        # avoids putting emails used for testing into github, just leave config fields blank and configure fields in dotenv file
        if self.address_from == "":
            self.address_from = os.getenv("temp_address_from")
        if self.address_to == "":
            self.address_to = os.getenv("temp_address_to")

        self.mail_server_user = os.getenv(f"mail_server_user_{mail}")
        self.mail_server_pass = os.getenv(f"mail_server_pass_{mail}")

    """
    This requires sendmail to be installed on the system. Also requires the system to be linux.
    Returns true.
    """
        
    def send_error_mail(self, health_id, guid = "No guid", service_name = "No name", service = "No service", status = "No status", error_msg = "No message", timestamp = None, exception = "None"):
        
        subj, message = self.create_error_mail_content(health_id, guid, service_name, service, status, error_msg, timestamp, exception)
        
        message = f"{subj}\n\n{message}"
        
        email_headers = f"From: {self.sender_name}\nTo: {self.address_to}\nSubject: {subj}\n\n"
        
        # The complete email content with headers and message
        email_content = f"{email_headers}{message}"
        
        command = ['sendmail', self.address_to]

        # Using subprocess.Popen for more control, including sending input via stdin
        process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True)
        process.communicate(input=email_content)
        
        return True
    
    """
    This requires sendmail to be installed on the system. Also requires the system to be linux.
    Returns true.
    """
    
    def send_status_change_mail(self, health_id, service_name, run_status, timestamp):
        
        subj, message = self.create_status_change_mail_content(health_id, service_name, run_status, timestamp)

        message = f"{subj}\n\n{message}"
        
        email_headers = f"From: {self.sender_name}\nTo: {self.address_to}\nSubject: {subj}\n\n"
        
        # The complete email content with headers and message
        email_content = f"{email_headers}{message}"
        
        command = ['sendmail', self.address_to]

        # Using subprocess.Popen for more control, including sending input via stdin
        process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True)
        process.communicate(input=email_content)

        return True
    

    """
    
    #This requires a mailserver to be setup and configured.
    #Returns true.
    
    def send_error_mail(self, health_id, guid = "No guid", service_name = "No name", service = "No service", status = "No status", error_msg = "No message", timestamp = None, exception = "None"):

        mail_subject, msg_content = self.create_error_mail_content(health_id, guid, service_name, service, status, error_msg, timestamp, exception)

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

        return True

    
    #This requires a mailserver to be setup and configured.
    #Returns true.
    
    def send_status_change_mail(self, health_id, service_name, run_status, timestamp):

        mail_subject, msg_content = self.create_status_change_mail_content(health_id, service_name, run_status, timestamp)

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
        
        return True
    """
    # Creates the email content that is being send.     
    def create_error_mail_content(self, health_id, guid = "No guid", service_name = "No name", service = None, status = None, error_msg = None, timestamp = None, exception = "None"):
        
        if service_name == "Test health api":
            mail_subject, mail_msg = self.create_test_content("Error/warning message content")
            return mail_subject, mail_msg

        add_time = ""
        mail_subject = f"{status} - {service_name} - {guid}"
        if timestamp is None:
            timestamp = '{:%d %b %Y %H:%M:%S %z}'.format(datetime.datetime.now())
            add_time = "- The timestamp was added by the mail sender."

        bonus_msg = self.create_mail_happiness()

        mail_msg = f"""
This is an autogenerated message from the integration server.

SERVICE: {service_name}
HEALTH DB ID: {health_id}
ASSET GUID: {guid}
FILE_LOCATION: {service}
STATUS: {status}
TIMESTAMP: {timestamp} {add_time}   
MESSAGE: {error_msg}
EXCEPTION: {exception} 

{bonus_msg}
                    """

        return mail_subject, mail_msg

    def create_status_change_mail_content(self, health_id, service_name, run_status, timestamp):

        if service_name == "Test health api":
            mail_subject, mail_msg = self.create_test_content("Status change mail content")
            return mail_subject, mail_msg

        mail_subject = f"{service_name} status changed to {run_status}"

        bonus_msg = self.create_mail_happiness()

        mail_msg = f"""
This is an autogenerated message from the integration server. 
{service_name} has changed status.

SERVICE: {service_name}
HEALTH DB ID: {health_id}
RUN STATUS: {run_status}
TIMESTAMP: {timestamp}

{bonus_msg}
                    """
        return mail_subject, mail_msg
    
    def create_test_content(self, subject):

        mail_subject = "UNIT TEST"

        bonus_msg = self.create_mail_happiness()

        mail_msg = f"""
{subject} - everything is fine.

{bonus_msg}
                    """
        return mail_subject, mail_msg
    
    def create_mail_happiness(self):

        noun = ["A penguin", "A lion", "A tiger", "A biologist", "A clown", "The primeminister", "A goldfish", "A martian", "The sun", "A boat", "A ghost", "A dragon", "A god", "A student", "A professor", "A rabbit", "A bumble-bee"]

        verb = ["dances with", "swings", "adjusts", "holds onto", "laughs at", "kisses", "praises", "roars towards", "handles", "makes", "loves", "creates", "carries", "bends", "dashes after", "apologises to"]

        adjective = ["a blue", "a spotted", "an orange", "a smelly", "a dangerous", "a lovely", "a striped", "a hungry", "a pretentious", "a green", "a serious", "a golden", "a basking"]

        object = ["computer", "pencil", "car", "cow", "beer can", "apple tree", "model", "painting", "song", "cat", "guitar", "mask", "teapot", "tentacle", "soap bubble", "radiator", "cake"]

        time_desc = ["at noon", "during a hot summer", "once a blue moon", "in the afternoon", "when the first snow falls" "everytime", "early mornings", "late evenings", "has never happened", "could be", "is not happening", "in a good mood", "happily"]

        n = noun[random.randint(0,len(noun)-1)]
        v = verb[random.randint(0,len(verb)-1)]
        a = adjective[random.randint(0,len(adjective)-1)]
        o = object[random.randint(0,len(object)-1)]
        t = time_desc[random.randint(0,len(time_desc)-1)]

        poetry = f"{n} {v} {a} {o} {t}."

        return poetry