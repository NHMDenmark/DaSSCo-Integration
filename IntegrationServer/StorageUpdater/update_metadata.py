import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import track_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum
from HealthUtility import health_caller, run_utility
import utility

"""
Responsible updating metadata and changing the status of the update_metadata field in the track db.
Logs warnings and errors from this process, and directs them to the health service. 
"""

class UpdateMetadata():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        # service name for logging/info purposes
        self.service_name = "Update metadata ARS"

        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.track_mongo = track_repository.TrackRepository()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
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
            
            asset = self.track_mongo.get_entry("update_metadata", self.validate_enum.YES.value)

            if asset is not None:
                if asset["is_in_ars"] == self.validate_enum.YES.value:

                    # TODO handle if is in ars == NO

                    guid = asset["_id"]
                    
                    updated = self.storage_api.update_metadata(guid)

                    if updated is True:
                        self.track_mongo.update_entry(guid, "update_metadata", self.validate_enum.NO.value)
                
                # TODO handle false better than ignoring it

                    time.sleep(1)

            if asset is None:
                time.sleep(1)

            # checks if service should keep running - configurable in ConfigFiles/run_config.json            
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.validate_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()
        
        # Outside main while loop
        self.track_mongo.close_connection()


if __name__ == '__main__':
    UpdateMetadata()