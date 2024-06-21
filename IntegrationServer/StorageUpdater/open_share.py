import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB import track_repository, metadata_repository, service_repository
from StorageApi import storage_client
from Enums import status_enum, validate_enum
from Enums.status_enum import Status
from Enums.validate_enum import Validate
import utility
import time
from HealthUtility import health_caller, run_utility
from StorageApi import storage_client

"""
TODO Description
"""

class OpenShare(Status, Validate):

    def __init__(self):
        Status.__init__(self)
        Validate.__init__(self)

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        # service name for logging/info purposes
        self.service_name = "Open file share ARS"
        
        self.mongo_track = track_repository.TrackRepository()
        self.mongo_metadata = metadata_repository.MetadataRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.util = utility.Utility()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        
        # set the config file value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)

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
                                           storage_api.exc, self.run_util.log_enum.ERROR.value)
            self.health_caller.warning(self.service_name, entry)
            self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.STOPPED.value)
            
        return storage_api

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": self.NO, "has_open_share": self.NO,
                                                                          "jobs_status": self.WAITING, "is_in_ars": self.YES,
                                                                            "has_new_file": self.NO, "erda_sync": self.YES}])
            if asset is None:
                time.sleep(1)        
            else: 
                 
                guid = asset["_id"]
                institution = self.mongo_metadata.get_value_for_key(guid, "institution")
                collection = self.mongo_metadata.get_value_for_key(guid, "collection")
                asset_size = self.mongo_track.get_value_for_key(guid, "asset_size")
                
                proxy_path = self.storage_api.open_share(guid, institution, collection, asset_size)
                
                if proxy_path is not False:

                    self.mongo_track.update_entry(guid, "proxy_path", proxy_path)
                    
                    # create links for all files in the asset
                    files = asset["file_list"]

                    for file in files:
                        if file["deleted"] is not True:
                            name = file["name"]
                            link = proxy_path + name
                            self.mongo_track.update_track_file_list(guid, name, "ars_link", link)

                    
                    self.mongo_track.update_entry(guid, "has_open_share", self.YES)

                # TODO handle if proxy path is false
            
            # checks if service should keep running          
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.PAUSED:
                self.run = self.run_util.pause_loop()

        # outside main while loop        
        self.mongo_track.close_connection()
        self.mongo_metadata.close_connection()
        self.service_mongo.close_connection()


if __name__ == '__main__':
    OpenShare()