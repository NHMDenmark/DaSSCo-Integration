import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import shutil
import utility
from AssetFileHandler import job_assigner
from HealthUtility import health_caller
from MongoDB import file_model, track_repository, metadata_repository, batch_repository, throttle_repository
from MongoDB.mongo_connection import MongoSharedClient
from Enums import status_enum, validate_enum, metadata_origin, log_enum, asset_status_nt, flag_enum
import json
from datetime import datetime
from dotenv import load_dotenv
from InformationModule import issue_writer

"""
Responsible for the processing/creation of assets coming from the Ndrive. 
"""

class AssetHandlerTwo:

    def __init__(self, run_util, mongo_client: MongoSharedClient = None):

        load_dotenv()

        self.util = utility.Utility()
        self.jobby = job_assigner.JobAssigner()
        self.status = status_enum.StatusEnum
        self.validate = validate_enum.ValidateEnum
        self.log_enum = log_enum.LogEnum
        self.flag_enum = flag_enum.FlagEnum
        self.origin = metadata_origin.MetadataOriginEnum
        self.asset_status_nt = asset_status_nt.AssetStatusNT
        self.file_model = file_model.FileModel()
        self.issue_writer = issue_writer.IssueWriter()

        self.ndrive_path = os.getenv("NDRIVE_PATH")

        self.mongo_config_path = f"{project_root}/ConfigFiles/mongo_connection_config.json"
        self.micro_service_config_path = f"{project_root}/ConfigFiles/micro_service_config.json"

        if mongo_client is None:
            self.mongo_client = MongoSharedClient()
        else:
            self.mongo_client = mongo_client
        self.mongo_track = track_repository.TrackRepository(self.mongo_client)
        self.mongo_metadata = metadata_repository.MetadataRepository(self.mongo_client)
        self.mongo_batchlist = batch_repository.BatchRepository(self.mongo_client)
        self.mongo_throttle = throttle_repository.ThrottleRepository(self.mongo_client)

        self.health_caller = health_caller.HealthCaller()
        self.run_util = run_util

    def process_new_assets(self, directory_name: str):

        new_directory_path = directory_name
        print(f"Processing new assets in directory: {new_directory_path}")

        for file in os.listdir(new_directory_path):
            
            file_name, file_extension = os.path.splitext(file)
            img_file_path = os.path.join(self.ndrive_path, directory_name, file)
            json_file_path = None

            if file_extension.lower() in [".tif"]:

                # check if asset already exists in the database
                exists = self.mongo_track.get_entry("_id", file_name)
                if exists is not None:
                    print(f"Asset {file_name} already exists in the database. Skipping.")
                    continue

                # check if file has a json and sets the json_file_path variable
                json_file_path = os.path.join(new_directory_path, f"{file_name}.json")
                if not os.path.exists(json_file_path):
                    print(f"JSON file for {file_name} does not exist. Skipping the tif file.")
                    entry = self.run_util.log_msg(self.run_util.prefix_id, f"JSON file for {file_name} does not exist in {new_directory_path}.", self.status.ERROR.value)
                    self.health_caller.error(self.run_util.service_name, entry)
                    continue

            if file_extension.lower() in [".json"]:

                # check if file has a tif
                tif_file_path = os.path.join(new_directory_path, f"{file_name}.tif")
                if not os.path.exists(tif_file_path):
                    print(f"TIF file for {file_name} does not exist. Skipping.")
                    entry = self.run_util.log_msg(self.run_util.prefix_id, f"TIF file for {file_name} does not exist in {new_directory_path}.", self.status.ERROR.value)
                    self.health_caller.error(self.run_util.service_name, entry)
                    continue
                else:
                    continue  # Skip processing the JSON file if the TIF file exists, as it will be processed in the TIF block

            # Read the JSON file to get the 'pipeline_name', 'guid', image extension, batch name, issues and barcodes
            pipeline_name = self.util.get_value(json_file_path, "pipeline_name")
            guid = self.util.get_value(json_file_path, "asset_guid")
            parent = self.util.get_value(json_file_path, "parent_guids")
            collection = self.util.get_value(json_file_path, "collection")
            issues = self.util.get_value(json_file_path, "issues")
            barcodes = self.util.get_value(json_file_path, "barcode")
            asset_subject = self.util.get_value(json_file_path, "asset_subject")
            workstation_name = self.util.get_value(json_file_path, "workstation_name")                

            try:
                # TODO have this resolved
                # hacking with the institution check since NHMA is using the PIPEPIOF0001 pipeline which belongs to NHMD
                institution = self.util.get_value(json_file_path, "institution")
            
                if institution == "NHMA":
                    pipeline_name = "PIPEPIOF0002"
                    self.util.update_json(json_file_path, "pipeline_name", pipeline_name)
            
                # TODO hacking the collection to fit with what is in SPECIFY - Vascular Plants to NHMD Vascular Plants
                if collection == "Vascular Plants":
                    collection = "NHMD Vascular Plants"
                    self.util.update_json(json_file_path, "collection", collection)
            
                # TODO hacking the asset_pid to fit with what is in ARS - ADDED_ + guid
                asset_pid = self.util.get_value(json_file_path, "asset_pid")
                if asset_pid is None or asset_pid == "":
                    asset_pid = "ADDED_" + guid
                    self.util.update_json(json_file_path, "asset_pid", asset_pid)
            
                # TODO handle if there can only ever be one image added to an asset here... not sure this is true though
                # image_extension = []
                # for format in self.util.get_value(json_file_path, "file_format"):
                # format = "." + format
                # image_extension.append(format)
                image_extension = self.util.get_value(json_file_path, "file_format")
                date_value = self.util.get_value(json_file_path, "date_asset_taken")
                batch_name = ""
            
                if date_value is not None:
                    batch_name = date_value[:10]
                else:
                    #TODO handle if there is no date in the metadata - set to current date
                    continue
                                        
                #Add new track entry to mongoDB
                self.mongo_track.create_track_entry(file_name, pipeline_name, self.origin.NDRIVE.value )
            
                # safety lock - set available for services to NO
                safety_flag = True # set this to false if something is wrong later on
                self.mongo_track.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate.NO.value)
            
                # default asset size
                asset_size = -1
            
                # Add image file checksums(s) and img file size to track entry, calculates total asset size
                #for extension in image_extension:                                
                #extension = image_extension
                #img_file_name = json_file_name.replace('.json', f".{extension}")
                #img_file_path = os.path.join(subdirectory_path, img_file_name)
            
                img_size = self.util.calculate_file_size_round_to_next_mb(img_file_path)
                check_sum = self.util.calculate_crc_checksum(img_file_path)
                file_type = file_extension
                file_type = file_type[-3:]
            
                self.file_model = file_model.FileModel()
            
                self.file_model.file_size = img_size
                self.file_model.check_sum = check_sum
                self.file_model.erda_sync = self.validate.NO.value
                self.file_model.name = file_name
                self.file_model.type = file_type
                self.file_model.deleted = False
                                            
                file_data = self.file_model.model_dump_json()
            
                file_data = json.loads(file_data)
            
                self.mongo_track.append_file_list(guid, file_data)
            
                if asset_size == -1:
                    asset_size = img_size
                else:
                    asset_size = asset_size + img_size
            
                # Sets asset size to the total amount of required space in mb
                if asset_size != -1:
                    self.mongo_track.update_entry(guid, "asset_size", asset_size)    
            
                # updates has new file enum if files were added
                if len(image_extension) > 0:
                    self.mongo_track.update_entry(guid, "has_new_file", self.validate.YES.value)
            
                # Add batchlist name to the track entry
                batchlist_name = workstation_name + "_" + batch_name
                self.mongo_track.update_entry(guid, "batch_list_name", batchlist_name)
            
                # Add asset to batch list in mongodb
                self.mongo_batchlist.add_entry_to_list(guid, batchlist_name)
            
                # handling cases with parent not being a list
                if isinstance(parent, list) is False:
                                        
                    if parent != None and parent != "":                            
                        parent = [parent]
                        self.util.update_json(json_file_path, "parent_guids", parent)
                        print(f"parent_guid for {guid} was not nothing and also not a list, and has been appended into a list.")
                    else:
                        print(f"parent_guid for {guid} was not a list and a empty list has been created.")
                        self.util.update_json(json_file_path, "parent_guid", [])
            
                # Add new metadata entry to mongoDB
                self.mongo_metadata.create_metadata_entry(json_file_path, guid)
                #print(f"create metadata: {check}")                                    
                self.mongo_metadata.update_entry(guid, "status", self.asset_status_nt.BEING_PROCESSED.value)
            
                self.mongo_track.update_entry(guid, "temporary_files_ndrive", self.validate.YES.value)
                self.mongo_track.update_entry(guid, "temporary_path_ndrive", directory_name)
           
                self.mongo_track.update_entry(guid, "is_in_ars", self.validate.NO.value)
            
                # Check for barcodes in metadata if they exist set has_new_specimen to YES
                if  barcodes:
                    self.mongo_track.update_entry(guid, self.flag_enum.HAS_NEW_SPECIMEN.value, self.validate.YES.value)
            
                # check for issues that barcodes have been added manually, if so update barcode reading job status to SKIPPED
                service_config = self.util.get_value(self.micro_service_config_path, "Process new files (Ndrive)")
                issue_names = service_config["barcode_issue_names"]
                                    
                if issue_names:
                    for issue in issues:
                        if issue["name"].lower() in issue_names:
            
                            if barcodes and asset_subject:
                                self.mongo_track.update_track_job_status(guid, "barcode", self.status.SKIPPED.value)
                            else:
                                entry = self.run_util.log_msg(self.run_util.prefix_id, f"Barcode 'issue' found in metadata for {guid} without sufficient data present in the metadata (barcode, mso, mos_id, preparation_type, asset_subject). has_new_specimen set to CRITICAL_ERROR and available_for_services to NO.", self.log_enum.CRITICAL_ERROR.value)
                                self.health_caller.error(self.run_util.service_name, entry, guid, self.flag_enum.HAS_NEW_SPECIMEN.value, self.status.CRITICAL_ERROR.value)
                                self.mongo_track.update_entry(guid, self.flag_enum.HAS_NEW_SPECIMEN.value, self.validate.CRITICAL_ERROR.value)
                                self.mongo_track.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate.NO.value)
                                safety_flag = False
            
                # remove safety lock - set available for services to YES, add to throttle count for assets in flight
                if safety_flag:
                    self.mongo_track.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate.YES.value)
                    self.mongo_throttle.add_one_to_count("assets_in_flight", "value")
            
            except Exception as e:
                print(f"Error processing asset {guid}. This asset has to be manually checked depending on where the failure happened the flags could be messed up and needs to be correctly set. Exception: {e}")
                entry = self.run_util.log_exc(self.run_util.prefix_id, f"Error processing asset {guid}. This asset has to be manually checked depending on where the failure happened the flags could be messed up and needs to be correctly set.", e, self.log_enum.CRITICAL_ERROR.value)
                self.health_caller.error(self.run_util.service_name, entry, guid)
            
        return True
