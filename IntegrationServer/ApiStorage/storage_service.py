import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from MongoDB import mongo_connection
from ApiStorage import api_metadata_model
from Enums import restricted_access_nt


# untested
class StorageService():

    def __init__(self):
        self.util = utility.Utility()
        self.metadata_db = mongo_connection.MongoConnection("metadata")
        

    def get_metadata_creation_body(self, guid):
        
        specimen = api_metadata_model.Specimen
        api_metadata = api_metadata_model.ApiMetadataModel

        entry = self.metadata_db.get_entry("_id", guid)

        api_metadata.asset_guid = guid
        api_metadata.asset_pid = entry["asset_pid"]
        api_metadata.parent_guid = entry["parent_guid"]
        api_metadata.status = entry["status"]
        api_metadata.multi_specimen = entry["multispecimen"]
        api_metadata.funding = entry["funding"]
        api_metadata.subject = entry["asset_subject"]
        api_metadata.payload_type = entry["payload_type"]
        api_metadata.file_formats = entry["file_format"] # needs to ensure list on both sides
        api_metadata.asset_locked = entry["asset_locked"]
        api_metadata.restricted_access = entry["restricted_access"] # needs to ensure agreed upon data here
        api_metadata.audited = entry["audited"]
        api_metadata.date_asset_taken = entry["date_asset_taken"]
        api_metadata.pipeline = entry["pipeline"]
        api_metadata.workstation = entry["workstation_name"]
        api_metadata.digitizer = entry["digitiser"]
        api_metadata.tags = entry["tags"]


        api_metadata.institution = entry["institution"]
        api_metadata.collection = entry["collection"]
        barcode = entry["barcode"]

        if barcode is not "":
            specimen.barcode = barcode
            specimen.collection = api_metadata.collection
            specimen.institution = api_metadata.institution
            specimen.preparation_type = entry["preparation_type"]
            specimen.specimen_pid = entry["speciment_pid"]

            api_metadata.specimens.append(self.specimen)
        
        if api_metadata.restricted_access is []:
            api_metadata.restricted_access.append(restricted_access_nt.RestrictedAccessNT.USER.value)

        return api_metadata

    def get_metadata_json_format(self, guid):

        data = self.get_metadata_creation_body(guid)

        return data.model_dump_json()
