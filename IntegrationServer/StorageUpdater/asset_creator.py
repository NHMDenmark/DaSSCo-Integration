import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import metadata_repository, track_repository, service_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum
from HealthUtility import health_caller, run_utility
import utility

"""
Responsible creating new metadata assets in ars. Updates track database with assets status.
Logs warnings and errors from this process, and directs them to the health service. 
"""

class AssetCreator():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        self.service_name = "Asset creator ARS"
        self.track_mongo = track_repository.TrackRepository()
        self.metadata_mongo = metadata_repository.MetadataRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.health_caller = health_caller.HealthCaller()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.util = utility.Utility()

        # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)

        self.run_util = run_utility.RunUtility(self.service_name, self.log_filename, self.logger_name)

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
            self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.STOPPED.value)
            
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
                        message = self.run_util.log_msg(response)

                    # TODO handle 300-399

                    if 400 <= status_code <= 499:
                        message = self.run_util.log_exc(response, exc, self.run_util.log_enum.ERROR.value)
                        self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.PAUSED.value)
                        self.health_caller.warning(self.service_name, message, guid, "is_in_ars")
                        time.sleep(1)
                    # TODO handle if status code is 555 - this means we set it during another exception - see storage_client.get_status_code_from_exc()
                    if 500 <= status_code:
                        message = self.run_util.log_exc(response, exc)
                        self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.PAUSED.value)
                        self.health_caller.warning(self.service_name, message)
                        time.sleep(1)
                    # self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.ERROR.value) this responsibility is moved to health module, sets TEMP_ERROR status here 

                time.sleep(1)

            if asset is None:
                time.sleep(1)

            # checks if service should keep running           
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.validate_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()

        # outside main while loop        
        self.track_mongo.close_connection()
        self.metadata_mongo.close_connection()
        self.service_mongo.close_connection()

if __name__ == '__main__':
    AssetCreator()