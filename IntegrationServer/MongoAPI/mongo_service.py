import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
import json
from MongoDB import mongo_connection
from Enums import validate_enum, status_enum

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
    
    def create_new_asset_entries(self, metadata, link_list):    

        if len(link_list["file_links"]) < 1:
            http_status = 422
            msg = "MUST CONTAIN A FILE LINK"
            return http_status, msg
        
        if metadata["parent_guid"] == "":
            metadata["parent_guid"] = None
        
        has_value = self.check_metadata_field(metadata, "asset_guid")
        has_value = self.check_metadata_field(metadata, "collection")
        has_value = self.check_metadata_field(metadata, "pipeline")
        has_value = self.check_metadata_field(metadata, "")
        has_value = self.check_metadata_field(metadata, "")
        has_value = self.check_metadata_field(metadata, "")

        if has_value is False:
            http_status = 422
            msg = "MISSING METADATA FIELD VALUE"
            return http_status, msg

        guid = metadata["asset_guid"]
        pipeline = metadata["pipeline"]


        http_status = 200
        msg = "CREATED"

        return http_status, msg
    
    def check_metadata_field_contains_value(self, metadata, field_name):

        if metadata[field_name] == "" or metadata[field_name] == None:
            return False