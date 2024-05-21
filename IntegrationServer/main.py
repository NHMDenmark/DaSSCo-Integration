# from IntegrationServer.Connections import smb_connecter
# from IntegrationServer.Connections import connections
import os
import utility
# from IntegrationServer.JobList import job_driver
# from IntegrationServer.Connections import northtech_rest_api
from MongoDB import mongo_connection
import IntegrationServer.Ndrive.ndrive_new_files as ndrive_new_files
import IntegrationServer.Ndrive.process_files_from_ndrive as process_files_from_ndrive
from StorageApi import storage_client
from HpcSsh import hpc_job_caller, hpc_asset_creator
import json
from bson.json_util import dumps
from datetime import datetime
from dotenv import load_dotenv
import email_sender
import slack_webhook

""""
Test area for the different processes. May contain deprecated information.
"""


class IntegrationServer(object):
    def __init__(self):
        self.util = utility.Utility()
        # self.jobby = job_driver.JobDriver()
        # self.cons = connections.Connections()

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
    #  cons.create_ssh_connections("./ConfigFiles/ssh_connections_config.json")
    #storage = storage_client.StorageClient()

    #storage.test()
    #print(storage.create_asset("third0003"))
    #storage.update_metadata("second0002", "Shorty")
    #print(storage.sync_erda("second0002"))
    #print(storage.get_asset_status("second0002"))
    #print(storage.open_share("second0002", "test-institution", "test-collection", 610))
    

    relPath = "Tests/TestConfigFiles/test_track_entry.json"
    #name = os.path.basename(relPath)
    #print(name)
    """
    x = mongo.find_running_jobs_older_than()
    for entry in x:
        util.write_full_json(relPath, entry)
    
    crc = util.calculate_crc_checksum("C:/Users/tvs157/Desktop/VSC_projects/DaSSCo-Integration/postman.txt")
    """
    #mb = util.calculate_file_size_round_to_next_mb("C:/Users/tvs157/Desktop/CP0002637_L_selago_Fuji_ICC.tif")
    #print(mb)
    #entry = mongo.get_entry("_id", "sixth0006")
    #entry_dict = json.loads(dumps(entry))
    email = email_sender.EmailSender("test")
    email.send_error_mail("abc", "upload_file", "CRITICAL", "Everything is breaking down, call the police.")
    #sl = slack_webhook.SlackWebhook()
    #sl.message_from_integration("zxy", "CHIPS EATING MACHINE", "BREAK A LEG")
    #util.write_full_json(relPath, entry)

    #mongo.create_metadata_entry(relPath, "test_0001")
    #print(os.getenv("password"))

if __name__ == '__main__':
    # git rm -r --cached .idea/
    # i = IntegrationServer()
    test()
    