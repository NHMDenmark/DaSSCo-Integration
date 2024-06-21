import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import track_repository, service_repository
from StorageApi import storage_client
from Enums.status_enum import Status
from Enums.flag_enum import Flag
from Enums.validate_enum import Validate
from Enums.erda_status import ErdaStatus
from HealthUtility import health_caller, run_utility
import utility

"""
Responsible validating files have been synced with erda and updating track data accordingly.
"""

class SyncErda(Status, Flag, ErdaStatus, Validate):

    def __init__(self):

        Status.__init__(self)
        Flag.__init__(self)
        ErdaStatus.__init__(self)
        Validate.__init__(self)

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        # service name for logging/info purposes
        self.service_name = "Validate erda sync ARS"

        self.track_mongo = track_repository.TrackRepository()
        self.service_mongo = service_repository.ServiceRepository()
        
        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()

        # set the config file value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.RUNNING)

        self.run_util = run_utility.RunUtility(self.service_name, self.log_filename, self.logger_name)

        entry = self.run_util.log_msg(f"{self.service_name} status changed at initialisation to {self.RUNNING}")
        self.health_caller.run_status_change(self.service_name, self.RUNNING, entry)

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
                                           storage_api.exc, self.run_util.ERROR)
            self.health_caller.warning(self.service_name, entry)
            self.service_mongo.update_entry(self.service_name, "run_status", self.STOPPED)
            
        return storage_api

    def loop(self):

        while self.run == self.RUNNING:

            # checks if service should keep running            
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.PAUSED:
                self.run = self.run_util.pause_loop()
            
            if self.run == self.STOPPED:
                continue           
            
            assets = self.track_mongo.get_entries_from_multiple_key_pairs([{self.ERDA_SYNC: self.AWAIT}])

            if len(assets) == 0:
                # no assets found that needed validation
                time.sleep(1)
                continue

            for asset in assets:
                guid = asset["_id"]
                
                asset_status = self.storage_api.get_asset_status(guid)
                
                if asset_status == self.COMPLETED:

                    self.track_mongo.update_entry(guid, self.ERDA_SYNC, self.YES)
                    
                    self.track_mongo.update_entry(guid, self.HAS_OPEN_SHARE, self.NO)

                    self.track_mongo.update_entry(guid, self.HAS_NEW_FILE, self.NO)

                    self.track_mongo.update_entry(guid, "proxy_path", "")

                    for file in asset["file_list"]:
                        self.track_mongo.update_track_file_list(guid, file["name"], self.ERDA_SYNC, self.YES)        

                    print(f"Validated erda sync for asset: {guid}")

                if asset_status == self.ASSET_RECEIVED:
                    # no action needed here since asset is basically queued to be synced and just waiting for that to happen
                    print(f"Waiting on erda sync for asset: {guid}")
                    pass    

                if asset_status == self.ERDA_ERROR:
                    # TODO figure out how to handle this situation further. maybe set a counter that at a certain number triggers a long delay and clears if there are no ERDA_ERRORs
                    # currently resetting sync status to "NO" attempts a new sync 
                    self.track_mongo.update_entry(guid, self.ERDA_SYNC, self.NO)

                if asset_status is False:
                    # TODO handle when something went wrong with api call
                    pass
                time.sleep(1)

            # total delay after one run
            time.sleep(1)

        # Outside main while loop
        self.track_mongo.close_connection()
        self.service_mongo.close_connection()

if __name__ == '__main__':
    SyncErda()