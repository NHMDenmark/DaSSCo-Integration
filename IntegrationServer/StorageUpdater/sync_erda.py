import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import track_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum
from InformationModule.log_class import LogClass
from HealthUtility import health_caller
import utility
from datetime import datetime, timedelta

"""
Responsible syncing assets with erda after their files have been uploaded to their file shares in ARS.
Logs warnings and errors from this process, and directs them to the health service. 
"""

class SyncErda(LogClass):

    def __init__(self):

        # setting up logging
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.relpath(os.path.abspath(__file__), start=project_root))
        # service name for logging/info purposes
        self.service_name = "Erda sync ARS"

        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.track_mongo = track_repository.TrackRepository()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()

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

            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"has_new_file" : self.validate_enum.AWAIT.value, "erda_sync": self.validate_enum.NO.value}])

            if asset is not None:
                guid = asset["_id"]
                storage_api = storage_client.StorageClient()
                synced = storage_api.sync_erda(guid)
                
                # TODO handle if false - api fail
                if synced is True:
                    self.track_mongo.update_entry(guid, "erda_sync", self.validate_enum.AWAIT.value)
                    
                
                time.sleep(3)

            if asset is None:
                time.sleep(10)

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
        
        # Outside main while loop
        self.track_mongo.close_connection()


if __name__ == '__main__':
    SyncErda()
