import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import track_repository, service_repository, throttle_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum
from InformationModule.log_class import LogClass
from HealthUtility import health_caller, run_utility
import utility
from datetime import datetime, timedelta

"""
Responsible for closing file shares once they hpc has downloaded files from it. 
Logs warnings and errors from this process, and directs them to the health service. 
"""

class CloseShare(LogClass):

    def __init__(self):
        
        # setting up logging
        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        # service name for logging/info purposes
        self.service_name = "Close file share ARS"
        self.prefix_id = "CfsA"
        #self.throttle_config_path = f"{project_root}/ConfigFiles/throttle_config.json"
        self.auth_timestamp = None
        self.track_mongo = track_repository.TrackRepository()
        self.health_caller = health_caller.HealthCaller()
        self.service_mongo = service_repository.ServiceRepository()
        self.throttle_mongo = throttle_repository.ThrottleRepository()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.util = utility.Utility()

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)

        # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
        # special status change, logging and contact health api
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        # get currrent self.run value
        self.run = self.run_util.get_service_run_status()
        # update service_run value for run_util
        self.run_util.service_run = self.run

        self.storage_api = self.create_storage_api()
        
        try:
            self.loop()
        except Exception as e:
            print("service crashed", e)
    
    def loop(self):
 
        while self.run == self.status_enum.RUNNING.value:
            
            # check if new keycloak auth is needed, creates the storage client
            self.authorization_check()
            if self.storage_api is None:
                continue

            time.sleep(1)
            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"has_new_file": self.validate_enum.NO.value, "erda_sync":self.validate_enum.YES.value, "hpc_ready":self.validate_enum.YES.value,
                                                                         "has_open_share":self.validate_enum.YES.value}])

            if asset is not None:
                guid = asset["_id"]
                #print(f"Found asset: {guid}")

                try:
                    closed = self.storage_api.close_share(guid)
                except Exception as e:
                    entry = self.log_exc(f"Failed to close file proxy share for guid {guid}.", e, self.log_enum.ERROR.value)
                    self.health_caller.warning(self.service_name, entry)
                    self.track_mongo.update_entry(guid, "has_open_share", self.validate_enum.ERROR.value)
                    closed = False

                if closed is True:
                    self.track_mongo.update_entry(guid, "has_open_share", self.validate_enum.NO.value)
                    self.update_throttle(asset)
                    print(f"closed share: {guid}")
            
            if asset is None:
                #print(f"failed to find assets")
                time.sleep(10)

            self.end_of_loop_checks()

        # outside main while loop        
        self.track_mongo.close_connection()
        self.service_mongo.close_connection()
        self.throttle_mongo.close_connection()
        self.run_util.service_mongo.close_connection()
        self.storage_api.service.metadata_db.close_mdb()
        print("service stopped")

    def end_of_loop_checks(self):
        # checks if service should keep running           
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.validate_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()

    def update_throttle(self, asset):
        self.throttle_mongo.subtract_from_amount("total_max_asset_size_mb", "value", asset["asset_size"])
        self.throttle_mongo.subtract_from_amount("total_reopened_share_size_mb", "value", asset["asset_size"])

        # TODO decide if this belongs here - its kind of natural to have the removal of the temp tag here though
        if "temporary_reopened_share_status" in asset:
            self.track_mongo.delete_field(asset["_id"], "temporary_reopened_share_status")
        else:
            entry = self.run_util.log_msg(self.prefix_id, f"Closed share of {asset["_id"]} without a temporary_reopened_share_status flag.", self.run_util.log_enum.WARNING.value)
            self.health_caller.warning(self.service_name, entry, asset["_id"])


    # check if new keycloak auth is needed, makes call to create the storage client
    def authorization_check(self):
        current_time = datetime.now()
        time_difference = current_time - self.auth_timestamp
            
        if time_difference > timedelta(minutes=4):
            self.storage_api.service.metadata_db.close_mdb()
            print(f"creating new storage client, after {time_difference}")
            self.storage_api = self.create_storage_api()
        if self.storage_api.client is None:
            time.sleep(60)
            print("Waited 60 seconds before retrying to create the storage client after failing once")                
            self.storage_api = self.create_storage_api()

    """
    Creates the storage client.
    If this fails it sets the service run config to STOPPED and notifies the health service.  
    Returns the storage client or None.
    """
    def create_storage_api(self):
    
        storage_api = storage_client.StorageClient()
        
        self.auth_timestamp = datetime.now()

        # handle initial fails
        if storage_api.client is None and self.run != self.status_enum.STOPPED.value:
            # log the failure to create the storage api
            entry = self.run_util.log_exc(self.prefix_id, f"Failed to create storage client for {self.service_name}. Received status: {storage_api.status_code}. {self.service_name} will retry in 1 minute. {storage_api.note}",
                                           storage_api.exc, self.run_util.log_enum.ERROR.value)
            self.health_caller.error(self.service_name, entry)

            # change run value in db 
            self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.STOPPED.value)
            
            # log the status change + health call 
            self.run_util.log_status_change(self.service_name, self.run, self.status_enum.STOPPED.value)

            # update run values
            self.run = self.run_util.get_service_run_status()
            self.run_util.service_run = self.run

            return storage_api           
        
        # handle retry success
        if storage_api.client is not None and self.run == self.status_enum.STOPPED.value:            
            
            entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} created storage client after retrying.")
            self.health_caller.warning(self.service_name, entry)

            # change run value in db 
            self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
            
            # log the status change + health call
            self.run_util.log_status_change(self.service_name, self.run, self.status_enum.RUNNING.value)

            # update run values
            self.run = self.run_util.get_service_run_status()
            self.run_util.service_run = self.run

            return storage_api

        # handles retry fail
        if storage_api.client is None and self.run == self.status_enum.STOPPED.value:
            entry = self.run_util.log_exc(self.prefix_id, f"Retry failed to create storage client for {self.service_name}. Received status: {storage_api.status_code}. {self.service_name} will shut down and need to be restarted manually. {storage_api.note}",
                                           storage_api.exc, self.run_util.log_enum.ERROR.value)
            self.health_caller.error(self.service_name, entry)
            return storage_api
        
        return storage_api

if __name__ == '__main__':
    CloseShare()