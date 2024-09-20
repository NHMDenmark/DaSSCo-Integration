import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
from MongoDB import track_repository, service_repository, throttle_repository
from StorageApi import storage_client
from Enums.status_enum import Status
from Enums.flag_enum import Flag
from Enums.validate_enum import Validate
from Enums.erda_status import ErdaStatus
from HealthUtility import health_caller, run_utility
import utility

"""
Responsible validating files have been synced with erda and updating track data accordingly. 
Does this by finding assets with flags set to erda_sync: WAITING and has_open_share: YES
Then calls the ARS get asset status and checks if the asset has been synced. 
"""

class SyncErda(Status, Flag, ErdaStatus, Validate):

    def __init__(self):

        Status.__init__(self)
        Flag.__init__(self)
        ErdaStatus.__init__(self)
        Validate.__init__(self)

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        # service name for logging/info purposes
        self.service_name = "Validate erda sync ARS"
        self.prefix_id = "VesA"
        self.auth_timestamp = None
        self.service_config_path = f"{project_root}/ConfigFiles/micro_service_config.json"

        self.track_mongo = track_repository.TrackRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.throttle_mongo = throttle_repository.ThrottleRepository()

        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()

        self.max_sync_erda_attempt_wait_time = self.util.get_nested_value(self.service_config_path, self.service_name, "max_sync_erda_attempt_wait_time")

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)

        # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.RUNNING)
        # special status change, logging and contact health api
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.RUNNING}")
        self.health_caller.run_status_change(self.service_name, self.RUNNING, entry)

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
            # log the failure to create the storage api
            entry = self.run_util.log_exc(self.prefix_id, f"Failed to create storage client. {self.service_name} failed to run. Received status: {storage_api.status_code}. {self.service_name} needs to be manually restarted. {storage_api.note}",
                                           storage_api.exc, self.run_util.log_enum.ERROR.value)
            self.health_caller.error(self.service_name, entry)
            # change run value in db
            self.service_mongo.update_entry(self.service_name, "run_status", self.STOPPED)
            
            # log the status change + health call 
            self.run_util.log_status_change(self.service_name, self.run, self.STOPPED)

            # update run values
            self.run = self.run_util.get_service_run_status()
            self.run_util.service_run = self.run           
            
        return storage_api

    def loop(self):

        while self.run == self.RUNNING:

            current_time = datetime.now()
            time_difference = current_time - self.auth_timestamp
            
            # renew authentication with keycloak
            if time_difference > timedelta(minutes=4):
                self.storage_api.service.metadata_db.close_mdb()
                print(f"creating new storage client, after {time_difference}")
                self.storage_api = self.create_storage_api()
            if self.storage_api is None:
                continue

            # checks if service should keep running
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.PAUSED:
                self.run = self.run_util.pause_loop()
            
            if self.run == self.STOPPED:
                continue           
            
            assets = self.track_mongo.get_entries_from_multiple_key_pairs([{self.ERDA_SYNC: self.AWAIT, self.HAS_OPEN_SHARE: self.YES}])

            if len(assets) == 0:
                # no assets found that needed validation
                time.sleep(20)
                continue
            
            print(f"checking {len(assets)} assets:")
            for asset in assets:
                guid = asset["_id"]
                
                # bool(True if status 200, False otherwise), status code from api(set to -1 if the call failed completely), 
                # asset status(COMPLETED, ASSET_RECEIVED, ERDA_ERROR), asset share size(should be none/null for a success), note(any description if one is needed from the api call)
                attempted, status_code, asset_status, asset_share_size, note = self.storage_api.get_asset_sharesize_and_status(guid)
                
                # main area for errors
                if attempted is False:
                    if status_code == 1000:
                        continue
                    # other cases
                    else:
                        # logs and sends a error message to the health api
                        entry = self.run_util.log_msg(self.prefix_id, f"Something unexpected happened while attempting to get the asset status from ARS for {guid}. Status code: {status_code}. Will set erda_sync to ERROR. {note}")
                        self.health_caller.error(self.service_name, entry, guid, self.ERDA_SYNC, self.ERROR)
                        continue

                # success scenario for an asset
                if asset_status == self.COMPLETED and asset_share_size is None:
                    self.asset_validated(guid, asset)

                # check the case of a COMPLETED sync happens without the fileshare being closed, will set a lot of AWAIT status
                # TODO handle what happens if this triggers, for now it just puts the asset in a corner
                if asset_status == self.COMPLETED and asset_share_size is not None:
                    self.completed_sync_share_still_open(self, guid, asset)

                # asset is still waiting to be synced
                if asset_status == self.ASSET_RECEIVED:
                    # check if asset is timed out and handle if true
                    timed_out = self.check_timeout(guid)

                    if timed_out is True:                            
                            self.timeout_handling(guid, asset)
                    else:
                        # no action needed here since asset is queued to be synced and just waiting for that to happen
                        print(f"Waiting on erda sync for asset: {guid}")
                    
                if asset_status == self.ERDA_ERROR:
                    # TODO figure out how to handle this situation further. maybe set a counter that at a certain number triggers a long delay and clears if there are no ERDA_ERRORs
                    # currently resetting sync status to "NO" attempts a new sync 
                    self.track_mongo.update_entry(guid, self.ERDA_SYNC, self.NO)

                # wait time between calling ARS for asset status
                time.sleep(2)

            # total delay after one run
            time.sleep(10)

        # Outside main while loop
        self.track_mongo.close_connection()
        self.service_mongo.close_connection()
        self.throttle_mongo.close_connection()

    # success scenario
    def asset_validated(self, guid, asset):
        
        self.throttle_mongo.subtract_one_from_count("max_sync_asset_count", "value")

        self.track_mongo.update_entry(guid, self.ERDA_SYNC, self.YES)
                    
        self.track_mongo.update_entry(guid, self.HAS_OPEN_SHARE, self.NO)

        self.track_mongo.update_entry(guid, self.HAS_NEW_FILE, self.NO)

        # remove the temp sync timestamp 
        self.track_mongo.delete_field(guid, "temporary_erda_sync_time")
        # remove the temp time out status if it exist                    
        self.track_mongo.delete_field(guid, "temporary_time_out_sync_erda_attempt")

        self.track_mongo.update_entry(guid, "proxy_path", "")

        for file in asset["file_list"]:
            self.track_mongo.update_track_file_list(guid, file["name"], self.ERDA_SYNC, self.YES)        
        
        print(f"Validated erda sync for asset: {guid}")

    def check_timeout(self, guid):

        time_received = self.track_mongo.get_value_for_key(guid, "temporary_erda_sync_time")

        time_allowed = datetime.now() - timedelta(seconds=self.max_sync_erda_attempt_wait_time)

        if time_received < time_allowed:

            return True
        
        return False

    def timeout_handling(self, guid, asset):
            again = self.track_mongo.get_value_for_key(guid, "temporary_time_out_sync_erda_attempt")

            if again is True:
                # logs and sends error msg to health api. Service there will set the erda_sync to ERROR
                info = None
                try:
                    info = self.storage_api.check_file_info_for_asset(guid)
                except Exception as e:
                    entry = self.run_util.log_exc(self.prefix_id, f"{guid} encountered a bug while determining status after multiple erda sync validation timeouts.", e, self.ERROR)
                    self.health_caller.error(self.service_name, entry, guid, self.ERDA_SYNC, self.ERROR) 
                    self.throttle_mongo.subtract_one_from_count("max_sync_asset_count", "value")

                if info is False or info is None:
                    entry = self.run_util.log_msg(self.prefix_id, "The asset has timed out more than once while attempting to sync with ERDA. It likely gets stuck with the ASSET_RECEIVED status set by ARS.", self.ERROR)
                    self.health_caller.error(self.service_name, entry, guid, self.ERDA_SYNC, self.ERROR)
                    self.throttle_mongo.subtract_one_from_count("max_sync_asset_count", "value")
                # asset was synced despite the timeout status - note asset does not have and will not get the asset COMPLETED status in ARS
                if info is True:
                    entry = self.run_util.log_msg(self.prefix_id, f"{guid} got stuck with ASSET_RECEIVED status despite being succesfully synced with erda -
                                                   note asset does not have and will not get the asset COMPLETED status in ARS. This was discovered after multiple validation timeouts.")
                    self.health_caller.warning(self.service_name, entry, guid)
                    self.asset_validated(guid, asset)

            if again is None:
                self.track_mongo.update_entry(guid, self.ERDA_SYNC, self.NO)
                self.track_mongo.update_entry(guid, "temporary_time_out_sync_erda_attempt", True)
                self.throttle_mongo.subtract_one_from_count("max_sync_asset_count", "value")
                # logs and sends a warning message to the health api
                entry = self.run_util.log_msg(self.prefix_id, "The asset timed out while syncing with ERDA for the first time. Asset has had erda_sync flag set to NO and will be rescheduled for syncing.")
                self.health_caller.warning(self.service_name, entry, guid)

    def completed_sync_share_still_open(self, guid, asset):
        self.track_mongo.update_entry(guid, self.ERDA_SYNC, self.AWAIT)
                    
        self.track_mongo.update_entry(guid, self.HAS_OPEN_SHARE, self.AWAIT)

        self.track_mongo.update_entry(guid, self.HAS_NEW_FILE, self.AWAIT)

        # remove the temp sync timestamp 
        self.track_mongo.delete_field(guid, "temporary_erda_sync_time")
        # remove the temp time out status if it exist                    
        self.track_mongo.delete_field(guid, "temporary_time_out_sync_erda_attempt")

        for file in asset["file_list"]:
             self.track_mongo.update_track_file_list(guid, file["name"], self.ERDA_SYNC, self.AWAIT)
        
        # logs and sends a warning message to the health api
        entry = self.run_util.log_msg(self.prefix_id, "The asset was synced but the fileshare was not closed. This is a bug we have encountered before during testing. Erda_sync, has_open_share and has_new_file are all set to AWAIT. Check that asset is in erda")
        self.health_caller.warning(self.service_name, entry, guid)
        # TODO handle how to get back on track

if __name__ == '__main__':
    SyncErda()