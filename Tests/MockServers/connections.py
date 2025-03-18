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
from IntegrationServer.StorageApi import storage_client

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
        
        self.mock_derivative_file = f"{project_root}/Mockservers/MockData/derivative_metadata.json"
        self.mock_72_file = f"{project_root}/Mockservers/MockData/72.jpeg"
        self.mock_400_file = f"{project_root}/Mockservers/MockData/400.tif"
        
        self.util = utility.Utility()

        self.hpc_api = caller_hpc_api.CallerHPCApi()

        # get size and crc values for mock files. 
        self.size_72 = self.util.calculate_file_size_round_to_next_mb(self.mock_72_file)
        self.size_400 = self.util.calculate_file_size_round_to_next_mb(self.mock_400_file)
        
        self.crc_72 = self.util.calculate_crc_checksum(self.mock_72_file)
        self.crc_400 = self.util.calculate_crc_checksum(self.mock_400_file)

        # get mock metadata used for derivatives (this is not following metadata versions so changes needs to be made manually to the mock data)
        self.derivative_metadata = self.util.read_json(self.mock_derivative_file)

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

        update_dict = self.get_update_dict(guid, job)
        job_dict = self.get_job_dict(guid, job)

        self.derivative_metadata["parent_guid"] = guid

        file_info_72 = {"guid": guid_72,
                    "name": f"{guid_72}.jpg",
                    "type": "jpg",
                    "check_sum": self.crc_72,
                    "file_size": self.size_72
                    }

        file_info_400 = {"guid": guid_400,
                    "name": f"{guid_400}.tif",
                    "type": "tif",
                    "check_sum": self.crc_400,
                    "file_size": self.size_400
                    }

        self.queue_job(job_dict)
        time.sleep(1)
        self.start_job(job_dict)
        time.sleep(1)

        metadata_json = self.get_metadata(guid)
        self.derivative_metadata["asset_guid"] = guid_72
        self.derivative_metadata["file_format"] = "jpg"
        time.sleep(1)
        self.receive_derivative(self.derivative_metadata)
        time.sleep(1)
        self.file_info(file_info_72)
        time.sleep(1)

        metadata_json = self.get_metadata(guid)
        self.derivative_metadata["asset_guid"] = guid_400
        self.derivative_metadata["file_format"] = "tif"
        time.sleep(1)
        self.receive_derivative(self.derivative_metadata)
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

        # upload file
        try:
            client = storage_client.StorageClient()

            if guid[:-3] == "_72":
                file = self.mock_72_file
                size = self.size_72
            else:
                file = self.mock_400_file
                size = self.size_400

            client.upload_file(guid, "test-institution", "test-collection", file, size)

            time.sleep(1)
            self.derivative_file_uploaded(guid)
        except Exception as e:
            print(f"Will wait 5 minutes before trying next: Failed uploading a file: {e}")
            time.sleep(300)
            

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
