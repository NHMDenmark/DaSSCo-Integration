import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
from MongoDB import track_repository, service_repository, metadata_repository, throttle_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum, flag_enum
from HealthUtility import health_caller, run_utility
import utility

"""
Sets asset to be synced with Specify.
Finds assets that have the specify_sync field in track db set to PREPARE.
Updates the metadata locally. 
Updates the ARS with the assets info.
Updates track to reflect the updates/changes. spcify_sync -> AWAIT.
"""

class SyncSpecify():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        # service name for logging/info purposes
        self.service_name = "Specify sync ARS"
        self.prefix_id = "SSA"
        self.throttle_config_path = f"{project_root}/ConfigFiles/throttle_config.json"
        self.auth_timestamp = None
        self.track_mongo = track_repository.TrackRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.metadata_mongo = metadata_repository.MetadataRepository()
        self.throttle_mongo = throttle_repository.ThrottleRepository()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.flag_enum = flag_enum.FlagEnum
        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()

        self.await_specify_sync_count = self.util.get_value(self.throttle_config_path, "await_specify_sync_count")

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name, self.pid)

        self.run_util.service_starting_updates()
        # special status change, logging and contact health api
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        # get currrent self.run value
        self.run = self.run_util.get_service_run_status()
        # update service_run value for run_util
        self.run_util.service_run = self.run

        # create the storage api
        self.storage_api = self.create_storage_api()
        
        try:
            self.loop()
        except Exception as e:
            print("service crashed", e)
            try:
                entry = self.run_util.log_exc(self.prefix_id, f"{self.service_name} crashed.", e)
                self.health_caller.unexpected_error(self.service_name, entry)
            except:
                print(f"failed to inform about crash")
            self.run_util.service_stopping_updates()
            self.close_db_connections()

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

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            # check if new keycloak auth is needed, creates the storage client
            self.authorization_check()
            if self.storage_api is None:
                continue

            # check throttle
            sync_count = self.throttle_mongo.get_value_for_key("await_specify_sync_count", "value")
            if sync_count >= self.await_specify_sync_count:
                # TODO implement better throttle than sleep
                time.sleep(30)
                self.end_of_loop_checks()
                continue

            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{self.flag_enum.HAS_OPEN_SHARE.value: self.validate_enum.YES.value, self.flag_enum.SPECIFY_SYNC.value: self.validate_enum.PREPARE.value, 
                                                                         self.flag_enum.AVAILABLE_FOR_SERVICES.value: self.validate_enum.YES.value}])

            if asset is not None:
                
                guid = asset["_id"]

                if asset["asset_type"] == "DEVICE_TARGET":
                    print(f"Asset {guid} is a device target, skipping specify sync.")
                    self.track_mongo.update_entry(guid, self.flag_enum.SPECIFY_SYNC.value, self.validate_enum.YES.value)
                    continue

                try:
                    self.metadata_mongo.update_entry(guid, "push_to_specify", True)
                    self.metadata_mongo.update_entry(guid, "asset_locked", True)
                    self.metadata_mongo.update_entry(guid, "specify_attachment_remarks", "Test case.")
                    self.metadata_mongo.update_entry(guid, "specify_attachment_title", guid)
                except Exception as e:
                    print(f"Failed to update metadata for asset {guid}: {e}")

                # update the ARS with the asset info
                try:
                    updated = self.storage_api.update_metadata(guid)

                    if updated is True:
                        print(f"{guid} was set to sync with Specify.")

                        self.track_mongo.update_entry(guid, "temporary_specify_sync_time", datetime.now())
                        self.throttle_mongo.add_one_to_count("await_specify_sync_count", "value")
                        self.track_mongo.update_entry(guid, self.flag_enum.SPECIFY_SYNC.value, self.validate_enum.AWAIT.value)
                    else:
                        print(f"{guid} failed to be initiate sync with Specify.")

                except Exception as e:
                    print(f"Failed for asset {guid}: {e}")
                time.sleep(10)
            if asset is None:
                time.sleep(10)

            self.end_of_loop_checks()
        
        # Outside main while loop
        self.run_util.service_stopping_updates()
        self.close_db_connections()
        print("service closed")

    def end_of_loop_checks(self):
        # checks if service should keep running          
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.validate_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()

    def close_db_connections(self):
        try:
            self.track_mongo.close_connection()
            self.metadata_mongo.close_connection()
            self.service_mongo.close_connection()
            self.throttle_mongo.close_connection()
        except Exception as e:
            print(f"Failed to close db connections: {e}")

    # check if new keycloak auth is needed, makes call to create the storage client
    def authorization_check(self):
        current_time = datetime.now()
        time_difference = current_time - self.auth_timestamp
            
        if time_difference > timedelta(minutes=4):
            self.storage_api.service.metadata_db.close_connection()
            print(f"creating new storage client, after {time_difference}")
            self.storage_api = self.create_storage_api()
        if self.storage_api.client is None:
            time.sleep(60)
            print("Waited 60 seconds before retrying to create the storage client after failing once")                
            self.storage_api = self.create_storage_api()

if __name__ == '__main__':
    SyncSpecify()