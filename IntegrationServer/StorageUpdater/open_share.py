import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB import track_repository, metadata_repository
from StorageApi import storage_client
from Enums import status_enum, validate_enum
import utility
import time
from HealthUtility import health_caller
from InformationModule.log_class import LogClass
from StorageApi import storage_client
from datetime import datetime, timedelta

"""
TODO Description
"""

class OpenShare(LogClass):

    def __init__(self):

        # setting up logging
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.relpath(os.path.abspath(__file__), start=project_root))
        # service name for logging/info purposes
        self.service_name = "Open file share ARS"

        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.mongo_track = track_repository.TrackRepository()
        self.mongo_metadata = metadata_repository.MetadataRepository()
        self.util = utility.Utility()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        

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

            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.NO.value, "has_open_share": validate_enum.ValidateEnum.NO.value,
                                                                          "jobs_status": status_enum.StatusEnum.WAITING.value, "is_in_ars": validate_enum.ValidateEnum.YES.value,
                                                                            "has_new_file": validate_enum.ValidateEnum.NO.value, "erda_sync": validate_enum.ValidateEnum.YES.value}])
            if asset is None:
                time.sleep(10)        
            else: 
                time.sleep(1)     
                guid = asset["_id"]
                institution = self.mongo_metadata.get_value_for_key(guid, "institution")
                collection = self.mongo_metadata.get_value_for_key(guid, "collection")
                asset_size = self.mongo_track.get_value_for_key(guid, "asset_size")
                print(f"Attempt open share for: {guid}")
                proxy_path = self.storage_api.open_share(guid, institution, collection, asset_size)
                print(proxy_path)
                if proxy_path is not False:

                    self.mongo_track.update_entry(guid, "proxy_path", proxy_path)
                    
                    # create links for all files in the asset
                    files = asset["file_list"]

                    for file in files:
                        if file["deleted"] is not True:
                            name = file["name"]
                            link = proxy_path + name
                            self.mongo_track.update_track_file_list(guid, name, "ars_link", link)

                    
                    self.mongo_track.update_entry(guid, "has_open_share", validate_enum.ValidateEnum.YES.value)

                # TODO handle if proxy path is false
            
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

        # outside main while loop        
        self.mongo_track.close_connection()
        self.mongo_metadata.close_connection()


if __name__ == '__main__':
    OpenShare()