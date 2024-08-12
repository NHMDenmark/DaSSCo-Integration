import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import track_repository
from StorageApi import storage_client
from Enums import validate_enum, erda_status, status_enum
from HealthUtility import health_caller
from InformationModule.log_class import LogClass
import utility
from datetime import datetime, timedelta

"""
Responsible validating files have been synced with erda and updating track data accordingly.
"""

class ValidateErda(LogClass):

    def __init__(self):

        # setting up logging
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.relpath(os.path.abspath(__file__), start=project_root))
        # service name for logging/info purposes
        self.service_name = "Validate erda sync ARS"

        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.track_mongo = track_repository.TrackRepository()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.erda_enum = erda_status.ErdaStatus
        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()

        self.auth_timestamp = None

        # set the config file value to RUNNING, mostly for ease of testing
        self.util.update_json(self.run_config_path, self.service_name, self.status_enum.RUNNING.value)
        
        self.storage_api = self.create_storage_api()
        
        self.run = self.util.get_value(self.run_config_path, self.service_name)        

        self.loop()

    """
    Creates the storage client.
    If this fails it sets the service run config to STOPPED and notifies the health service.  
    Returns the storage client or None. 
    """
    def create_storage_api(self):

        storage_api = storage_client.StorageClient()
        
        self.auth_timestamp = datetime.now()

        if storage_api.client is None:
            entry = self.log_exc(f"Failed to create storage client. {self.service_name} failed to run. Received status: {storage_api.status_code}. {self.service_name} needs to be manually restarted. {storage_api.note}", storage_api.exc, self.log_enum.ERROR.value)
            
            self.health_caller.warning(self.service_name, entry)
            self.run = self.util.update_json(self.run_config_path, self.service_name, self.status_enum.STOPPED.value)
            
        return storage_api

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            current_time = datetime.now()
            time_difference = current_time - self.auth_timestamp
            
            if time_difference > timedelta(minutes=4):
                print(f"creating new storage client, after {time_difference}")
                self.storage_api = self.create_storage_api()
            if self.storage_api is None:
                continue

            # checks if service should keep running - configurable in ConfigFiles/run_config.json
            all_run = self.util.get_value(self.run_config_path, "all_run")
            service_run = self.util.get_value(self.run_config_path, self.service_name)

            # Pause loop
            counter = 0
            while service_run == self.status_enum.PAUSED.value:
                sleep = 10
                counter += 1
                time.sleep(sleep)
                wait_time = sleep * counter
                entry = self.log_msg(f"{self.service_name} has been in pause mode for ~{wait_time} seconds")
                self.health_caller.warning(self.service_name, entry)
                service_run = self.util.get_value(self.run_config_path, self.service_name)
                
                all_run = self.util.get_value(self.run_config_path, "all_run")
                if all_run == self.status_enum.STOPPED.value:
                    service_run = self.status_enum.STOPPED.value
                
                if service_run != self.status_enum.PAUSED.value:
                    entry = self.log_msg(f"{self.service_name} has changed run status from {self.status_enum.PAUSED.value} to {service_run}")                   
                    self.health_caller.warning(self.service_name, entry)

            if all_run == self.status_enum.STOPPED.value or service_run == self.status_enum.STOPPED.value:
                self.run = self.status_enum.STOPPED.value
                continue           

            assets = self.track_mongo.get_entries_from_multiple_key_pairs([{"erda_sync": self.validate_enum.AWAIT.value}])

            if len(assets) == 0:
                # no assets found that needed validation
                time.sleep(1)
                continue

            for asset in assets:
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

        # Outside main while loop
        self.track_mongo.close_connection()

if __name__ == '__main__':
    ValidateErda()
