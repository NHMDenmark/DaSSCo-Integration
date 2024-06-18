import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import track_repository
from StorageApi import storage_client
from Enums import validate_enum, erda_status, status_enum, flag_enum
from HealthUtility import health_caller, run_utility
import utility

"""
Responsible validating files have been synced with erda and updating track data accordingly.
"""

class SyncErda():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        # service name for logging/info purposes
        self.service_name = "Validate erda sync ARS"

        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.track_mongo = track_repository.TrackRepository()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.erda_enum = erda_status.ErdaStatusEnum
        self.flag_enum = flag_enum.FlagEnum
        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()

        # set the config file value to RUNNING, mostly for ease of testing
        self.util.update_json(self.run_config_path, self.service_name, self.status_enum.RUNNING.value)

        self.run_util = run_utility.RunUtility(self.service_name, self.run_config_path, self.log_filename, self.logger_name)

        entry = self.run_util.log_msg(f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.storage_api = self.create_storage_api()
        
        self.run = self.run_util.get_service_run_status()
        self.run_util.service_run = self.run
        
        self.loop()

    """
    Creates the storage client.
    If this fails it sets the service run config to STOPPED and notifies the health service.  
    Returns the storage client or None. 
    """
    def create_storage_api(self):

        storage_api = storage_client.StorageClient()
         
        if storage_api.client is None:
            entry = self.run_util.log_exc(f"Failed to create storage client. {self.service_name} failed to run. Received status: {storage_api.status_code}. {self.service_name} needs to be manually restarted. {storage_api.note}",
                                           storage_api.exc, self.run_util.log_enum.ERROR.value)
            self.health_caller.warning(self.service_name, entry)
            self.run = self.util.update_json(self.run_config_path, self.service_name, self.status_enum.STOPPED.value)
            
        return storage_api

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:

            # checks if service should keep running - configurable in ConfigFiles/run_config.json            
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.validate_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()
            
            if self.run == self.status_enum.STOPPED.value:
                continue           
            
            assets = self.track_mongo.get_entries_from_multiple_key_pairs([{self.flag_enum.ERDA_SYNC.value: self.validate_enum.AWAIT.value}])

            if len(assets) == 0:
                # no assets found that needed validation
                time.sleep(1)
                continue

            for asset in assets:
                guid = asset["_id"]
                
                asset_status = self.storage_api.get_asset_status(guid)
                
                if asset_status == self.erda_enum.COMPLETED.value:

                    self.track_mongo.update_entry(guid, self.flag_enum.ERDA_SYNC.value, self.validate_enum.YES.value)
                    
                    self.track_mongo.update_entry(guid, self.flag_enum.HAS_OPEN_SHARE.value, self.validate_enum.NO.value)

                    self.track_mongo.update_entry(guid, self.flag_enum.HAS_NEW_FILE.value, self.validate_enum.NO.value)

                    self.track_mongo.update_entry(guid, "proxy_path", "")

                    for file in asset["file_list"]:
                        self.track_mongo.update_track_file_list(guid, file["name"], self.flag_enum.ERDA_SYNC.value, self.validate_enum.YES.value)        

                    print(f"Validated erda sync for asset: {guid}")

                if asset_status == self.erda_enum.ASSET_RECEIVED.value:
                    # no action needed here since asset is basically queued to be synced and just waiting for that to happen
                    print(f"Waiting on erda sync for asset: {guid}")
                    pass    

                if asset_status == self.erda_enum.ERDA_ERROR.value:
                    # TODO figure out how to handle this situation further. maybe set a counter that at a certain number triggers a long delay and clears if there are no ERDA_ERRORs
                    # currently resetting sync status to "NO" attempts a new sync 
                    self.track_mongo.update_entry(guid, self.flag_enum.ERDA_SYNC.value, self.validate_enum.NO.value)

                if asset_status is False:
                    # TODO handle when something went wrong with api call
                    pass
                time.sleep(1)

            # total delay after one run
            time.sleep(1)

        # Outside main while loop
        self.track_mongo.close_connection()

if __name__ == '__main__':
    SyncErda()