import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
import utility
from MongoDB import service_repository, track_repository, metadata_repository, mos_repository, health_repository, throttle_repository
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum, flag_enum, erda_status
from StorageApi import storage_client

"""
# TODO Description
"""
class AssetErrorStatusHandler():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        # service name for logging/info purposes
        self.service_name = "Asset error status handler"
        self.prefix_id= "Aesh"


        self.util = utility.Utility()
        self.auth_timestamp = None
        self.service_mongo = service_repository.ServiceRepository()
        self.track_mongo = track_repository.TrackRepository()
        self.metadata_mongo = metadata_repository.MetadataRepository()
        self.mos_mongo = mos_repository.MOSRepository()
        self.health_mongo = health_repository.HealthRepository()
        self.health_caller = health_caller.HealthCaller()
        self.throttle_mongo = throttle_repository.ThrottleRepository()
        self.status_enum = status_enum.StatusEnum
        self.flag_enum = flag_enum.FlagEnum
        self.erda_enum = erda_status.ErdaStatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)

        # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
        
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        # create the storage api
        self.storage_api = self.create_storage_api()

        self.run = self.run_util.get_service_run_status()
        self.loop()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            self.authorization_check()
            if self.storage_api is None:
                continue

            assets = self.track_mongo.get_error_entries()

            if assets is None:
                time.sleep(600)
            else:
                errors_found = 0
                for asset in assets:
                    errors_found += 1
                    guid = asset["_id"]
                    
                    # erda_sync error
                    if asset[self.flag_enum.ERDA_SYNC.value] == self.status_enum.ERROR.value:
                        self.handle_erda_sync_error(asset, guid)

                print(f"Assets with errors found: {errors_found}")
                time.sleep(600)

            #checks if service should keep running           
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.status_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()
        
        # out of main loop
        self.close_connections()
        print("Service shut down")

    def close_connections(self):
        try:
            self.service_mongo.close_connection()
            self.track_mongo.close_connection()
            self.metadata_mongo.check_connection()
            self.mos_mongo.close_connection()
            self.health_mongo.close_connection()
            self.throttle_mongo.close_connection()
        except Exception as e:
            print(e)

    """
    Creates the storage client.
    If this fails it sets the service run config to STOPPED and notifies the health service.  
    Returns the storage client or None. 
    """
    def create_storage_api(self):
    
        storage_api = storage_client.StorageClient()
        
        self.auth_timestamp = datetime.now()

        if storage_api.client is None:
            # log the failure to create the storage api
            entry = self.run_util.log_exc(self.prefix_id, f"Failed to create storage client. {self.service_name} failed to run. Received status: {storage_api.status_code}. {self.service_name} needs to be manually restarted. {storage_api.note}",
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

    def handle_erda_sync_error(self, asset, guid):
        
        self.authorization_check()

        ars_status = self.storage_api.get_full_asset_status(guid)

        # gives time for ARS to update - in case this is about the share still appearing open despite sync completed
        time.sleep(120)

        if ars_status["data"].status == self.erda_enum.COMPLETED.value and ars_status["data"].share_allocation_mb is None:
            
            self.throttle_mongo.add_one_to_count("await_sync_asset_count", "value")
            self.track_mongo.update_entry(guid, self.flag_enum.ERDA_SYNC.value, self.validate_enum.AWAIT.value)
            print(f"found {guid} to have been successfully synced to erda - sent asset back to normal flow")

        else:
            print(f"unable to handle {guid} - set to critical error")
            message = self.run_util.log_msg(self.prefix_id, f"Tried handling erda_sync error for {guid}. Could not determine the issue. Will need manual handling. erda_sync set to {self.status_enum.CRITICAL_ERROR.value}")
            self.health_caller.error(self.service_name, message, guid, "erda_sync", self.status_enum.CRITICAL_ERROR.value)


if __name__ == '__main__':
    AssetErrorStatusHandler()