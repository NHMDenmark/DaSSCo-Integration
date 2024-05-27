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
            self.count -= 1

            if self.count == 0:
                self.run = False

            # checks if service should keep running - configurable in ConfigFiles/run_config.json
            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            all_run = self.util.get_value(run_config_path, "all_run")
            service_run = self.util.get_value(run_config_path, "validate_erda_sync_run")

            if all_run == "False" or service_run == "False":
                self.run = False
                self.track_mongo.close_mdb()
                self.metadata_mongo.close_mdb()
                continue

            assets = self.track_mongo.get_entries_from_multiple_key_pairs([{"erda_sync": self.validate_enum.AWAIT.value}])

            if len(assets) == 0:
                # no assets found that needed validation
                time.sleep(1)
                continue

            for asset in assets:
                guid = asset["_id"]
                
                asset_status = self.storage_api.get_asset_status(guid)
                
                if asset_status == self.erda_enum.COMPLETED.value:

                    self.track_mongo.update_entry(guid, "erda_sync", self.validate_enum.YES.value)
                    
                    self.track_mongo.update_entry(guid, "has_open_share", self.validate_enum.NO.value)

                    self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.NO.value)

                    self.track_mongo.update_entry(guid, "proxy_path", "")

                    for file in asset["file_list"]:
                        self.track_mongo.update_track_file_list(guid, file["name"], "erda_sync", self.validate_enum.YES.value)        

                    print(f"Validated erda sync for asset: {guid}")

                if asset_status == self.erda_enum.ASSET_RECEIVED.value:
                    # no action needed here since asset is basically queued to be synced and just waiting for that to happen
                    print(f"Waiting on erda sync for asset: {guid}")
                    pass    

                if asset_status == self.erda_enum.ERDA_ERROR.value:
                    # TODO figure out how to handle this situation further. maybe set a counter that at a certain number triggers a long delay and clears if there are no ERDA_ERRORs
                    # currently resetting sync status to "NO" attempts a new sync 
                    self.track_mongo.update_entry(guid, "erda_sync", self.validate_enum.NO.value)

                if asset_status is False:
                    # TODO handle when something went wrong with api call
                    pass
                time.sleep(1)

            # total delay after one run
            time.sleep(1)


if __name__ == '__main__':
    SyncErda()