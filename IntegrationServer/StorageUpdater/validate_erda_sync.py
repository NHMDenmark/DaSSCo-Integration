import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import mongo_connection
from StorageApi import storage_client
from Enums import validate_enum, erda_status


"""
Responsible validating files have been synced with erda and updating track data accordingly.
"""

class SyncErda:

    def __init__(self):

        self.track_mongo = mongo_connection.MongoConnection("track")
        self.storage_api = storage_client.StorageClient()
        self.validate_enum = validate_enum.ValidateEnum
        self.erda_enum = erda_status.ErdaStatus
        self.run = True
        self.count = 2

        self.loop()

    def loop(self):

        while self.run:
            
            asset = self.track_mongo.get_entry("erda_sync", self.validate_enum.AWAIT.value)

            if asset is not None:
                guid = asset["_id"]
                
                asset_status = self.storage_api.get_asset_status(guid)
                
                if asset_status is self.erda_enum.COMPLETE.value:
                    self.track_mongo.update_entry(guid, "erda_sync", self.validate_enum.YES.value)

                if asset_status is self.erda_enum.ASSET_RECEIVED.value:
                    # TODO figure out if pointing to another asset is needed here
                    pass

                if asset_status is self.erda_enum.ERDA_ERROR.value:
                    # TODO figure out how to handle this situation further.
                    self.track_mongo.update_entry(guid, "erda_sync", self.validate_enum.NO.value)

                time.sleep(1)

            if asset is None:
                time.sleep(1)

            self.count -= 1

            if self.count == 0:
                self.run = False


if __name__ == '__main__':
    SyncErda()