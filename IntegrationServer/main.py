import logging.handlers
import os
import utility
import sys
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
from MongoDB import mongo_connection, track_repository, health_repository, service_model
import IntegrationServer.Ndrive.ndrive_new_files as ndrive_new_files
import IntegrationServer.Ndrive.process_files_from_ndrive as process_files_from_ndrive
from StorageApi import storage_client
from HpcSsh import hpc_job_caller, hpc_asset_creator
import json
import time
from bson.json_util import dumps
from datetime import datetime
from dotenv import load_dotenv
import InformationModule.email_sender as email_sender
import InformationModule.slack_webhook as slack_webhook
import subprocess
import logging
from HealthUtility import health_caller
from Enums.feedback_enum import Feedback
from HealthApi import health_service
from HealthUtility.run_utility import LogClass
from pymongo.errors import InvalidOperation
""""
Test area for the different processes. May contain deprecated information.
"""

class IntegrationServer(object):
    def __init__(self):
        self.util = utility.Utility()

        self.new_files_path = "IntegrationServer/Files/NewFiles/"
        self.updated_files_path = "IntegrationServer/Files/UpdatedFiles/"
        self.ssh_config_path = "IntegrationServer/ConfigFiles/ssh_connections_config.json"

        self.cons.create_ssh_connections(self.ssh_config_path)
        load_dotenv()

def test():
    util = utility.Utility()
    # jobby = job_driver.JobDriver()
    # cons = connections.Connections()
    # api = northtech_rest_api.APIUsage()
    # smb = smb_connecter.SmbConnecter()
    # mongo = mongo_connection.MongoConnection("track")
    # meta_mongo = mongo_connection.MongoConnection("metadata")
    # ndrive = ndrive_new_files.NdriveNewFilesFinder()
    # new_files = process_files_from_ndrive.ProcessNewFiles()
    # ars = storage_client.StorageClient()
    # job_caller = hpc_job_caller.HPCJobCaller()
    # hpc_creator = hpc_asset_creator.HPCAssetCreator()
    # cons.create_ssh_connections("./ConfigFiles/ssh_connections_config.json")

    relPath = "Tests/TestConfigFiles/test_track_entry.json"
    #name = os.path.basename(relPath)
    #print(name)
    
    #mb = util.calculate_file_size_round_to_next_mb("C:/Users/tvs157/Desktop/CP0002637_L_selago_Fuji_ICC.tif")
    #print(mb)
    #entry = mongo.get_entry("_id", "sixth0006")
    #entry_dict = json.loads(dumps(entry))

    #email = email_sender.EmailSender("test")
    #email.send_error_mail("abc", "upload_file", "CRITICAL", "Everything is breaking down, call the police.")
    #sl = slack_webhook.SlackWebhook()
    #sl.message_from_integration("Lars", "MIGHTY WARRIOR", "GET WELL")
    #util.write_full_json(relPath, entry)
    #track = track_repository.TrackRepository()
    #track.update_entry("7e8-4-09-0a-00-34-0-001-00-000-0b8ab2-00000", "has_new_file", "POSSIBLE")
    #print(track.get_entry("_id", "7e8-4-09-0a-00-34-0-001-00-000-0b8ab2-00000"))
    
    #c = health_caller.HealthCaller()
    #c.warning(service="main", message="ERROR#2024-05-30 14:26:25,053#xd.py#yolo#trouble shoot message")
    #h = health_repository.HealthRepository()
    #p = h.get_recent_errors("some service", 2000000)
    #print(p[0:7])
    #h.close_connection()
    

class x(Feedback, LogClass):
    def __init__(self):
        Feedback.__init__(self)
        LogClass.__init__(self, "yo", "ho")
        print(self.AWAIT)

def im_loopy():
        x = 3
        try:
            while x > 0:
                print("yo")
                x -= 1
                y = 3/x
                print(y)
        except Exception as e:
            print(x, y, e)
            time.sleep(5)
            im_loopy()

if __name__ == '__main__':
    #logging.basicConfig(filename="myapp.log", format='%(levelname)s:%(asctime)s:%(name)s:%(message)s:%(exc_info)s', encoding="utf-8", level=logging.INFO)
    
    a = 90%100
    print(a)
    # i = IntegrationServer()
    #test()
    #x()
