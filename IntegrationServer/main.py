import asyncio
import logging.handlers
import os
import utility
import sys
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
from MongoDB import mongo_connection, track_repository, health_repository, service_model, metadata_repository, throttle_repository, service_repository
from Ndrive import ndrive_new_files
import IntegrationServer.Ndrive.process_files_from_ndrive as process_files_from_ndrive
from StorageApi import storage_client, ars_health_check, storage_service
from HpcSsh.LUMIScripts import lumi_ssh_setup
from HpcSsh import hpc_job_caller, hpc_asset_creator
import json
import time
from dassco_utils.guid import main
from dassco_utils.metadata import MetadataModel, MetadataHandler
from dassco_utils.messaging import orchestration_client, async_rabbitmq_client, OrchestrationEvent
from bson import ObjectId
from rabbitmq_client import RabbitMqClient as rmq
from dasscostorageclient import DaSSCoStorageClient
from KeycloakInterface import auth
from MongoDB.mongo_connection import MongoSharedClient
from field_validation import FieldValidation

#from PIL import Image, TiffImagePlugin, TiffTags
#from PIL.TiffImagePlugin import ImageFileDirectory_v2
#from pyexiv2 import Image as ImgMeta
from bson.json_util import dumps
import datetime
from dotenv import load_dotenv
import InformationModule.email_sender as email_sender
import InformationModule.slack_webhook as slack_webhook
from InformationModule import issue_writer
import subprocess
import logging
from Connections import connections
from HealthUtility import health_caller, caller_hpc_api
from Enums.feedback_enum import Feedback
from Enums.feedback_enum import FeedbackEnum
from HealthApi import health_service
from HealthUtility.run_utility import LogClass
from AssetFileHandler import asset_handler
from DashboardAPIs import micro_service_paths
import traceback
#from pymongo.errors import InvalidOperation
#import field_validation
""""
Test area for the different processes. May contain deprecated information.
"""

class IntegrationServer(object):
    """
    Test text.
    """
    def __init__(self):
        self.util = utility.Utility()

        self.new_files_path = "IntegrationServer/Files/NewFiles/"
        self.updated_files_path = "IntegrationServer/Files/UpdatedFiles/"
        self.ssh_config_path = f"{project_root}/IntegrationServer/ConfigFiles/ucloud_connection_config.json"
        self.service_config_path = (f"{project_root}/IntegrationServer/ConfigFiles/micro_service_config.json")
        
        cons = connections.Connections()
        cons.create_ssh_connection(self.ssh_config_path)
        cons.close_connection()
        load_dotenv()    

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

def exif_data(path_name):
    f = open(path_name, 'rb')

    # Return Exif tags
    tags = exifread.process_file(f)

    

    for tag in tags.keys():
        #if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
        #print(tag)
        print("Key: %s, value %s" % (tag, tags[tag]))

def modify_exif_data(file_path, new_exif_data):
    # Open the image file with Pillow
    with Image.open(file_path) as img:
        # Convert to single-strip format
        img = img.convert("RGB")  # Convert to RGB to simplify the process

        # Create a new EXIF data object
        exif_dict = img.getexif()

        print(img.getexif().bigtiff)
        
        for tag, value in exif_dict:
            print(tag, value)
        
        # Update the EXIF data with new values
        for tag, value in new_exif_data.items():
            print(tag, value)
            exif_dict[tag] = value

        # Save the image with the modified EXIF data back to the same file
        img.save("C:/Users/tvs157/Desktop/first3.tif", tiffinfo=exif_dict)

def test_mail():
    subject = "TEST"
    message = "testing"
    # Specify the sender in the From header
    email_headers = f"From: yod\nTo: bogus@snm.ku.dk\nSubject: {subject}\n\n"
    # The complete email content with headers and message
    email_content = f"{email_headers}{message}"

    # Using subprocess.Popen for sending the email
    command = ['sendmail', "bogus@snm.ku.dk"]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True)
    # Send the email content via the process
    process.communicate(input=email_content)

def test_exception():
    try:
        a = 1/0
    except:
        raise Exception("fun")
    
def add_d_clean_up_job(guid):
        
        track = track_repository.TrackRepository()
        job = {
                "name": "clean_up",
                "status": "WAITING",
                "priority": 2,
                "job_queued_time": None,
                "job_start_time": None,
                "hpc_job_id": -9,
                }
                    
        track.append_existing_list(guid, "job_list", job)
        track.close_connection()

def add_clean_up_job(guid):
        
        track = track_repository.TrackRepository()
        job = {
                "name": "clean_up",
                "status": "WAITING",
                "priority": 5,
                "job_queued_time": None,
                "job_start_time": None,
                "hpc_job_id": -9,
                }
                    
        track.append_existing_list(guid, "job_list", job)
        track.close_connection()

def add_upload_job(guid):
        track = track_repository.TrackRepository()
        job = {
            "name": "uploader",
            "status": "WAITING",
            "priority": 1,
            "job_queued_time": None,
            "job_start_time": None,
            "hpc_job_id": -9,
            }

        track.append_existing_list(guid, "job_list", job)
        track.close_connection()


async def test_oc():
     
    connection_options = async_rabbitmq_client.ConnectionOptions()
    connection_options.host_name = "hostname"
    connection_options.username = "user"
    connection_options.password = "password"
    connection_options.enable_tls = False

    retry_config = async_rabbitmq_client.RetryConfig()
    retry_config.retry_delays = [60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 300000]  # 11 retries, each after 60 seconds last after 5 minutes

    armq = async_rabbitmq_client.AsyncRabbitMqClient(options=connection_options, retry_config=retry_config)
    
    oc = orchestration_client.OrchestrationClient(mq_client=armq, service_name="Starfish")

    @oc.handler("check_something")
    async def print_something(event: OrchestrationEvent):
        print("Hello from async rabbitmq client!", event)
        return {"status": "done"}

    await oc.register_handlers()

    await armq.loop()

def find_directory_name_with_file(parent_directory, filename):
        """
        Search for the directory name containing the specified filename within the parent directory.

        Args:
            parent_directory (str): The root directory to start the search.
            filename (str): The name of the file to look for.

        Returns:
            str: The name of the directory containing the file, or None if not found.
        """
        for dirpath, _, filenames in os.walk(parent_directory):
            if filename in filenames:
                return os.path.basename(dirpath) 
        return None

if __name__ == '__main__':

    guid = "040ck2b867e9a0306142212233b675_400"
    sc = storage_client.StorageClient()

    found, file_list, status_code = sc.get_files_info(guid)

    print(found, file_list, status_code)

    """
    load_dotenv()
    home_path = os.getenv("HPC_ASSET_DIRECTORY")
    job_id = 21379691
    guid= "040ck2b867e9a07073005162f12635_400"
    client = MongoSharedClient()
    track = track_repository.TrackRepository(client)
    metadata = metadata_repository.MetadataRepository(client)
    cons = connections.Connections(client)
    cons.create_ssh_connection("lumi")
    con = cons.get_connection()

    info = track.get_file_info(guid, "tif")
    print(info)
    # cases to solve:
        # fail state: CANCELLED, TIMEOUT, FAIELD, OUT_OF_MEMORY, NODE_FAIL, PREEMPTED
        # unresolved state: PENDING, RUNNING
        # check asset status state: COMPLETED
        # others
        # nothing
    expected_file_size = info["file_size"]
    pgs = metadata.get_value_for_key(guid, "parent_guids")
    if pgs is not None:
        pg = pgs[0]
        batchlist_name = track.get_value_for_key(pg, "batch_list_name")              
    else:
        batchlist_name = track.get_value_for_key(guid, "batch_list_name")
    path = os.path.join(home_path, batchlist_name)
    
    response = con.ssh_command(f"ls -ll {path} | grep {guid}")
    
    lines = response.strip().splitlines()

    if len(lines) < 2:
        print("Expected at least 2 files")
    else:
        jpg_line = next((line for line in lines if ".jpeg" in line), None)
        tif_line = next((line for line in lines if ".tif" in line), None)
        json_line = next((line for line in lines if ".json" in line), None)

        if tif_line and json_line:
            file_size_bytes = int(tif_line.split()[4])
            file_size_mb = round(file_size_bytes / (1000 * 1000), 0)

            print(f"TIF size: {file_size_mb} MB")

        if jpg_line and json_line:
            file_size_bytes = int(jpg_line.split()[4])
            file_size_mb = round(file_size_bytes / (1000 * 1000), 0)
            print(f"JPEG size: {file_size_mb} MB")

    if expected_file_size == file_size_mb:
         print("success")
        
    cons.close_connection()
    track.close_connection()
    """
    """
    client = MongoSharedClient()
    
    track = track_repository.TrackRepository(client)

    c =track.count_assets_in_hpc_load_state()

    b = track.count_assets_in_download_state()

    a = track.count_assets_in_upload_state()

    print(a)
    print(c)
    print(b)

    track.close_connection()
    """
    