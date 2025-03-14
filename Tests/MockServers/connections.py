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

    def derivative_handler(self, guid):

        job = "derivative"
        guid_72 = f"{guid}_72"
        guid_400 = f"{guid}_400"
        derivative_metadata = self.util.read_json(f"{project_root}/Mockservers/derivative_metadata.json")

        update_dict = self.get_update_dict(guid, job)
        job_dict = self.get_job_dict(guid, job)

        file_info_72 = {"guid": guid_72,
                    "name": f"{guid_72}.jpg",
                    "type": "jpg",
                    "check_sum": 123,
                    "file_size": 12
                    }

        file_info_400 = {"guid": guid_400,
                    "name": f"{guid_400}.jpg",
                    "type": "tif",
                    "check_sum": 123,
                    "file_size": 12
                    }

        self.queue_job(job_dict)
        time.sleep(1)
        self.start_job(job_dict)
        time.sleep(1)

        metadata_json = self.get_metadata(guid)
        derivative_metadata["asset_guid"] = guid_72
        time.sleep(1)
        self.receive_derivative(derivative_metadata)
        time.sleep(1)
        self.file_info(file_info_72)
        time.sleep(1)

        metadata_json = self.get_metadata(guid)
        derivative_metadata["asset_guid"] = guid_400
        time.sleep(1)
        self.receive_derivative(derivative_metadata)
        time.sleep(1)
        self.file_info(file_info_400)
        time.sleep(1)

        self.update_asset(update_dict)


    def asset_uploader_handler(self, guid):

        job = "uploader"

        job_dict = self.get_job_dict(guid, job)

        self.queue_job(job_dict)
        time.sleep(1)
        self.start_job(job_dict)
        time.sleep(1)

    def cropping_handler(self, guid):

        job = "cropping"

        job_dict = self.get_job_dict(guid, job)
        
        update_dict = self.get_update_dict(guid, job)

        self.queue_job(job_dict)
        time.sleep(1)
        self.start_job(job_dict)
        time.sleep(1)
        self.update_asset(update_dict)

    def barcode_handler(self, guid):

        job = "barcode"

        job_dict = self.get_job_dict(guid, job)

        update_dict = self.get_update_dict(guid, job, {"payload_type":"image"})
        
        barcode_dict = {"guid": guid,
                    "job": job,
                    "status": "DONE",
                    "barcodes": ["mock_barcode"],
                    "asset_subject": "specimen",
                    "MSO": False,
                    "MOS": False,
                    "label": False,
                    "disposable": None}

        self.queue_job(job_dict)
        time.sleep(1)
        self.start_job(job_dict)
        time.sleep(1)
        self.insert_barcode(barcode_dict)
        time.sleep(1)
        self.update_asset(update_dict)


    def asset_loader_handler(self, guid):
        
        job = "assetLoader"

        job_dict = self.get_job_dict(guid, job)
        
        update_dict= self.get_update_dict(guid, job)

        self.queue_job(job_dict)
        time.sleep(1)
        self.start_job(job_dict)
        time.sleep(1)
        self.asset_ready(guid)
        time.sleep(1)        
        self.update_asset(update_dict)

    def asset_deleter_handler(self, guid):

        job_dict = self.get_job_dict(guid, "clean_up")
        
        self.queue_job(job_dict)
        time.sleep(1)
        self.start_job(job_dict)
        time.sleep(1)
        self.asset_clean_up(guid)

    def get_job_dict(self, guid, job):
        timestamp = datetime.datetime.now().isoformat()
        job_dict = {
                "guid": guid,
                "job_name": job,
                "job_id": "mock_id",
                "timestamp": timestamp}
        return job_dict
    
    def get_update_dict(self, guid, job, data={}):

        update_dict={
            "guid": guid,
            "job": job,
            "status": "DONE",
            "data": data}
        
        return update_dict

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

    def get_metadata(self, guid):
        return self.hpc_api.get_metadata_asset(guid)
    


    
    


        
