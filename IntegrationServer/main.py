import logging.handlers
import os
import utility
import sys
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
from MongoDB import mongo_connection, track_repository, health_repository, service_model, metadata_repository, throttle_repository
from Ndrive import ndrive_new_files
import IntegrationServer.Ndrive.process_files_from_ndrive as process_files_from_ndrive
from StorageApi import storage_client, ars_health_check, storage_service
from HpcSsh import hpc_job_caller, hpc_asset_creator
import json
import time
#from PIL import Image, TiffImagePlugin, TiffTags
#from PIL.TiffImagePlugin import ImageFileDirectory_v2
#from pyexiv2 import Image as ImgMeta
from bson.json_util import dumps
from datetime import datetime, timedelta
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
    
    #throttle  = throttle_repository.ThrottleRepository()
    #throttle.subtract_from_amount("total_new_asset_size_mb", "value", 15000) 
    #throttle.subtract_from_amount("total_asset_size_mb", "value", 15000) 
    
    #throttle.reset_throttle()
    """
    mp = micro_service_paths.MicroServicePaths()

    print(mp.get_path_from_name("Delete local files"))

    #call = caller_hpc_api.CallerHPCApi()

    u = utility.Utility()

    track = track_repository.TrackRepository()
    meta = metadata_repository.MetadataRepository()
    throttle  = throttle_repository.ThrottleRepository()
    
    #throttle.reset_throttle()
    
    #guid = "dev-ucloud-926"
    a = u.convert_json_to_utf8("\u00c3\u00b8")
    print(a)
    #track.update_track_job_status(guid, "uploader", "DONE")
    #track.update_entry(guid, "jobs_status", "DONE")
    #track.update_entry(guid, "has_open_share", "NO")
    #track.update_entry(guid, "hpc_ready", "NO")
    #track.update_track_job_data_point(guid, "priority", 2, "status", "DONE")

    #[{key: value, key: value}]
    list = track.get_entries_from_multiple_key_pairs([{"temporary_files_ndrive":"ERROR", "batch_list_name":"WORKHERB0001_2024-09-12"}])
    
    #list = track.get_entries("_id", "7e7-a-04-0d-1b-0c-1-001-01-000-0d4d5b-00000_400")

    #track.update_entry(guid, "available_for_services", "YES")
    #track.update_entry(guid, "available_for_services_timestamp", None)
    #track.update_entry(guid, "available_for_services_wait_time", None)

    #track.update_track_job_status("7e6-8-13-01-06-18-0-001-00-000-0ec096-00000", "barcode", "WAITING")
    #track.update_entry("7e6-8-13-01-06-18-0-001-00-000-0ec096-00000", "jobs_status", "WAITING")
    #list = track.get_error_entries()
    
    #sc = storage_client.StorageClient()
    #hpc_caller = caller_hpc_api.CallerHPCApi()
    #p = hpc_caller.say_hi()
    #print(p)
    #h = 0
    #second_attempted, second_status_code, second_asset_status, second_asset_share_size, second_note = sc.get_asset_sharesize_and_status(guid)
    #print(second_attempted, second_status_code, second_asset_status, second_asset_share_size, second_note)
    
    f = 0
    for l in list:
        guid = l["_id"]
        print(guid)
        #hpc_caller.asset_clean_up(guid)
        #track.update_entry(guid, "temporary_files_ndrive", "YES")
        #track.update_entry(l["_id"], "jobs_status", "DONE")
        
        #track.update_track_job_status(l["_id"], "assetLoader", "WAITING")
        f += 1
        #full_status = sc.get_full_asset_status(guid)
        
        #if full_status["data"].share_allocation_mb is not None:
            #track.update_entry(guid, "has_open_share", "YES")

        #job = track.get_job_info(l["_id"], "uploader")
        #track.update_entry(l["_id"], "has_open_share", "YES")
        #if job["status"] == "STARTING":
            #print(l["_id"])
            #track.update_track_job_status(l["_id"], "uploader", "WAITING")
            #track.update_entry(l["_id"], "jobs_status", "WAITING")
            #h += 1
        #else:
            #print(guid)
        #x = sc.check_file_uploaded(l["_id"])
        #if x is True:
        #    call.derivative_file_uploaded(guid)
        #if x is False:
        #    track.update_entry(l["_id"], "jobs_status", "DONE")
        #    track.update_track_job_status(l["_id"], "assetLoader", "WAITING")
        #    track.update_entry(l["_id"], "has_new_file", "YES")    
        # pass
        #track.update_entry(l["_id"], "jobs_status", "WAITING")
        #track.update_track_job_status(l["_id"], "assetLoader", "WAITING")
        #track.update_entry(l["_id"], "has_open_share", "YES")
        
    print(f)
    

    throttle.close_connection()
    track.close_connection()
    meta.close_connection()
    """
    #try:
    #    test_exception()
    #except Exception as e:
    #    print(e)
    #guid = "7e7-a-04-0d-25-05-1-001-01-000-0557a6-00000_400"
    #track.update_track_job_status(guid, "uploader", "DONE")

    #f = "'b200 ad"
    #print(int(f[2:5]))
    #x = track.all.get_count_for_key_value_pair("hpc_ready", "AWAIT")
    #y = track.all.calculate_values_for_fields_with_key_value("asset_size", "has_open_share", "ERROR")
    #z = track.all.multiple_key_values_calculate_field_total_value("asset_size", [{"has_open_share":"YES", "erda_sync":"ERROR"}])
    #print(f"multiple key value: {z}")
    #print(f"total single key-value: {y}")
    #print(f"count: {x}")
    #track.close_connection()
    
    
    #i = IntegrationServer()

    #t = i.util.get_nested_value(i.service_config_path, "File uploader ARS", "mail_wait_time")
    #print(t)
    
    #u = utility.Utility()
    #c = {"h":1, "b":2}
    #print(c["h"])
    #a = u.find_key_by_value(c, 2)
    #a = u.convert_json_to_utf8({"id":"\u00c3\u00b8ab"})
    #print(a)
    #a = asset_handler.AssetHandler()   
    #name = a.find_directory_name_with_file("/work/data/Ndrive/WORKHERB0002", "7e7-a-04-0d-1e-1b-1-001-01-000-098b37-00000.json")
    #print(name)
    
    #logging.basicConfig(filename="myapp.log", format='%(levelname)s:%(asctime)s:%(name)s:%(message)s:%(exc_info)s', encoding="utf-8", level=logging.INFO)
    #test() 2024-04-09T10:00:52+02:00
    #test()
    #t = datetime.now() - timedelta(hours=1000)
    #load_dotenv()
    #print(os.environ.get("UCLOUD_USER"))

    #throttle_config_path = f"{project_root}/IntegrationServer/ConfigFiles/throttle_config.json"
    #print(throttle_config_path)
    
    #max_total_asset_size = utility.Utility().get_value(file_path=throttle_config_path, key="total_asset_size_mb")
    #print(max_total_asset_size)
    #e = email_sender.EmailSender("test")

    #e.send_status_change_mail("h", "Test health api", "bogus", None)
    #test_mail()
    """
    mongo = track_repository.TrackRepository()
    
    mongo.update_track_job_list("dev-ucloud-400", "attempt_1", "name", f"assetLoader")
    a = mongo.get_job_from_key_value("dev-ucloud-400", "name", "assetLoader")
    print(a)
    mongo.close_connection()
    """
    """
    time = ""
    b = field_validation.FieldValidation().datetime_validator(time)
    print(b)
    x = validators.datetime(time, allow_empty=True)
    y = checkers.is_datetime(x)
    print(x, y, type(x))
    """
    """
    Image.MAX_IMAGE_PIXELS = None
    new_exif_data = {
    270: "New Description",  # Tag 270 is for ImageDescription
    305: "New Software"      # Tag 305 is for Software
}

    modify_exif_data("C:/Users/tvs157/Desktop/first.tif", new_exif_data)

    exif_data("C:/Users/tvs157/Desktop/first3.tif")
    """
    """
    with ImgMeta("C:/Users/tvs157/Desktop/first2.tif") as img_meta:

        exif = img_meta.read_exif()
        
        a = exif.items()

        for key, value in a:
            print(key, value)

        #img_meta.modify_exif({305: "Lars' studio"})


    exif_data("C:/Users/tvs157/Desktop/first2.tif")
    """
    #i = IntegrationServer()
    #test()
    #x()
    

        
    