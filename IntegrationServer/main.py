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
from HpcSsh import hpc_job_caller, hpc_asset_creator
import json
import time
from dassco_utils.guid import main
from dassco_utils.metadata import MetadataModel, MetadataHandler
from bson import ObjectId
from rabbitmq_client import RabbitMqClient as rmq
from dasscostorageclient import DaSSCoStorageClient

#from PIL import Image, TiffImagePlugin, TiffTags
#from PIL.TiffImagePlugin import ImageFileDirectory_v2
#from pyexiv2 import Image as ImgMeta
from bson.json_util import dumps
import datetime
from dotenv import load_dotenv
import InformationModule.email_sender as email_sender
import InformationModule.slack_webhook as slack_webhook
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
#from validator_collection import checkers, validators
""""
Test area for the different processes. May contain deprecated information.
"""

class IntegrationServer(object):
    """
    Test text
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

def test():
    util = utility.Utility()
    #field = field_validation.FieldValidation()
    # jobby = job_driver.JobDriver()
    # cons = connections.Connections()
    # api = northtech_rest_api.APIUsage()
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
    #email.send_error_mail("abc", service_name="Test health api")
    #sl = slack_webhook.SlackWebhook()
    #sl.message_from_integration("Lars", "MIGHTY WARRIOR", "GET WELL")
    #util.write_full_json(relPath, entry)
    track = track_repository.TrackRepository()
    #track.update_entry("7e8-4-09-0a-00-34-0-001-00-000-0b8ab2-00000", "has_new_file", "POSSIBLE")
    print(track.get_entry("_id", "dev-ucloud-865"))
    
    #c = health_caller.HealthCaller()
    #c.warning(service="main", message="ERROR#2024-05-30 14:26:25,053#xd.py#yolo#trouble shoot message")
    #h = health_repository.HealthRepository()
    #p = h.get_recent_errors("some service", 2000000)
    #print(p[0:7])
    #h.close_connection()
    #a = util.check_value_in_enum(None, FeedbackEnum)
    
    #a = field.is_acceptable_string("asset-guid-53268-æææ")
    #print(a)

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

if __name__ == '__main__':   

    #md = metadata_repository.MetadataRepository()
    ser = storage_service.StorageService()
    sclient = storage_client.StorageClient()

    load_dotenv()
    
    client_id = os.getenv("client_id")
    client_secret = os.getenv("client_secret")

    service_username = "STARFISH"

    status = sclient.get_full_asset_status("040ck2b867e98130f173b07c8ba882")

    print(type(status["data"]), status["data"].error_message)

    if "something" in status["data"].error_message:
        print("yes")

    #u = utility.Utility()

    #crc = u.calculate_crc_checksum("/work/data/Dev-Integration/DaSSCo-Integration/IntegrationServer/Files/InProcess/PIPEHERB0001/2025-08-11/040ck2b867e98130f173b07c8ba882/040ck2b867e98130f173b07c8ba882.tif")
    #print(crc)
    """
    load_dotenv()
    user = os.getenv("rabbit_user")
    pw = os.getenv("rabbit_pw")
    
    rmc = rmq(host_name="biovault.bhsi.xyz", port=5671, credentials={"username":user, "password":pw})
    
    rmc.publish("my_queue", "yolo")
    """
    #rmc.add_handler("first_test", print_something)

    #rmc.publish("metadata-info-queue", {"metadata":{"guid": "asdih123", "digi":"\u00c5se \u00d8sterb\u00e6k-\u00c6r\u00f8"}, "file":{"name":"sem", "size":34}})
    """
    """
    #rmc.publish("first_test", {"asd":4})

    #rmc.start_consuming()

    #rmc.publish("first_test", {"asd":1})
    #rmc.publish("first_test", {"asd":4})
    
    #m = rmc.consume_one("first_test")
    #if m is not None:
    #    m = json.loads(m)
    #print(type(m))
    #print(m["asset"])

    
