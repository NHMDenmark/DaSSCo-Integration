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
Responsible creating new metadata assets in ars.
"""

class AssetCreator:

    def __init__(self):

        self.track_mongo = mongo_connection.MongoConnection("track")
        self.metadata_mongo = mongo_connection.MongoConnection("metadata")
        self.storage_api = storage_client.StorageClient()
        self.validate_enum = validate_enum.ValidateEnum
        
        self.run = True
        self.count = 2

        self.loop()

    def loop(self):

        while self.run:
            
            asset = self.track_mongo.get_entry("is_in_ars", self.validate_enum.NO.value)

            if asset is not None:
                guid = asset["_id"]
                
                if asset["asset_size"] != -1:
                    created = self.storage_api.create_asset(guid, asset["asset_size"])
                else:
                    created = self.storage_api.create_asset(guid)


                if created is True:
                    self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.YES.value)
                    self.track_mongo.update_entry(guid, "has_open_share", self.validate_enum.YES.value)
                    if asset["asset_size"] != -1:
                        self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.YES.value)

            # TODO handle false better than ignoring it set AWAIT or some other status for is_in_ars maybe
                elif created is False:
                    self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.AWAIT.value)


                time.sleep(1)

            if asset is None:
                time.sleep(1)

            self.count -= 1

            if self.count == 0:
                self.run = False


if __name__ == '__main__':
    AssetCreator()