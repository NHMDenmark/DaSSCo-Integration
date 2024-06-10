import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import metadata_repository, track_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum
from InformationModule.log_class import LogClass
from HealthUtility import health_caller
import utility


"""
Responsible creating new metadata assets in ars. Updates track database with assets status.
Logs warnings and errors from this process, and directs them to the health service. 
"""

class AssetCreator(LogClass):

    def __init__(self):

        # setting up logging
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.relpath(os.path.abspath(__file__), start=project_root))
        # service name for logging/info purposes
        self.service_name = "Asset creator ARS"
        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.track_mongo = track_repository.TrackRepository()
        self.metadata_mongo = metadata_repository.MetadataRepository()
        self.health_caller = health_caller.HealthCaller()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.util = utility.Utility()

        # set the config file value to RUNNING, mostly for ease of testing
        self.util.update_json(self.run_config_path, self.service_name, self.status_enum.RUNNING.value)
        entry = self.log_msg(f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

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
            entry = self.log_exc(f"Failed to create storage client. {self.service_name} failed to run. Received status: {storage_api.status_code}. {self.service_name} needs to be manually restarted.", storage_api.exc, self.log_enum.ERROR.value)
            self.health_caller.warning(self.service_name, entry)
            self.run = self.util.update_json(self.run_config_path, self.service_name, self.status_enum.STOPPED.value)
            
        return storage_api

    def loop(self):
 
        while self.run == self.status_enum.RUNNING.value:
            
            asset = self.track_mongo.get_entry("is_in_ars", self.validate_enum.NO.value)

            if asset is not None:
                guid = asset["_id"]
                
                # Receives created: bool, response: str, exc: exception, status_code: int
                if asset["asset_size"] != -1:
                    created, response, exc, status_code = self.storage_api.create_asset(guid, asset["asset_size"])
                else:
                    created, response, exc, status_code = self.storage_api.create_asset(guid)


                if created is True:
                    metadata = self.metadata_mongo.get_entry("_id", guid)
                    self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.YES.value)
                    self.track_mongo.update_entry(guid, "has_open_share", self.validate_enum.YES.value)
                    if asset["asset_size"] != -1 and metadata["parent_guid"] == "":
                        self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.YES.value)

                if created is False:
                    if status_code <= 299:                    
                        message = self.log_msg(response)

                    # TODO handle 300-399

                    if 400 <= status_code <= 499:
                        message = self.log_exc(response, exc, self.log_enum.ERROR.value)
                        self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.PAUSED.value)
                        self.health_caller.warning(self.service_name, message, guid, "is_in_ars")
                        time.sleep(1)
                    if 500 <= status_code:
                        message = self.log_exc(response, exc)
                        self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.PAUSED.value)
                        self.health_caller.warning(self.service_name, message)
                        time.sleep(1)
                    # self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.ERROR.value) this responsibility is moved to health module, sets TEMP_ERROR status here 

                time.sleep(1)

            if asset is None:
                time.sleep(1)

            # checks if service should keep running - configurable in ConfigFiles/run_config.json            
            all_run = self.util.get_value(self.run_config_path, "all_run")
            service_run = self.util.get_value(self.run_config_path, self.service_name)

            if all_run != self.run:
                entry = self.log_msg(f"All run status changed from {self.run} to {all_run}")
                self.health_caller.run_status_change(self.service_name, self.run, entry)

            if service_run != self.run:
                entry = self.log_msg(f"{self.service_name} status changed from {self.run} to {service_run}")
                self.health_caller.run_status_change(self.service_name, self.run, entry)

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
        self.track_mongo.close_connection()
        self.metadata_mongo.close_connection()

if __name__ == '__main__':
    AssetCreator()