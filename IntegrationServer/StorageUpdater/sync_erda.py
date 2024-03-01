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
Responsible for checking for assets that are ready for erda syncing after they have been transferred to HPC cluster.
"""

class SyncErda:

    def __init__(self):

        self.track_mongo = mongo_connection.MongoConnection("track")
        self.storage_api = storage_client.StorageClient()
        self.validate_enum = validate_enum.ValidateEnum
        self.run = True
        self.count = 2

        self.loop()

    def loop(self):

        while self.run:
            
            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"is_on_hpc" : self.validate_enum.YES.value, "erda_sync": self.validate_enum.NO.value}])

            if asset is not None:
                guid = asset["_id"]
                workstation = asset["batch_list_name"][:-11]
                pipeline = asset["pipeline"]
                self.storage_api.sync_erda(guid, pipeline, workstation)
                # TODO get status back from api and check its ok before update entry
                self.track_mongo.update_entry(guid, "erda_sync", self.validate_enum.AWAIT.value)
                
                time.sleep(1)

            if asset is None:
                time.sleep(1)

            self.count -= 1

            if self.count == 0:
                self.run = False


if __name__ == '__main__':
    SyncErda()
