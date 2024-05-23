import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import mongo_connection
from StorageApi import storage_client
from Enums import validate_enum, erda_status
import utility

"""
Responsible validating files have been synced with erda and updating track data accordingly.
"""

class ValidateErda:

    def __init__(self):

        self.track_mongo = mongo_connection.MongoConnection("track")
        self.storage_api = storage_client.StorageClient()
        self.validate_enum = validate_enum.ValidateEnum
        self.erda_enum = erda_status.ErdaStatus
        self.util = utility.Utility()
        self.run = True
        self.count = 4

        self.loop()

    def loop(self):

        while self.run:
            
            asset = self.track_mongo.get_entry("erda_sync", self.validate_enum.AWAIT.value)
            
            if asset is not None:
                guid = asset["_id"]
                print(guid)
                asset_status = self.storage_api.get_asset_status(guid)
                # This if statement is a hack to deal with api being broken- only use for testing!!!
                if asset_status is True:
                    asset_status = "COMPLETED"

                if asset_status == self.erda_enum.COMPLETED.value:

                    self.track_mongo.update_entry(guid, "erda_sync", self.validate_enum.YES.value)
                    
                    self.track_mongo.update_entry(guid, "has_open_share", self.validate_enum.NO.value)

                    self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.NO.value)

                    self.track_mongo.update_entry(guid, "proxy_path", "")

                    for file in asset["file_list"]:
                        self.track_mongo.update_track_file_list(guid, file["name"], "erda_sync", self.validate_enum.YES.value)        

                if asset_status == self.erda_enum.ASSET_RECEIVED.value:
                    time.sleep(10)
                    # TODO figure out if pointing to another asset is needed here
                    pass

                if asset_status == self.erda_enum.ERDA_ERROR.value:
                    # TODO figure out how to handle this situation further.
                    self.track_mongo.update_entry(guid, "erda_sync", self.validate_enum.NO.value)

                time.sleep(1)

            if asset is None:
                time.sleep(10)

            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            run = self.util.get_value(run_config_path, "run")
            if run == "False":
                self.run = False
                self.track_mongo.close_mdb()

            #self.count -= 1

            if self.count == 0:
                self.run = False
                self.track_mongo.close_mdb()

if __name__ == '__main__':
    ValidateErda()
