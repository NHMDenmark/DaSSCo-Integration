import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import mongo_connection
from StorageApi import storage_client
from Enums import validate_enum
import utility

"""
Responsible for checking for assets that are ready for erda syncing after they have been transferred to HPC cluster.
"""

class SyncErda:

    def __init__(self):

        self.track_mongo = mongo_connection.MongoConnection("track")
        self.storage_api = storage_client.StorageClient()
        self.validate_enum = validate_enum.ValidateEnum
        self.util = utility.Utility()
        self.run = True
        self.count = 4

        self.loop()

    def loop(self):

        while self.run:
            
            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"has_new_file" : self.validate_enum.AWAIT.value, "erda_sync": self.validate_enum.NO.value}])

            if asset is not None:
                guid = asset["_id"]
                storage_api = storage_client.StorageClient()
                synced = storage_api.sync_erda(guid)
                
                if synced is True:
                    self.track_mongo.update_entry(guid, "erda_sync", self.validate_enum.AWAIT.value)
                    
                
                time.sleep(3)

            if asset is None:
                time.sleep(10)

            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            self.run = self.util.get_value(run_config_path, "run")
            if self.run == "False":
                self.run = False
                self.track_mongo.close_mdb()
            

            # self.count -= 1

            if self.count == 0:
                self.run = False
                self.track_mongo.close_mdb()

if __name__ == '__main__':
    SyncErda()
