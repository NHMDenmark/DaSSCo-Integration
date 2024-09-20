import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
from MongoDB import track_repository, service_repository, throttle_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum, flag_enum, erda_status
from HealthUtility import health_caller, run_utility
import utility

"""
Responsible syncing assets with erda after their files have been uploaded to their file shares in ARS.
Logs warnings and errors from this process, and directs them to the health service. 
"""

class SyncErda():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        # service name for logging/info purposes
        self.service_name = "Erda sync ARS"
        self.prefix_id = "EsA"
        self.throttle_config_path = f"{project_root}/ConfigFiles/throttle_config.json"
        self.auth_timestamp = None
        self.track_mongo = track_repository.TrackRepository()
        self.throttle_mongo = throttle_repository.ThrottleRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.flag_enum = flag_enum.FlagEnum
        self.erda_status_enum = erda_status.ErdaStatusEnum
        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()

        self.max_sync_asset_count = self.util.get_value(self.throttle_config_path, "max_sync_asset_count")


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

        # create the storage api
        self.storage_api = self.create_storage_api()
        
        self.loop()

    """
    Creates the storage client.
    If this fails it sets the service run config to STOPPED and notifies the health service.  
    Returns the storage client or None. 
    """
    def create_storage_api(self):
    
        storage_api = storage_client.StorageClient()
        
        self.auth_timestamp = datetime.now()

        if storage_api.client is None:
            
            # TODO experimental ignoring status 504 and 502, and retry after 5 min
            if storage_api.status_code == 504 or storage_api.status_code == 502:
                entry = self.run_util.log_msg(self.prefix_id, f"Failed to create storage client for {self.service_name}, it will wait 5 min and retry. Received status: {storage_api.status_code}. {storage_api.note}",
                                          self.run_util.log_enum.WARNING.value)
                self.health_caller.warning(self.service_name, entry)
                time.sleep(300)
                return storage_api

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

    # TODO handle this further when api is available again
    # handle if the sync happened after the time out but before the resync
    def test_asset_timeout_and_synced(self, guid, asset):
        
        asset_status = self.storage_api.get_asset_status(guid)
                
        if asset_status == self.erda_status_enum.COMPLETED.value :

            self.track_mongo.update_entry(guid, self.flag_enum.ERDA_SYNC.value, self.validate_enum.YES.value)
                    
            self.track_mongo.update_entry(guid, self.flag_enum.HAS_OPEN_SHARE.value, self.validate_enum.NO.value)

            self.track_mongo.update_entry(guid, self.flag_enum.HAS_NEW_FILE.value, self.validate_enum.NO.value)

            # remove the temp sync timestamp 
            self.track_mongo.delete_field(guid, "temporary_erda_sync_time")
            # remove the temp time out status if it exist                    
            self.track_mongo.delete_field(guid, "temporary_time_out_sync_erda_attempt")

            self.track_mongo.update_entry(guid, "proxy_path", "")

            for file in asset["file_list"]:
                self.track_mongo.update_track_file_list(guid, file["name"], self.flag_enum.ERDA_SYNC.value, self.validate_enum.YES.value) 

            return True

        return False

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            current_time = datetime.now()
            time_difference = current_time - self.auth_timestamp
            
            if time_difference > timedelta(minutes=4):
                self.storage_api.service.metadata_db.close_mdb()
                print(f"creating new storage client, after {time_difference}")
                self.storage_api = self.create_storage_api()
            if self.storage_api is None:
                self.end_of_loop_checks()
                continue
            
            # check throttle
            sync_count = self.throttle_mongo.get_value_for_key("max_sync_asset_count", "value")
            if sync_count >= self.max_sync_asset_count:
                # TODO implement better throttle than sleep
                time.sleep(5)
                self.end_of_loop_checks()
                continue

            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{self.flag_enum.HAS_NEW_FILE.value : self.validate_enum.AWAIT.value, self.flag_enum.ERDA_SYNC.value: self.validate_enum.NO.value}])

            if asset is not None:
                guid = asset["_id"]
                
                if "temporary_time_out_sync_erda_attempt" in asset:
                    asset_time_out_and_synced_anyway = self.test_asset_timeout_and_synced(guid, asset)
                
                    if asset_time_out_and_synced_anyway: 
                        # asset has been synced so no need to continue with it
                        self.end_of_loop_checks()
                        continue
                
                # api call
                synced, status_code, note = self.storage_api.sync_erda(guid)
                
                # success scenario - update track database
                if synced is True:
                    self.success_sync(guid)
                
                # handle api fails
                if synced is False:
                    # handle specific cases
                    # found wrong type of data as status code from exception, likely not the asset that caused the -1 or -2 
                    if status_code == -1:
                        time.sleep(1)
                        
                    # could not find any data as status code from exception # TODO can maybe handle -1 and -2 in one check - create functions for these, can probably be generic for all storage updater classes.
                    elif status_code == -2:
                        time.sleep(1)
                        
                    elif status_code == 400:
                        # if call returns true then asset was synced anyway see integration repo issue 112
                        check = self.handle_status_400(guid, asset, note)
                        if check is True:
                            self.success_sync(guid)
                    
                    elif status_code == 504:
                        check = self.handle_status_504(guid, note)
                        if check is True:
                            self.success_sync(guid)

                    # other fails
                    else:
                        entry = self.run_util.log_msg(self.prefix_id, f"Sync with erda api call with status {status_code} failed for {guid}. {note}", self.status_enum.ERROR.value)
                        self.health_caller.error(self.service_name, entry, guid, self.flag_enum.ERDA_SYNC.value, self.status_enum.ERROR.value)
                        time.sleep(1)

                time.sleep(1)

            if asset is None:
                time.sleep(10)

            # perform end of loop checks for pause and run status
            self.end_of_loop_checks()
        
        # Outside main while loop
        self.track_mongo.close_connection()
        self.service_mongo.close_connection()
        self.throttle_mongo.close_connection()

    # end of loop checks
    def end_of_loop_checks(self):
        # checks if service should keep running           
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.validate_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()

    # success scenario
    def success_sync(self, guid):
        self.track_mongo.update_entry(guid, self.flag_enum.ERDA_SYNC.value, self.validate_enum.AWAIT.value)                    
        # add timestamp for when attempted sync, this will be used to check that an asset dont end up stuck with the ASSET_RECEIVED status by ARS forever.
        self.track_mongo.update_entry(guid, "temporary_erda_sync_time", datetime.now())
        self.throttle_mongo.add_one_to_count("max_sync_asset_count", "value")

    # handles status 400, checks if the asset has actually been synced despite the 400 status. Returns True if asset has synced, false otherwise
    def handle_status_400(self, guid, asset, note):

        response_get_asset_status = self.storage_api.get_full_asset_status(guid)

        status_from_ARS = response_get_asset_status["data"].status
        share_allocation_size = response_get_asset_status["data"].share_allocation_mb

        if share_allocation_size is None and status_from_ARS == self.erda_status_enum.ASSET_RECEIVED.value:
            # TODO handle this - check if open share works?
            pass


        if status_from_ARS is False or status_from_ARS in [self.erda_status_enum.METADATA_RECEIVED.value, self.erda_status_enum.ERDA_ERROR.value]:
            entry = self.run_util.log_msg(self.prefix_id, f"Sync with erda api call with status 400 failed for {guid}. {note}", self.status_enum.ERROR.value)
            self.health_caller.error(self.service_name, entry, guid, self.flag_enum.ERDA_SYNC.value, self.status_enum.ERROR.value)
            return False

        if status_from_ARS in [self.erda_status_enum.ASSET_RECEIVED.value, self.erda_status_enum.COMPLETED.value]:
            entry = self.run_util.log_msg(self.prefix_id, f"Sync with erda api call with status 400 for {guid} still succeeded. Asset has ARS erda status {status_from_ARS}. This is a known issue, see github issue 112 in integration project board. {note}")
            self.health_caller.warning(self.service_name, entry, guid)
            return True

        return False
    

    def handle_status_504(self, guid, note):
        
        try:
            status_from_ars = self.storage_api.get_asset_status(guid)

            # TODO might want to add some kind of pausing if too many timeouts happe
            # logs the timeout failure, does not update the asset flags -> asset will be retried
            if status_from_ars == False:                                
                message = self.run_util.log_msg(self.prefix_id, f"Timeout detected without syncing {guid}. Status: 504. {note}")
                self.health_caller.warning(self.service_name, message, guid)

            if status_from_ars in [self.erda_status_enum.COMPLETED.value, self.erda_status_enum.ASSET_RECEIVED.value]:                
                # log the time out
                message = self.run_util.log_msg(self.prefix_id, f"{guid} sync request was a success despite receiving status 504 from ARS. Asset has {status_from_ars} as status from ARS.")
                self.health_caller.warning(self.service_name, message, guid)
                return True

        except Exception as e:
            message = self.run_util.log_exc(self.prefix_id, f"While handling status 504 from sync asset for {guid} another error occurred. {note}", e, self.run_util.log_enum.ERROR.value)                            
            self.health_caller.error(self.service_name, message, guid, self.flag_enum.ERDA_SYNC.value, self.validate_enum.ERROR.value)
           
        return False


if __name__ == '__main__':
    SyncErda()