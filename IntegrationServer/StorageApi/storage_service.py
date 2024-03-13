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

# untested
class StorageService():

    def __init__(self):
        self.util = utility.Utility()
        self.metadata_db = mongo_connection.MongoConnection("metadata")
        self.api_metadata = api_metadata_model.ApiMetadataModel()

    def get_metadata_creation_body(self, guid):
        
        self.api_metadata = api_metadata_model.ApiMetadataModel()
        specimen = api_metadata_model.Specimen

        entry = self.metadata_db.get_entry("_id", guid)

        self.api_metadata.asset_guid = guid
        self.api_metadata.asset_pid = entry["asset_pid"]
        self.api_metadata.parent_guid = entry["parent_guid"]
        self.api_metadata.status = entry["status"]
        self.api_metadata.multi_specimen = entry["multispecimen"]
        self.api_metadata.funding = entry["funding"]
        self.api_metadata.subject = entry["asset_subject"]
        for p in entry["payload_type"]:
            self.api_metadata.payload_type.append(p) 
        self.api_metadata.file_formats = entry["file_format"] # needs to ensure list on both sides
        self.api_metadata.restricted_access = entry["restricted_access"] # needs to ensure agreed upon data here
        self.api_metadata.audited = entry["audited"]
        self.api_metadata.date_asset_taken = self.convert_str_to_datetime(entry["date_asset_taken"])
        self.api_metadata.pipeline = entry["pipeline_name"]
        self.api_metadata.workstation = entry["workstation_name"]
        self.api_metadata.digitizer = entry["digitiser"]
        for t in entry["tags"]:
            self.api_metadata.tags.append({"key": t["key"], "value": t["value"]})

        self.api_metadata.institution = entry["institution"]
        self.api_metadata.collection = entry["collection"]
        barcode = []
        for b in entry["barcode"]:
            barcode.append(b)

        if len(barcode) != 0:
            for b in barcode:
                specimen.barcode = barcode
                specimen.collection = self.api_metadata.collection
                specimen.institution = self.api_metadata.institution
                specimen.preparation_type = entry["preparation_type"]
                specimen.specimen_pid = entry["speciment_pid"]

                self.api_metadata.specimens.append(self.specimen)
        
        if self.api_metadata.restricted_access is []:
            self.api_metadata.restricted_access.append(restricted_access_nt.RestrictedAccessNT.USER.value)

        if self.api_metadata.status == "":
            self.api_metadata.status = asset_status_nt.AssetStatusNT.WORKING_COPY.value

        return self.api_metadata

    def get_metadata_json_format(self, guid):
        
        self.get_metadata_creation_body(guid)
        
        data = self.api_metadata.model_dump_json() 
        return data
    
    def convert_str_to_datetime(self, timestring):

        if isinstance(timestring, str):
            date_object = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S%z")
            return date_object
        else:
            return timestring