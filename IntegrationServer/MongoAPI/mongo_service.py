import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
import json
from MongoDB import mongo_connection
from Enums import validate_enum, status_enum, asset_status_nt

class MongoService():

    def __init__(self):
        self.track_mdbc = mongo_connection.MongoConnection("track")
        self.metadata_mdbc = mongo_connection.MongoConnection("metadata")
        self.batch_mdbc = mongo_connection.MongoConnection("batch")
        self.slurm_mdbc = mongo_connection.MongoConnection("slurm")
        self.availability_mdbc = mongo_connection.MongoConnection("availability")
        
        self.util = utility.Utility()
        
        self.validate_enum = validate_enum.ValidateEnum
        self.enum_status = status_enum.StatusEnum
        self.nt_status_enum = asset_status_nt.AssetStatusNT
    
    def create_new_asset_entries(self, metadata, link_list):    

        if len(link_list["file_links"]) < 1:
            http_status = 422
            msg = "MUST CONTAIN A FILE LINK"
            return http_status, msg
        
        # Handle empty parent guid
        if metadata["parent_guid"] == "":
            metadata["parent_guid"] = None
        
        # Handle empty status
        if metadata["status"] == "":
            metadata["status"] = self.nt_status_enum.WORKING_COPY.value

        # Must include these values 
        has_value = self.check_metadata_field(metadata, "asset_guid")
        has_value = self.check_metadata_field(metadata, "collection")
        has_value = self.check_metadata_field(metadata, "pipeline_name")
        has_value = self.check_metadata_field(metadata, "institution")
        has_value = self.check_metadata_field(metadata, "workstation_name")
        
        if has_value is False:
            http_status = 422
            msg = "MISSING METADATA FIELD VALUE"
            return http_status, msg

        guid = metadata["asset_guid"]
        pipeline = metadata["pipeline_name"]

        new_entry = self.metadata_mdbc.create_metadata_entry_from_api(guid, metadata)

        if new_entry is False:
            http_status = 422
            msg = "ASSET ALREADY EXISTS"
            return http_status, msg

        self.track_mdbc.create_track_entry(guid, pipeline)

        http_status = 200
        msg = "CREATED"

        # TODO persist file links in track entry i think

        return http_status, msg
    
    def check_metadata_field_contains_value(self, metadata, field_name):

        if metadata[field_name] == "" or metadata[field_name] == None:
            return False