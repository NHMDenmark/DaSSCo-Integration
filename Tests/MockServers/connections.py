"""
This is a mocked interpretation of the slurm server on ucloud and all the ssh connection classes. It is named the same as the "connections" in the Connections module to make it easy to switch to the mock setup and back.
Change the import "from Connection import connections" in all the HpcSsh services to "from Tests.MockServers import connections".
Naming it the same means no other changes needs to happen to run tests with the mock setup.
"""
import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import datetime
import time

from IntegrationServer import utility
from IntegrationServer.HealthUtility import caller_hpc_api

class Connections():
    """
    Imitates some behavior of Connections class in Connections connections.py script.
    """

    def __init__(self):
        self.connection = None
        self.msg = None
        self.exc = None

    def create_ssh_connections(self, string):
        # empty call that would normally setup the connection as prep for get_connection
        pass

    def get_connection(self):
        # returns the CallsHandler class as the "connection" 
        self.connection = CallsHandler()
        print("Got mock connection")
        return self.connection

    def close_connection(self):
        print("Closed mock connection")
        

class CallsHandler():
    """
    Imitates some behavior of SSHConnection class in Connections ssh.py script.  
    Additionally imitates and handles all calls as if it was the ucloud slurm. Calls the hpc api with successes only.
    Uploads a mock file to ars, and sends mock data in all cases where its relevant.
    """

    def __init__(self):
        
        self.mock_file_path = f"{project_root}/MockServers/mock.tif"
        
        self.util = utility.Utility()

        self.hpc_api = caller_hpc_api.CallerHPCApi()


    def ssh_command(self, command, output_path=None):

        command_tuple = command.split()

        guid = command_tuple[2]

        script_tuple = command_tuple[1].split("/")

        job_script = input(script_tuple[-1])

        # add more jobs here if needed
        match job_script:
            case "barcodeReader.sh":
                self.barcode_handler(guid)
            case "cropping.sh":
                self.cropping_handler(guid)
            case "derivative.sh":
                self.derivative_handler(guid)
            case "assetLoader.sh":
                self.asset_loader_handler(guid)
            case "assetUploader.sh":
                self.asset_uploader_handler(guid)
            case "assetDeleter.sh":
                self.asset_deleter_handler(guid)
        
        return command
    
    def barcode_handler(self, guid):
        job_name = ""
    
    def cropping_handler(self, guid):
        job_name = ""

    def derivative_handler(self, guid):
        job_name = ""

    def asset_uploader_handler(self, guid):
        job_name = ""

    def asset_loader_handler(self, guid):
        timestamp = datetime.datetime.now().isoformat()

        job_dict = {
                "guid": guid,
                "job_name": "assetLoader",
                "job_id": "mock_asset_loader",
                "timestamp": timestamp}
        
        self.queue_job(job_dict)
        time.sleep(1)
        self.start_job(job_dict)
        time.sleep(1)
        self.asset_ready(guid)
        time.sleep(1)

        update_dict={
            "guid": guid,
            "job": "assetLoader",
            "status": "DONE",
            "data": {}}
        
        self.update_asset(update_dict)

    def asset_deleter_handler(self, guid):

        timestamp = datetime.datetime.now().isoformat()

        job_dict = {
                "guid": guid,
                "job_name": "clean_up",
                "job_id": "mock_clean_up",
                "timestamp": timestamp}
        
        self.queue_job(job_dict)
        time.sleep(1)
        self.start_job(job_dict)
        time.sleep(1)
        self.asset_clean_up(guid)

    def derivative_file_uploaded(self, guid):
        self.hpc_api.derivative_file_uploaded(guid)

    def asset_clean_up(self, guid):
        self.hpc_api.asset_clean_up(guid)

    def receive_derivative(self, metadata):
        self.hpc_api.receive_derivative_metadata(metadata)

    def update_asset(self, update_data):
        self.hpc_api.update_asset(update_data)

    def insert_barcode(self, barcode_data):
        self.hpc_api.insert_barcode(barcode_data)

    def queue_job(self, job_data):
        self.hpc_api.queue_job(job_data)

    def start_job(self, job_data):
        self.hpc_api.start_job(job_data)

    def failed_job(self, fail_job_data):
        self.hpc_api.failed_job(fail_job_data)
    
    def asset_ready(self, asset_guid):
        self.hpc_api.asset_ready(asset_guid)

    def file_info(self, file_info_data):
        self.hpc_api.file_info(file_info_data)
    


    
    


        
