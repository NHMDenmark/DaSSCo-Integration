import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from datetime import datetime
from MongoDB import mongo_connection
from StorageApi import api_metadata_model
from Enums import restricted_access_nt
from Enums import asset_status_nt
from pydantic import BaseModel, Field, Json

class StorageService():

    def __init__(self):
        self.util = utility.Utility()
        self.metadata_db = mongo_connection.MongoConnection("metadata")
        self.api_metadata = api_metadata_model.ApiMetadataModel()

    def get_metadata_creation_body(self, guid):
        
        self.api_metadata = api_metadata_model.ApiMetadataModel()

        entry = self.metadata_db.get_entry("_id", guid)

        if entry is None:
            return None

        self.api_metadata.asset_guid = guid
        self.api_metadata.asset_pid = entry["asset_pid"]
        self.api_metadata.asset_subject = entry["asset_subject"]
        self.api_metadata.audited = entry["audited"]
        self.api_metadata.camera_setting_control = entry["camera_setting_control"]
        self.api_metadata.collection = entry["collection"]

        if entry["complete_digitiser_list"] == []:
            self.api_metadata.complete_digitiser_list.append(entry["digitiser"])
        else:    
            self.api_metadata.complete_digitiser_list = entry["complete_digitiser_list"]
        
        self.api_metadata.date_asset_finalised = entry["date_asset_finalised"]
        self.api_metadata.date_asset_taken = self.convert_str_to_datetime(entry["date_asset_taken"])
        self.api_metadata.date_metadata_ingested = entry["date_metadata_ingested"]
        self.api_metadata.digitiser = entry["digitiser"]
        self.api_metadata.external_publisher = entry["external_publisher"]
        # ingestion/integration has file format as a single string entry
        self.api_metadata.file_formats.append(entry["file_format"].upper())
        self.api_metadata.funding = entry["funding"]
        self.api_metadata.institution = entry["institution"]
        self.api_metadata.issues = entry["issues"]
        self.api_metadata.legality = entry["legality"]
        self.api_metadata.make_public = entry["make_public"]
        self.api_metadata.metadata_source = entry["metadata_source"]
        self.api_metadata.metadata_version = entry["metadata_version"]
        self.api_metadata.mos_id = entry["mos_id"]
        self.api_metadata.multi_specimen = entry["multi_specimen"]
        self.api_metadata.parent_guid = entry["parent_guid"]     
        
        if isinstance(entry["payload_type"], list):
            for payload in entry["payload_type"]:
                if isinstance(payload, list):
                    self.api_metadata.payload_type = payload[0]
                else:
                    self.api_metadata.payload_type = payload
        else:        
            self.api_metadata.payload_type = entry["payload_type"]

        self.api_metadata.pipeline = entry["pipeline_name"]
        self.api_metadata.restricted_access = entry["restricted_access"]             
        self.api_metadata.status = entry["status"]
        self.api_metadata.tags = entry["tags"]
        self.api_metadata.workstation = entry["workstation_name"] 
        
        barcode = []
        for b in entry["barcode"]:
            barcode.append(b)

        if len(barcode) != 0:
            for b in barcode:
                # Create a new instance of Specimen
                new_specimen = api_metadata_model.Specimen()  
                new_specimen.barcode = b
                new_specimen.collection = self.api_metadata.collection
                new_specimen.institution = self.api_metadata.institution
                # TODO need to figure out this exactly, what can and what cant be lists
                new_specimen.preparation_type = entry["preparation_type"]
                if new_specimen.preparation_type == []:
                    new_specimen.preparation_type = ""
                    
                # TODO again issue with something potentially being a list
                new_specimen.specimen_pid = entry["specimen_pid"]
                if new_specimen.specimen_pid == []:
                        new_specimen.specimen_pid = ""

                self.api_metadata.specimens.append(new_specimen)
            
        # This field cannot be empty # TODO there are other fields that must have values in order to update/create assets in ARS - make some check for this
        if self.api_metadata.status == "" or self.api_metadata.status is None:
            self.api_metadata.status = asset_status_nt.AssetStatusNT.WORKING_COPY.value

        return self.api_metadata

    def get_metadata_json_format(self, guid):
        
        data = self.get_metadata_creation_body(guid)
        
        data = data.model_dump_json()

        return data
    
    def convert_str_to_datetime(self, timestring):

        if isinstance(timestring, str):
            try:
                date_object = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S%z")
                return date_object
            except Exception as e:
                print(f"converting to date object from string went wrong: {e}")
                return timestring
        else:
            return timestring