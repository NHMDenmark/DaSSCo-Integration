import subprocess
import sys
import os
from dotenv import load_dotenv

"""
This requires sendmail to be installed on a linux system.
See the email_sender.py for a way to use it without those restrictions (needs a mailserver setup instead).
Sends emails to the address set in the .env file. 
"""
class MailSender:

    def __init__(self):
        load_dotenv()
        

    def send_mail(self, subject = "No subject", message = "No Message"):
    
        mail_receiver = os.getenv("mail_receiver")

        subject = f"Subject: {subject}\n\n{message}"

        command = ['sendmail', mail_receiver]

        # Using subprocess.Popen for more control, including sending input via stdin                
        process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True)
        process.communicate(input=subject)

if __name__=="__main__":
    
    """ 
    Allow mailsender to be called manually with subject line and message written in console,
    note the receiver of the mail must be set in the .env file
    """
    if len(sys.argv) == 3:
        m = MailSender()
        header = sys.argv[1]
        content = sys.argv[2]
        m.send_mail(header, content)