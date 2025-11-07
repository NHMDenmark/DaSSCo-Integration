import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
from MongoDB import track_repository, service_repository, throttle_repository, metadata_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum, flag_enum, erda_status, asset_status_nt
from HealthUtility import health_caller, run_utility
import utility

"""
Responsible validating assets have been synced with specify and updating track data accordingly.
Finds assets with the specify_sync field in track db set to AWAIT.
Queries the ARS for assets that have been set to sync with specify. 
When assets have been synced successfully updates track db to reflect this. specify_sync -> YES.
"""

class ValidateSpecifySync():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        # service name for logging/info purposes
        self.service_name = "Validate specify sync ARS"
        self.prefix_id = "VssA"
        self.auth_timestamp = None
        self.service_config_path = f"{project_root}/ConfigFiles/micro_service_config.json"
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.flag_enum = flag_enum.FlagEnum
        self.erda_enum = erda_status.ErdaStatusEnum
        self.asset_status_enum = asset_status_nt.AssetStatusNT
        self.track_mongo = track_repository.TrackRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.throttle_mongo = throttle_repository.ThrottleRepository()
        self.metadata_mongo = metadata_repository.MetadataRepository()
        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()

        self.max_sync_specify_attempt_wait_time = self.util.get_nested_value(self.service_config_path, self.service_name, "max_sync_specify_attempt_wait_time")

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
                entry = self.run_util.log_exc(self.prefix_id, f"{self.service_name} crashed.", e, self.status_enum.CRITICAL_ERROR.value)
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

            # checks if service should keep running
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.status_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()
            
            if self.run == self.status_enum.STOPPED.value:
                continue           
            
            assets = self.track_mongo.get_entries_from_multiple_key_pairs([{self.flag_enum.SPECIFY_SYNC.value: self.validate_enum.AWAIT.value,
                                                                             self.flag_enum.HAS_OPEN_SHARE.value: self.validate_enum.YES.value, self.flag_enum.AVAILABLE_FOR_SERVICES.value: self.validate_enum.YES.value}])

            if len(assets) == 0:
                # no assets found that needed validation
                time.sleep(20)
                continue
            
            # print(f"checking {len(assets)} assets:")
            for asset in assets:
                guid = asset["_id"]

                attempted, status_code, asset_status, asset_share_size, note = self.storage_api.get_asset_sharesize_and_status(guid)
                
                if attempted is False:
                    if status_code == 1000:
                        continue
                    # other cases
                    else:
                        # logs and sends a error message to the health api, subtracts from throttle count and moves on
                        entry = self.run_util.log_msg(self.prefix_id, f"Something unexpected happened while attempting to get the asset status from ARS for {guid}. Status code: {status_code}. Will set specify_sync to ERROR. {note}")
                        self.health_caller.error(self.service_name, entry, guid, self.flag_enum.SPECIFY_SYNC.value , self.status_enum.ERROR.value)
                        self.run_util.update_metadata_status(guid, self.asset_status_enum.PROCESSING_ISSUE.value)
                        continue

                if asset_share_size <= 0 or None:
                    # logs and sends a error message to the health api, subtracts from throttle count and moves on
                    entry = self.run_util.log_msg(self.prefix_id, f"Asset was attempting to sync with specify but had no file share in ARS. {guid}. Status code: {status_code}. Will set specify_sync to ERROR. {note}")
                    self.health_caller.error(self.service_name, entry, guid, self.flag_enum.SPECIFY_SYNC.value , self.status_enum.ERROR.value)
                    self.run_util.update_metadata_status(guid, self.asset_status_enum.PROCESSING_ISSUE.value)
                    self.update_throttle_count()
                    self.update_throttle_size(asset, guid)
                    continue

                # success scenario for an asset
                if asset_status == self.erda_enum.SPECIFY_SYNCHRONISED.value:
                    self.asset_validated(guid)

                # asset is still waiting to be synced
                if asset_status == self.erda_enum.SPECIFY_SYNC_SCHEDULED.value:
                    # check if asset is timed out and handle if true
                    timed_out = self.check_timeout(guid)

                    if timed_out is True:                            
                            self.timeout_handling(guid)
                    else:
                        # no action needed here since asset is queued to be synced and just waiting for that to happen
                        print(f"Waiting on specify sync for asset: {guid}")
                    
                if asset_status == self.erda_enum.SPECIFY_SYNC_FAILED.value:
                     
                    self.track_mongo.update_entry(guid, self.flag_enum.SPECIFY_SYNC.value, self.validate_enum.ERROR.value)

                    entry = self.run_util.log_msg(self.prefix_id, f"Asset failed to sync with specify in ARS. Status found in ARS: {asset_status}. {guid}. Will set specify_sync to ERROR. {note}")
                    self.health_caller.error(self.service_name, entry, guid, self.flag_enum.SPECIFY_SYNC.value , self.status_enum.ERROR.value)
                    self.run_util.update_metadata_status(guid, self.asset_status_enum.PROCESSING_ISSUE.value)
                    
                # wait time between calling ARS for asset status
                time.sleep(1)

            # total delay after one run
            time.sleep(10)

        # Outside main while loop
        self.run_util.service_stopping_updates()
        self.close_db_connections()
        print("service closed")
        
    def close_db_connections(self):
        try:
            self.track_mongo.close_connection()
            self.service_mongo.close_connection()
            self.throttle_mongo.close_connection()
        except Exception as e:
            print(f"Faied to close db connections: {e}")

    # success scenario
    def asset_validated(self, guid):

        # remove the temp sync timestamp 
        self.track_mongo.delete_field(guid, "temporary_specify_sync_time")
        # remove the temp time out status if it exist                    
        self.track_mongo.delete_field(guid, "temporary_time_out_sync_specify_attempt")    

        self.track_mongo.update_entry(guid, self.flag_enum.SPECIFY_SYNC.value, self.validate_enum.YES.value)
        self.update_throttle_count()        
        
        self.run_util.update_metadata_status(guid, self.asset_status_enum.PUBLISHED_TO_SPECIFY.value)
        
    def check_timeout(self, guid):

        time_received = self.track_mongo.get_value_for_key(guid, "temporary_specify_sync_time")

        time_allowed = datetime.now() - timedelta(seconds=self.max_sync_specify_attempt_wait_time)

        if time_received < time_allowed:

            return True
        
        return False

    def timeout_handling(self, guid):
            again = self.track_mongo.get_value_for_key(guid, "temporary_time_out_sync_specify_attempt")
            # TODO
            pass
        
    def update_throttle_size(self, asset, guid):

        self.throttle_mongo.subtract_from_amount("total_asset_size_mb", "value", asset["asset_size"])

        self.throttle_mongo.subtract_from_amount("total_reopened_size_mb", "value", asset["asset_size"])
        self.track_mongo.delete_field(guid, "temporary_reopened_share_status")     
    
    def update_throttle_count(self):
        self.throttle_mongo.subtract_one_from_count("await_specify_sync_count", "value")

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
    ValidateSpecifySync()