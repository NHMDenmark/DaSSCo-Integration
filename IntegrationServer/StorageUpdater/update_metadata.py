import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import mongo_connection
from StorageApi import storage_client
from Enums import validate_enum


"""
Responsible updating metadata and changing the status of the update_metadata field in the track db.
"""

class UpdateMetadata:

    def __init__(self):

        self.track_mongo = mongo_connection.MongoConnection("track")
        self.storage_api = storage_client.StorageClient()
        self.validate_enum = validate_enum.ValidateEnum
        
        self.run = True
        self.count = 2

        self.loop()

    def loop(self):

        while self.run:
            
            asset = self.track_mongo.get_entry("update_metadata", self.validate_enum.YES.value)

            if asset is not None:
                if asset["is_in_ars"] == self.validate_enum.YES.value:

                    # TODO handle if is in ars == NO

                    guid = asset["_id"]
                    
                    updated = self.storage_api.update_metadata(guid)

                    if updated is True:
                        self.track_mongo.update_entry(guid, "update_metadata", self.validate_enum.NO.value)
                
                # TODO handle false better than ignoring it

                    time.sleep(1)

            if asset is None:
                time.sleep(1)

            # checks if service should keep running - configurable in ConfigFiles/run_config.json
            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            all_run = self.util.get_value(run_config_path, "all_run")
            service_run = self.util.get_value(run_config_path, "update_metadata_run")

            if all_run == "False" or service_run == "False":
                self.run = False
                self.track_mongo.close_mdb()
                self.metadata_mongo.close_mdb()

            self.count -= 1

            if self.count == 0:
                self.run = False
                self.track_mongo.close_mdb()
                self.metadata_mongo.close_mdb()


if __name__ == '__main__':
    UpdateMetadata()